import importlib.util
import os

ROOT = os.path.dirname(__file__)
PARSER_PATH = os.path.join(ROOT, '..', 'src', 'infrastructure', 'parser.py')
spec = importlib.util.spec_from_file_location('parser', PARSER_PATH)
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)


def test_article_title_detection():
    elements = [
        'Điều 1.',
        'TIÊU ĐỀ ĐIỀU MỘT',
        '1. Khoản một nội dung',
    ]
    nodes = parser.parse_paragraphs(elements)
    # find article node
    art = next((n for n in nodes if n.get('article_number') == 1), None)
    assert art is not None
    assert art.get('article_title') == 'TIÊU ĐỀ ĐIỀU MỘT'


def test_table_and_part_detection():
    elements = [
        'Phần I',
        'Chương I. Những quy định chung',
        'Điều 2. Title here',
        '1. First clause',
        {'type': 'table', 'rows': [['H1', 'H2'], ['v1', 'v2']]},
        '2. Second clause after table',
    ]
    nodes = parser.parse_paragraphs(elements)
    # table node should be present
    table_nodes = [n for n in nodes if n.get('raw_context', {}).get('table_rows')]
    assert len(table_nodes) == 1
    # check part detection
    any_part = any(n.get('part') and 'Phần' in n.get('part') for n in nodes)
    assert any_part
