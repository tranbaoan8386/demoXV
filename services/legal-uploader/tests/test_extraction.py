import os
import json
import importlib.util

ROOT = os.path.dirname(os.path.dirname(__file__))
STORAGE_PATH = os.path.join(ROOT, 'src', 'infrastructure', 'storage.py')
VALIDATOR_PATH = os.path.join(ROOT, 'src', 'infrastructure', 'validators.py')

spec = importlib.util.spec_from_file_location('storage', STORAGE_PATH)
storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storage)

spec2 = importlib.util.spec_from_file_location('validators', VALIDATOR_PATH)
validators = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(validators)


def test_save_extracted_artifact():
    # create a temporary BASE_UPLOAD_DIR override
    st = storage
    # prepare items
    items = [
        {'type': 'paragraph', 'text': 'First paragraph.'},
        {'type': 'paragraph', 'text': 'Second paragraph.'},
        {'type': 'table', 'index': 0, 'rows': [['A', 'B'], ['C', 'D']]},
    ]
    # use a doc_id
    doc_id = 'test-doc-1'
    path = st.save_extracted_artifact(doc_id, items)
    assert os.path.exists(path)
    with open(path, 'r', encoding='utf-8') as fh:
        lines = [json.loads(l) for l in fh]
    assert len(lines) == 3


def test_validate_extraction_items():
    items = [
        {'type': 'paragraph', 'text': 'Paragraph one.'},
        {'type': 'paragraph', 'text': 'Paragraph two.'},
    ]
    ok, err = validators.validate_extraction_items(items, min_paragraphs=1)
    assert ok
    ok2, err2 = validators.validate_extraction_items([], min_paragraphs=1)
    assert not ok2 and 'no extracted' in err2
