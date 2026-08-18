import os
import sys

# Make src importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from infrastructure import parser


def test_pdf_parser_anchor_extraction(monkeypatch):
    test_lines = [
        'QUỐC HỘI',
        'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM',
        'Luật số: 91/2015/QH13',
        'Hà Nội, ngày 24 tháng 11 năm 2015',
        'BỘ LUẬT',
        'DÂN SỰ',
        'Căn cứ Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam;'
    ]

    monkeypatch.setattr(parser, 'extract_lines_from_pdf', lambda path: list(test_lines))

    metadata = parser.extract_metadata_from_lines(test_lines, fallback_title=None)

    assert metadata.get('title') == 'BỘ LUẬT DÂN SỰ'
    assert metadata.get('reference_number') == '91/2015/QH13'
    assert metadata.get('issued_date') == '2015-11-24'
