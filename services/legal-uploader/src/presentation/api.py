from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, BackgroundTasks, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID
from ..application import upload_service
from ..infrastructure import db, storage
from ..infrastructure.auth.jwt_service import JWTService
from ..infrastructure import parser
from ..infrastructure.doc_converter.libreoffice_converter import LibreOfficeConverter
import os
import tempfile
from io import BytesIO
from docx import Document


ALLOWED_EXT = {'.doc', '.docx', '.pdf'}
ALLOWED_MIME_TYPES = {
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/pdf',
    # Swagger UI / browsers may send generic or alternative MIME types
    'application/octet-stream',
    'application/x-pdf',
}
MAX_SIZE_BYTES = int(os.getenv('MAX_UPLOAD_BYTES', 20 * 1024 * 1024))

app = FastAPI(title='Legal Uploader Service')

security = HTTPBearer()
jwt_service = JWTService()


def allowed_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXT


def is_allowed_mime(ctype: str) -> bool:
    """Return True for known allowed MIME types. Accepts MIME with params
    (e.g. 'application/pdf; charset=binary') and common pdf variants.
    """
    if not ctype:
        return False
    base = ctype.split(';', 1)[0].strip().lower()
    # accept any MIME that explicitly mentions pdf or is in the allowlist
    if base in ALLOWED_MIME_TYPES:
        return True
    if 'pdf' in base:
        return True
    return False


def normalize_uuid(value):
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return str(UUID(value))
        except ValueError:
            return None
    return str(value)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = jwt_service.verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
    return payload


def extract_from_docx_bytes(file_bytes: bytes, fallback_title: str, filename: str = 'document.docx') -> dict:
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.doc':
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = os.path.join(tmpdir, filename)
            with open(temp_path, 'wb') as fh:
                fh.write(file_bytes)
            converted = LibreOfficeConverter().convert_to_docx(temp_path)
            with open(converted, 'rb') as fh:
                file_bytes = fh.read()
    doc = Document(BytesIO(file_bytes))
    lines = [p.text for p in doc.paragraphs[:10]]
    return parser.extract_document_metadata(lines, fallback_title=fallback_title)


@app.post('/api/laws/upload')
async def upload_law(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
    force: bool = Query(False),
):
    if not file:
        raise HTTPException(status_code=400, detail='file is required')
    filename = file.filename or ''
    ctype = getattr(file, 'content_type', None)

    if not allowed_file(filename):
        if ctype and is_allowed_mime(ctype):
            pass
        else:
            raise HTTPException(status_code=415, detail='unsupported media type')

    contents = await file.read()
    size = len(contents)
    if size > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail='payload too large')

    # MIME basic check
    if ctype and not is_allowed_mime(ctype) and not allowed_file(filename):
        raise HTTPException(status_code=415, detail='unsupported media type')

    # compute SHA256 content hash
    import hashlib
    content_hash = hashlib.sha256(contents).hexdigest()

    fallback_title = os.path.splitext(filename)[0]
    # Extract metadata depending on file type: PDF vs DOC/DOCX
    try:
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.pdf' or (not ext and (ctype and 'pdf' in (ctype or '').lower() )):
            # write to a temp file and let parser handle PDF extraction
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=True) as tf:
                tf.write(contents)
                tf.flush()
                try:
                    lines = parser.extract_lines_from_pdf(tf.name)
                except Exception as e:
                    # bubble up as a client error if pdf reading failed
                    raise RuntimeError(f'failed to extract PDF lines: {e}') from e
            metadata = parser.extract_document_metadata(lines, fallback_title=fallback_title)
        else:
            # doc/docx flow
            metadata = extract_from_docx_bytes(contents, fallback_title=fallback_title, filename=filename)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'internal error during metadata extraction: {e}')
    title = metadata.get('title') or fallback_title
    reference_number = metadata.get('reference_number')
    issued_date = metadata.get('issued_date')
    uploader_id = normalize_uuid(user.get('sub')) if isinstance(user, dict) else None

    fileobj = BytesIO(contents)
    try:
        # Detect duplicate
        existing = db.find_document_by_hash(content_hash)
        if existing and not force:
            return {'id': str(existing['id']), 'status': existing.get('status'), 'message': 'DUPLICATE', 'content_hash': content_hash}

        # Persist the uploaded file and initial record
        doc_id = upload_service.handle_upload(fileobj, filename, title, reference_number, issued_date, uploader_id, content_hash=content_hash)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Always schedule full parsing of the stored document (clause extraction) asynchronously
    try:
        if background_tasks is not None:
            background_tasks.add_task(upload_service.run_parsing_by_id, doc_id)
        else:
            # synchronous fallback (best-effort)
            try:
                upload_service.run_parsing_by_id(doc_id)
            except Exception:
                pass
    except Exception:
        # scheduling failure should not block upload response
        pass

    # Fast-path validation: if the rule-based metadata is sufficient, mark SUCCESS;
    # otherwise schedule background AI enhancement and return immediately.
    def validate_metadata(m: dict) -> bool:
        import re
        is_valid = True
        if not m or not isinstance(m, dict):
            return False
        title = (m.get('title') or '').strip()
        reference_number = (m.get('reference_number') or '').strip()

        # title must exist and be reasonably long
        if not title or len(title) < 5:
            return False

        # reject titles that look like header/boilerplate containing these keywords
        bad_keywords = [
            'cộng hòa',
            'xã hội chủ nghĩa',
            'độc lập',
            'tự do',
            'công báo',
            'quốc hội',
        ]
        low_title = title.lower()
        for kw in bad_keywords:
            if kw in low_title:
                return False

        # reference number must exist
        if not reference_number:
            return False

        # if reference contains a date-like token (DD-MM-YYYY or DD/MM/YYYY) -> invalid
        if re.search(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b", reference_number):
            return False

        # if reference_number does not contain any slash '/' -> invalid
        if '/' not in reference_number:
            return False

        return is_valid

    # ensure we have `lines` for saving extracted artifact
    lines_for_artifact = []
    try:
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.pdf' or (not ext and (ctype and 'pdf' in (ctype or '').lower())):
            # already extracted `lines` above when computing metadata for PDFs
            # but ensure variable exists (it was defined earlier for PDF path)
            # if not, re-extract from stored file
            if 'lines' not in locals() or not lines:
                # get storage path from db
                rec = db.get_document(doc_id)
                if rec:
                    stored = rec.get('storage_path')
                    try:
                        lines = parser.extract_lines_from_pdf(stored)
                    except Exception:
                        lines = []
            lines_for_artifact = [{'type': 'line', 'text': l} for l in (lines or [])]
        else:
            # extract paragraphs from DOCX to produce artifact lines
            try:
                from docx import Document as DocxDocument
                doc = DocxDocument(BytesIO(contents))
                doc_lines = [p.text for p in doc.paragraphs if p and p.text]
                lines_for_artifact = [{'type': 'line', 'text': l} for l in doc_lines]
            except Exception:
                lines_for_artifact = []
    except Exception:
        lines_for_artifact = []

    # Update metadata fields in DB (best-effort)
    try:
        db.update_document_metadata(doc_id, title=title, reference_number=reference_number, issued_date=issued_date)
    except Exception:
        pass

    if validate_metadata(metadata):
        # Fast path success: save extracted artifact and mark done
        try:
            extracted_path = None
            if lines_for_artifact:
                extracted_path = storage.save_extracted_artifact(doc_id, lines_for_artifact)
            db.update_extraction_metadata(doc_id, extracted_path=extracted_path, extraction_status='SUCCESS')
            db.update_status(doc_id, 'PROCESSED')
        except Exception as e:
            # if update fails, surface as server error
            raise HTTPException(status_code=500, detail=f'failed to persist extraction metadata: {e}')
        return {'id': doc_id, 'status': 'PROCESSED', 'message': 'Uploaded and metadata extracted.'}
    else:
        # Slow path: persist as pending AI enhancement and schedule background task
        try:
            db.update_extraction_metadata(doc_id, extracted_path=None, extraction_status='PENDING_AI_ENHANCEMENT')
            db.update_status(doc_id, 'PROCESSED')
        except Exception:
            pass

        if background_tasks is not None:
            background_tasks.add_task(upload_service.enhance_metadata_with_gemini, doc_id)
        else:
            # best-effort synchronous fallback (not ideal in production)
            try:
                upload_service.enhance_metadata_with_gemini(doc_id)
            except Exception:
                pass

        return {'id': doc_id, 'status': 'PROCESSED', 'message': 'Uploaded. Metadata enhancement scheduled.'}


@app.patch('/api/laws/{document_id}/approve')
def approve_law(document_id: str, user=Depends(get_current_user)):
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail='not found')
    status_val = doc['status']
    if status_val not in ('DONE', 'PROCESSED'):
        raise HTTPException(status_code=400, detail=f'document must be in PROCESSED state to approve (current={status_val})')
    approver = normalize_uuid(user.get('sub')) if isinstance(user, dict) else None
    try:
        db.update_status(document_id, 'APPROVED', error_message=None, approved_by=approver)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {'id': document_id, 'status': 'APPROVED'}

