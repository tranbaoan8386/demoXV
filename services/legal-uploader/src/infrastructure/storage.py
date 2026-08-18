import io
import json
import os
import shutil

from minio import Minio

# Read upload directory from environment; require configuration via env
UPLOAD_DIR = os.getenv('UPLOAD_DIR')
if not UPLOAD_DIR:
    BASE_UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'uploads', 'legal-uploader'))
else:
    BASE_UPLOAD_DIR = os.path.abspath(UPLOAD_DIR)


def ensure_storage_layout():
    os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)
    for subdir in ['incoming', 'converted', 'extracted', 'tmp', 'failed']:
        os.makedirs(os.path.join(BASE_UPLOAD_DIR, subdir), exist_ok=True)


ensure_storage_layout()


def get_storage_subdir(subdir: str) -> str:
    ensure_storage_layout()
    return os.path.join(BASE_UPLOAD_DIR, subdir)


def _get_minio_client():
    endpoint = os.getenv('MINIO_ENDPOINT', 'demoxv-minio:9000')
    access_key = os.getenv('MINIO_ROOT_USER', 'minio_admin')
    secret_key = os.getenv('MINIO_ROOT_PASSWORD', 'minio_secret_pass')
    secure = os.getenv('MINIO_USE_SSL', 'false').lower() == 'true'
    return Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)


def ensure_bucket():
    bucket_name = os.getenv('MINIO_BUCKET', 'legal-documents')
    client = _get_minio_client()
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
    return bucket_name


def save_file(fileobj, doc_id, original_filename):
    """Save uploaded file into configured upload directory and return absolute path."""
    ensure_storage_layout()
    ext = os.path.splitext(original_filename)[1]
    fname = f"{doc_id}{ext}"
    path = os.path.join(get_storage_subdir('incoming'), fname)
    fileobj.seek(0)
    payload = fileobj.read()
    with open(path, 'wb') as fh:
        fh.write(payload)

    try:
        bucket_name = ensure_bucket()
        client = _get_minio_client()
        client.put_object(bucket_name, fname, io.BytesIO(payload), length=len(payload), content_type='application/octet-stream')
    except Exception:
        # Best-effort upload; local filesystem remains canonical for the current service.
        pass

    return path


def move_to_failed(path: str):
    if not path or not os.path.exists(path):
        return None
    ensure_storage_layout()
    failed_dir = get_storage_subdir('failed')
    filename = os.path.basename(path)
    dest = os.path.join(failed_dir, filename)
    index = 1
    while os.path.exists(dest):
        root, ext = os.path.splitext(filename)
        dest = os.path.join(failed_dir, f"{root}_{index}{ext}")
        index += 1
    shutil.move(path, dest)
    return dest


def cleanup_temp_file(path: str):
    if not path or not os.path.exists(path):
        return False
    try:
        os.remove(path)
        return True
    except Exception:
        return False


def cleanup_temp_files(paths):
    for path in paths or []:
        cleanup_temp_file(path)


def save_extracted_artifact(doc_id: str, items: list):
    """Save extracted paragraphs and tables as JSONL artifact and return path."""
    ensure_storage_layout()
    extracted_dir = get_storage_subdir('extracted')
    fname = f"{doc_id}.jsonl"
    path = os.path.join(extracted_dir, fname)
    with open(path, 'w', encoding='utf-8') as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + '\n')
    return path
