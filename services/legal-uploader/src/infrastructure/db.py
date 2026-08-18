import os
from contextlib import contextmanager
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv, find_dotenv


def load_env():
    # auto-find .env in repo root or ancestor directories
    env_path = find_dotenv(usecwd=True)
    if env_path:
        load_dotenv(env_path)


def ensure_database_exists():
    load_env()
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        return

    # parse database name from DATABASE_URL and ensure it exists on the postgres server
    try:
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        db_name = parsed.path.lstrip('/')
        if not db_name:
            return

        admin_url = db_url.rsplit('/', 1)[0] + '/postgres'
        conn = psycopg2.connect(admin_url)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if cur.fetchone() is None:
                cur.execute(f'CREATE DATABASE "{db_name}"')
        conn.close()
    except Exception:
        # Ignore initialization errors when the target DB already exists or the server is not reachable yet.
        pass


def build_database_url():
    load_env()
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    db = os.getenv('POSTGRES_DOC_DB')
    if not (user and password and db):
        raise RuntimeError('Missing POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DOC_DB in environment')
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


@contextmanager
def get_conn():
    load_env()
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        db_url = build_database_url()
    ensure_database_exists()
    conn = psycopg2.connect(db_url)
    try:
        yield conn
    finally:
        conn.close()


def insert_document(record):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO public.legal_documents (id, title, reference_number, issued_date, original_filename, storage_path, uploader_id, status, content_hash, extracted_path, extraction_status, extraction_error)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    record['id'],
                    record.get('title'),
                    record.get('reference_number'),
                    record.get('issued_date'),
                    record.get('original_filename'),
                    record.get('storage_path'),
                    record.get('uploader_id'),
                    record.get('status', 'PENDING'),
                    record.get('content_hash'),
                    record.get('extracted_path'),
                    record.get('extraction_status'),
                    record.get('extraction_error'),
                ),
            )
            conn.commit()


def update_status(document_id, status, error_message=None, approved_by=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE public.legal_documents SET status = %s, error_message = %s, approved_by = %s, updated_at = now()
                WHERE id = %s
                """,
                (status, error_message, approved_by, document_id),
            )
            conn.commit()


def update_document_metadata(document_id, title=None, reference_number=None, issued_date=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE public.legal_documents
                SET title = COALESCE(%s, title),
                    reference_number = COALESCE(%s, reference_number),
                    issued_date = COALESCE(%s, issued_date),
                    updated_at = now()
                WHERE id = %s
                """,
                (title, reference_number, issued_date, document_id),
            )
            conn.commit()


def get_document(document_id):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM public.legal_documents WHERE id = %s", (document_id,))
            return cur.fetchone()


def find_document_by_hash(content_hash: str):
    if not content_hash:
        return None
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM public.legal_documents WHERE content_hash = %s", (content_hash,))
            return cur.fetchone()


def update_extraction_metadata(document_id, content_hash=None, extracted_path=None, extraction_status=None, extraction_error=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE public.legal_documents
                SET content_hash = COALESCE(%s, content_hash),
                    extracted_path = COALESCE(%s, extracted_path),
                    extraction_status = COALESCE(%s, extraction_status),
                    extraction_error = COALESCE(%s, extraction_error),
                    updated_at = now()
                WHERE id = %s
                """,
                (content_hash, extracted_path, extraction_status, extraction_error, document_id),
            )
            conn.commit()


def insert_clauses(document_id, clauses):
    with get_conn() as conn:
        with conn.cursor() as cur:
            for c in clauses:
                cur.execute(
                    """
                    INSERT INTO public.legal_clauses (
                      id, document_id, part, section, subsection, chapter, chapter_index,
                      article_id, article_number, article_title, clause_number, parent_clause_id,
                      point_label, content, order_index, start_paragraph_index, end_paragraph_index,
                      raw_context, is_needs_review, review_reason
                    )
                    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        document_id,
                        c.get('part'),
                        c.get('section'),
                        c.get('subsection'),
                        c.get('chapter'),
                        c.get('chapter_index'),
                        c.get('article_id'),
                        c.get('article_number'),
                        c.get('article_title'),
                        c.get('clause_number'),
                        c.get('parent_clause_id'),
                        c.get('point_label'),
                        c.get('content'),
                        c.get('order_index'),
                        c.get('start_paragraph_index'),
                        c.get('end_paragraph_index'),
                        psycopg2.extras.Json(c.get('raw_context') if c.get('raw_context') is not None else {}),
                        c.get('is_needs_review', False),
                        c.get('review_reason'),
                    ),
                )
            conn.commit()
