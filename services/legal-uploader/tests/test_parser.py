import os
import importlib.util
import pytest

# Load parser module directly from file to avoid package name issues
ROOT = os.path.dirname(os.path.dirname(__file__))
PARSER_PATH = os.path.join(ROOT, 'src', 'infrastructure', 'parser.py')
spec = importlib.util.spec_from_file_location('parser', PARSER_PATH)
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)


def test_article_clause_point_parsing():
    paras = [
        'Chương I. Những quy định chung',
        'Điều 1. Phạm vi điều chỉnh.',
        '1. Người lao động có quyền...',
        '2. Người sử dụng lao động có trách nhiệm...',
        'a) Tiêu chí A',
        'b) Tiêu chí B',
    ]
    nodes = parser.parse_paragraphs(paras)
    assert any(n.get('article_number') == 1 for n in nodes)
    assert any(n.get('clause_number') == 1 for n in nodes)
    assert any(n.get('point_label') == 'a' for n in nodes)


def test_orphan_clause():
    paras = [
        '1. Mở đầu không thuộc điều',
        '2. Tiếp tục'
    ]
    nodes = parser.parse_paragraphs(paras)
    assert any(n.get('clause_number') == 1 for n in nodes)


def test_extract_metadata_from_first_lines():
    lines = [
        'NGHỊ ĐỊNH SỐ 123/2024/NĐ-CP',
        'VỀ QUẢN LÝ HÀNH NGHỀ TỰ DO',
        'Số: 123/2024/NĐ-CP',
        'ngày 15 tháng 12 năm 2024',
        'BAN HÀNH',
    ]
    metadata = parser.extract_document_metadata(lines, fallback_title='fallback-doc')
    assert metadata['reference_number'] == '123/2024/NĐ-CP'
    assert metadata['issued_date'] == '2024-12-15'
    assert 'NGHỊ ĐỊNH' in metadata['title']


def test_extract_metadata_fallback_title():
    metadata = parser.extract_document_metadata(['Không có tiêu đề hợp lệ'], fallback_title='van-ban-ky-1')
    assert metadata['title'] == 'van-ban-ky-1'
    assert metadata['reference_number'] is None
    assert metadata['issued_date'] is None
