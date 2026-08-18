import importlib.util
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(__file__))
STORAGE_PATH = os.path.join(ROOT, 'src', 'infrastructure', 'storage.py')
spec = importlib.util.spec_from_file_location('storage_phase6', STORAGE_PATH)
storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storage)


def test_storage_layout_is_created():
    base = storage.BASE_UPLOAD_DIR
    for subdir in ['incoming', 'converted', 'extracted', 'tmp', 'failed']:
        assert os.path.isdir(os.path.join(base, subdir))


def test_temp_cleanup_removes_file():
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        temp_path = fp.name
    assert os.path.exists(temp_path)
    assert storage.cleanup_temp_file(temp_path) is True
    assert not os.path.exists(temp_path)


def test_move_to_failed_moves_file_out_of_incoming():
    incoming_dir = storage.get_storage_subdir('incoming')
    failed_dir = storage.get_storage_subdir('failed')
    filename = 'phase6_failure_test.txt'
    src = os.path.join(incoming_dir, filename)
    with open(src, 'w', encoding='utf-8') as fh:
        fh.write('simulated failure payload')
    moved = storage.move_to_failed(src)
    assert moved is not None
    assert os.path.exists(moved)
    assert moved.startswith(failed_dir)
    assert not os.path.exists(src)
    if os.path.exists(moved):
        os.remove(moved)


def test_save_file_uses_incoming_dir():
    doc_id = 'phase6-doc-id'
    path = storage.save_file(__import__('io').BytesIO(b'hello world'), doc_id, 'sample.txt')
    assert os.path.exists(path)
    assert os.path.dirname(path) == storage.get_storage_subdir('incoming')
    os.remove(path)
