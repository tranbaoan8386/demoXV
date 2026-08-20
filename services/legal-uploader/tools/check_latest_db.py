#!/usr/bin/env python3
import os
import sys
from pprint import pprint

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Prefer explicit localhost DB to reach host-postgres mapped port
os.environ.setdefault('DATABASE_URL', 'postgresql://demoxv_admin:demoxv_secret_pass@localhost:5432/legal_db')

from src.infrastructure import db


def main():
    doc = None
    # fetch latest document by created_at if available, else by id
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("SELECT id, title, reference_number, issued_date, created_at FROM public.legal_documents ORDER BY created_at DESC NULLS LAST LIMIT 1")
                row = cur.fetchone()
                if row:
                    doc = {
                        'id': str(row[0]),
                        'title': row[1],
                        'reference_number': row[2],
                        'issued_date': row[3],
                        'created_at': row[4],
                    }
            except Exception:
                # fallback: pick any document
                cur.execute("SELECT id, title, reference_number, issued_date FROM public.legal_documents ORDER BY id DESC LIMIT 1")
                row = cur.fetchone()
                if row:
                    doc = {'id': str(row[0]), 'title': row[1], 'reference_number': row[2], 'issued_date': row[3]}

    if not doc:
        print('No documents found in public.legal_documents')
        sys.exit(2)

    print('\nFound document:')
    pprint(doc)

    # fetch clauses
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, article_number, clause_number, content, order_index, start_paragraph_index, end_paragraph_index FROM public.legal_clauses WHERE document_id = %s ORDER BY order_index ASC", (doc['id'],))
            rows = cur.fetchall()

    if not rows:
        print('No clauses found for document', doc['id'])
        sys.exit(3)

    clauses = []
    for r in rows:
        clauses.append({
            'id': str(r[0]),
            'article_number': r[1],
            'clause_number': r[2],
            'content': (r[3] or '')[:200],
            'order_index': r[4],
            'start_paragraph_index': r[5],
            'end_paragraph_index': r[6],
        })

    total = len(clauses)
    print(f"\nTotal clauses: {total}")

    # check continuity of order_index
    order_indexes = [c['order_index'] for c in clauses]
    contiguous = True
    for i in range(1, len(order_indexes)):
        if order_indexes[i] != order_indexes[i-1] + 1:
            contiguous = False
            break

    print('Order_index contiguous:', contiguous)

    # print 3 clauses around midpoint to approximate part1/part2 boundary
    mid = total // 2
    a_start = max(0, mid - 3)
    a_end = mid
    b_start = mid
    b_end = min(total, mid + 3)

    print('\nLast 3 clauses of part1 (approx):')
    for c in clauses[a_start:a_end]:
        print(f"- idx={c['order_index']} article={c['article_number']} clause={c['clause_number']} start_p={c['start_paragraph_index']} content='{c['content']}'")

    print('\nFirst 3 clauses of part2 (approx):')
    for c in clauses[b_start:b_end]:
        print(f"- idx={c['order_index']} article={c['article_number']} clause={c['clause_number']} start_p={c['start_paragraph_index']} content='{c['content']}'")

    # simple metadata checks
    title_ok = bool(doc.get('title') and len(str(doc.get('title')).strip()) > 5)
    print('\nMetadata title present and plausible:', title_ok)

    if not contiguous:
        print('\nWARNING: order_index has gaps — clause continuity may be broken')


if __name__ == '__main__':
    main()
