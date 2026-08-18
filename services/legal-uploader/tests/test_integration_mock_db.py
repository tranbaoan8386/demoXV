import os
import tempfile
import uuid
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from application import upload_service
from infrastructure import parser


def _make_pdf(path):
    try:
        from reportlab.pdfgen import canvas
    except Exception:
        raise RuntimeError('reportlab required for this test')
    c = canvas.Canvas(path)
    y = 800
    lines = [
        'QUỐC HỘI',
        'Luật số: 91/2015/QH13',
        'Hà Nội, ngày 24 tháng 11 năm 2015',
        '',
        'BỘ LUẬT',
        'DÂN SỰ',
        '',
        'Căn cứ Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam;'
    ]
    for ln in lines:
        c.drawString(50, y, ln)
        y -= 18
    c.showPage()
    c.save()


def test_run_parsing_updates_status(tmp_path, monkeypatch):
    # Prepare PDF
    pdf_path = str(tmp_path / 'doc.pdf')
    _make_pdf(pdf_path)

    doc_id = str(uuid.uuid4())
    document_record = {
        'id': doc_id,
        'storage_path': pdf_path,
        'original_filename': 'doc.pdf',
        'content_hash': None,
    }

    calls = {'update_extraction_metadata': [], 'update_document_metadata': [], 'insert_clauses': [], 'update_status': []}

    def fake_update_extraction_metadata(document_id, **kwargs):
        calls['update_extraction_metadata'].append((document_id, kwargs))

    def fake_update_document_metadata(document_id, **kwargs):
        calls['update_document_metadata'].append((document_id, kwargs))

    def fake_insert_clauses(document_id, clauses):
        calls['insert_clauses'].append((document_id, clauses))

    def fake_update_status(document_id, status, error_message=None, approved_by=None):
        calls['update_status'].append((document_id, status, error_message, approved_by))

    # Patch db functions on the upload_service module
    monkeypatch.setattr(upload_service, 'db', upload_service.db)
    monkeypatch.setattr(upload_service.db, 'update_extraction_metadata', fake_update_extraction_metadata)
    monkeypatch.setattr(upload_service.db, 'update_document_metadata', fake_update_document_metadata)
    monkeypatch.setattr(upload_service.db, 'insert_clauses', fake_insert_clauses)
    monkeypatch.setattr(upload_service.db, 'update_status', fake_update_status)

    # Patch storage.save_extracted_artifact to return a path
    def fake_save_extracted_artifact(document_id, items):
        return f'extracted://{document_id}.json'

    monkeypatch.setattr(upload_service, 'storage', upload_service.storage)
    monkeypatch.setattr(upload_service.storage, 'save_extracted_artifact', fake_save_extracted_artifact)

    # Run parser on the document_record
    upload_service.run_parsing_for_document(document_record)

    # Verify that extraction metadata was updated and extraction status marked SUCCESS
    assert calls['update_extraction_metadata'], 'update_extraction_metadata not called'
    # find a call that included extraction_status
    assert any('extraction_status' in kwargs for _, kwargs in calls['update_extraction_metadata']), 'no extraction_status update recorded'
    statuses = [kwargs.get('extraction_status') for _, kwargs in calls['update_extraction_metadata'] if 'extraction_status' in kwargs]
    assert any(s in ('SUCCESS', 'NEEDS_REVIEW') for s in statuses), f'expected SUCCESS or NEEDS_REVIEW in {statuses}'
