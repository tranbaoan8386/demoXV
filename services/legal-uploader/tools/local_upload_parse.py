#!/usr/bin/env python3
import os
import sys
import io
import logging

# Ensure src is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('local_upload_parse')

try:
    from application import upload_service
    from infrastructure import storage, db
except Exception as e:
    logger.exception('Failed to import application/infrastructure modules: %s', e)
    raise


def find_sample_pdf():
    incoming = storage.get_storage_subdir('incoming')
    for root, dirs, files in os.walk(incoming):
        for f in files:
            if f.lower().endswith('.pdf'):
                return os.path.join(root, f)
    return None


def main():
    import argparse
    parser_arg = argparse.ArgumentParser()
    parser_arg.add_argument('--file', '-f', help='Path to local PDF file to upload (optional)')
    args = parser_arg.parse_args()
    sample = None
    if args.file:
        if os.path.exists(args.file):
            sample = args.file
        else:
            print('Provided file does not exist:', args.file)
            return 1
    else:
        sample = find_sample_pdf()
    if not sample:
        print('No PDF found in incoming dir:', storage.get_storage_subdir('incoming'))
        print('You can pass a file with --file /path/to/doc.pdf')
        return 1
    print('Using sample PDF:', sample)
    with open(sample, 'rb') as fh:
        data = fh.read()
    # upload (store) the file via handle_upload
    doc_id = upload_service.handle_upload(io.BytesIO(data), os.path.basename(sample), title=None, reference_number=None, issued_date=None, uploader_id=None, content_hash=None)
    print('Uploaded doc_id:', doc_id)
    # run parsing synchronously
    try:
        upload_service.run_parsing_by_id(doc_id)
    except Exception as exc:
        logger.exception('Parsing failed: %s', exc)
        return 2

    # query DB for clause count
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT count(*) FROM public.legal_clauses WHERE document_id = %s', (doc_id,))
                cnt = cur.fetchone()[0]
        print('Inserted clauses count for', doc_id, ':', cnt)
    except Exception as exc:
        logger.exception('DB query failed: %s', exc)
        return 3

    return 0


if __name__ == '__main__':
    sys.exit(main())
