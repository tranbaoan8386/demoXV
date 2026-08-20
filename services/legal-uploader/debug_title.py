import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from infrastructure.parser import extract_zone_1, extract_header_with_ai

header_text = """QUỐC HỘI
Luật số: 36/2005/QH11
CỘNG HOÀ XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
QUỐC HỘI
NƯỚC CỘNG HOÀ XÃ HỘI CHỦ NGHĨA VIỆT NAM
Khoá XI, kỳ họp thứ 7
(Từ ngày 05 tháng 5 đến ngày 14 tháng 6 năm 2005)
LUẬT
THƯƠNG MẠI
Căn cứ vào Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam năm
1992 đã được sửa đổi, bổ sung theo Nghị quyết số 51/2001/QH10 ngày 25 tháng
12 năm 2001 của Quốc hội khoá X, kỳ họp thứ 10;
Luật này quy định về hoạt động thương mại.
Chương I
NHỮNG QUY ĐỊNH CHUNG"""

lines = [line.strip() for line in header_text.splitlines() if line.strip()]
zone_1 = extract_zone_1(lines)
print('=== Zone 1 ===')
print(zone_1)
print('\n=== AI result ===')
print(extract_header_with_ai(zone_1))
