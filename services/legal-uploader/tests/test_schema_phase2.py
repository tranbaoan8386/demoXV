import os
import importlib.util


def test_migration_contains_columns_and_indexes():
    root = os.path.dirname(__file__)
    mig_path = os.path.join(root, '..', 'migrations', '20260818_add_structure_columns.sql')
    assert os.path.exists(mig_path), 'migration file missing'
    txt = open(mig_path, 'r', encoding='utf-8').read()
    assert 'ADD COLUMN IF NOT EXISTS part' in txt
    assert 'is_needs_review' in txt
    assert 'idx_legal_clauses_doc_article' in txt
    assert 'idx_legal_clauses_doc_order' in txt


def test_entities_have_new_fields():
    root = os.path.dirname(__file__)
    entities_path = os.path.join(root, '..', 'src', 'domain', 'entities.py')
    spec = importlib.util.spec_from_file_location('entities', entities_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cls = mod.LegalClause
    inst = cls(document_id='d', section=None, chapter=None, chapter_index=None, article_number=None, clause_number=None, point_label=None, content='c', order_index=1)
    # check attributes
    assert hasattr(inst, 'part')
    assert hasattr(inst, 'subsection')
    assert hasattr(inst, 'article_title')
    assert hasattr(inst, 'start_paragraph_index')
    assert hasattr(inst, 'is_needs_review')


def test_db_insert_clauses_has_new_columns():
    root = os.path.dirname(__file__)
    db_path = os.path.join(root, '..', 'src', 'infrastructure', 'db.py')
    txt = open(db_path, 'r', encoding='utf-8').read()
    assert 'article_title' in txt
    assert 'start_paragraph_index' in txt
    assert 'is_needs_review' in txt
