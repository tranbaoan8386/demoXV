import json
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


def _load_service_env_if_needed() -> None:
    """Safely load GEMINI config from local env files without crashing inside Docker."""
    key_present = bool(
        os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_GENAI_API_KEY')
    )
    if key_present:
        return

    try:
        base_dir = Path(__file__).resolve().parent
        candidates = [
            base_dir.parent.parent / '.env',
            base_dir.parent.parent / 'ai-audit-service' / '.env',
            base_dir.parent / '.env',
        ]
        for candidate in candidates:
            try:
                if not candidate.exists():
                    continue
                with candidate.open('r', encoding='utf-8') as fh:
                    for line in fh:
                        line = line.strip()
                        if not line or line.startswith('#') or '=' not in line:
                            continue
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and key not in os.environ and value:
                            os.environ[key] = value
                if os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_GENAI_API_KEY'):
                    return
            except (FileNotFoundError, OSError, IndexError, TypeError, ValueError):
                continue
    except Exception as exc:
        logger.error('Failed to load Gemini env from project files: %s', exc)


_load_service_env_if_needed()

# Regex helpers
RE_DATE = re.compile(r'(?:ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})|(\d{1,2})[\/-](\d{1,2})[\/-](\d{4}))', re.IGNORECASE)
RE_REF_NUMBER = re.compile(r'(\d{2,4}/\d{4}/[A-Z0-9Đ\-]+)')
HEADER_STOP_WORDS = [
    'cộng hòa xã hội chủ nghĩa việt nam',
    'độc lập - tự do - hạnh phúc',
    'quốc hội',
    'khóa',
    'kỳ họp thứ',
    'khoá',
    'ky hop thu',
]


def normalize_text(s: str) -> str:
    if s is None:
        return ''
    text = unicodedata.normalize('NFC', str(s))
    return re.sub(r'\s+', ' ', text).strip()


def _clean_line(s: str) -> str:
    if s is None:
        return ''
    s = s.replace('\xa0', ' ').replace('\t', ' ')
    s = s.replace('\r', '')
    return re.sub(r'\s+', ' ', s).strip()


def extract_lines_from_pdf(path: str) -> List[str]:
    """Extract clean lines from the first page of a PDF using pdfplumber."""
    try:
        import pdfplumber
    except Exception as exc:
        logger.error('pdfplumber not installed: %s', exc)
        raise RuntimeError('pdfplumber is required for PDF processing') from exc

    try:
        with pdfplumber.open(path) as pdf:
            if not pdf.pages:
                return []
            page = pdf.pages[0]
            txt = page.extract_text() or ''
    except Exception as exc:
        logger.exception('Failed to read PDF %s', path)
        raise

    lines = [_clean_line(l) for l in txt.splitlines()]
    return [l for l in lines if l]


def extract_all_lines_from_pdf(path: str) -> List[str]:
    """Extract clean lines from ALL pages of a PDF using pdfplumber.

    Returns concatenated list of cleaned lines from every page in document order.
    """
    try:
        import pdfplumber
    except Exception as exc:
        logger.error('pdfplumber not installed: %s', exc)
        raise RuntimeError('pdfplumber is required for PDF processing') from exc

    try:
        lines: List[str] = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                txt = page.extract_text() or ''
                page_lines = [_clean_line(l) for l in txt.splitlines()]
                lines.extend([l for l in page_lines if l])
        return lines
    except Exception as exc:
        logger.exception('Failed to read PDF %s', path)
        raise


def extract_metadata_from_lines(lines: List[str], fallback_title: Optional[str] = None) -> Dict[str, Optional[str]]:
    """Layout-aware extraction per spec:

    1) Preprocess: normalize and remove short garbage lines
    2) Find reference_number using pattern (e.g., 12/2023/QD-XYZ)
    3) Find title by aggregating consecutive uppercase or Title Case lines
    4) Find issued_date using common Vietnamese date forms
    """
    title = None
    reference_number = None
    issued_date = None

    if not lines:
        return {'title': fallback_title, 'reference_number': None, 'issued_date': None}

    # Preprocess: normalize and drop very short lines
    cleaned = [normalize_text(l) for l in lines if l and len(l.strip()) >= 2]

    # 1. Reference number search (prefer top 20 lines)
    for l in cleaned[:20]:
        m = RE_REF_NUMBER.search(l)
        if m:
            reference_number = m.group(1)
            break

    # Also try a generic fallback for common patterns
    if not reference_number:
        gen = re.compile(r'([\d]{1,4}[\/-][\d]{1,4}[\/-][A-Za-z0-9\-_/\.]+)')
        for l in cleaned[:30]:
            gm = gen.search(l)
            if gm:
                reference_number = gm.group(1)
                break

    # 2. Title extraction: bottom-up scan from the first 'Căn cứ' anchor
    title = None
    anchor_idx = None
    for idx, l in enumerate(cleaned):
        ll = l.lower()
        if 'căn cứ' in ll or 'can cu' in ll:
            anchor_idx = idx
            break

    title_lines: List[str] = []
    if anchor_idx is not None and anchor_idx > 0:
        # scan upwards from the line above the anchor
        for k in range(anchor_idx - 1, -1, -1):
            ln = cleaned[k].strip()
            if not ln:
                continue
            # skip lines that look like a reference or contain digits, but continue scanning above
            if RE_REF_NUMBER.search(ln) or re.search(r'\d', ln):
                continue
            # if line is fully uppercase and not trivial, collect it
            if ln.isupper() and len(ln) > 3:
                # insert at front so the list represents top-to-bottom order
                title_lines.insert(0, ln)
                continue
            # encountered a non-uppercase line -> stop collecting
            break

        if title_lines:
            # title_lines was built in top-to-bottom order by inserting at front
            title_list = title_lines
            # dedupe fragments that are substrings of larger fragments
            filtered = []
            for l in title_list:
                if any((l != other) and (l in other) for other in title_list):
                    continue
                filtered.append(l)
            title = ' '.join(filtered) if filtered else ' '.join(title_list)

    # fallback to previous heuristics if bottom-up didn't find a title
    if not title:
        # top-down heuristic: scan for heading-like lines near top
        candidates = []
        i = 0
        while i < min(len(cleaned), 30):
            line = cleaned[i]
            is_upper = line.isupper()
            has_keyword = any(k in line.lower() for k in ['luật', 'bộ luật', 'nghị', 'nghi', 'thông tư', 'thong tu', 'quyết định', 'quyet dinh', 'số', 'so', 'quyết'])
            looks_like_ref = bool(RE_REF_NUMBER.search(line)) or bool(re.search(r'\d{1,4}[\/\-]\d{1,4}', line))
            if (is_upper or has_keyword) and not looks_like_ref:
                buf = [line]
                j = i + 1
                while j < min(len(cleaned), 30):
                    nxt = cleaned[j]
                    # skip lines that look like reference numbers, contain digits, or are anchors
                    if RE_REF_NUMBER.search(nxt) or re.search(r'\d', nxt) or ('căn cứ' in nxt.lower() or 'can cu' in nxt.lower()):
                        break
                    if nxt.isupper() or (len(nxt.split()) <= 8 and nxt[0].isupper()) or any(k in nxt.lower() for k in ['luật', 'bộ luật', 'nghị', 'thông tư', 'quyết định']):
                        buf.append(nxt)
                        j += 1
                    else:
                        break
                cand = ' '.join(buf)
                candidates.append((i, cand))
                i = j
            else:
                i += 1

        if candidates:
            title = candidates[0][1]
        else:
            non_date_lines = [l for l in cleaned[:30] if not RE_DATE.search(l) and not re.search(r'\d', l)]
            if non_date_lines:
                title = non_date_lines[0]

    # 3. Issued date
    for l in cleaned[:40]:
        dm = RE_DATE.search(l)
        if dm:
            if dm.group(1):
                day, month, year = dm.group(1), dm.group(2), dm.group(3)
            else:
                day, month, year = dm.group(4), dm.group(5), dm.group(6)
            try:
                issued_date = datetime(int(year), int(month), int(day)).strftime('%Y-%m-%d')
            except Exception:
                issued_date = None
            break

    return {'title': title or fallback_title, 'reference_number': reference_number, 'issued_date': issued_date}


def extract_zone_1(lines: List[str]) -> str:
    """Split header text from the start of a legal document to the line before 'Căn cứ'."""
    header_lines: List[str] = []
    for raw_line in lines or []:
        line = _clean_line(raw_line)
        if not line:
            continue
        low = line.lower()
        if 'căn cứ' in low or 'can cu' in low:
            break
        if any(stop in low for stop in HEADER_STOP_WORDS):
            continue
        header_lines.append(line)
    return '\n'.join(header_lines).strip()


def extract_header_with_ai(header_text: str) -> Dict[str, Optional[str]]:
    """Use Gemini to clean the header and return title/reference_number JSON."""
    _load_service_env_if_needed()
    cleaned_text = (header_text or '').strip()
    if not cleaned_text:
        return {'title': None, 'reference_number': None}

    try:
        from google import genai
        from google.genai import types
    except Exception as exc:
        logger.error('AI header extraction failed because google-genai is unavailable: %s', exc)
        return {'title': None, 'reference_number': None}

    api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_GENAI_API_KEY')
    if not api_key:
        logger.error('AI header extraction skipped: no Gemini API key was available in the container environment')
        return {'title': None, 'reference_number': None}

    model_name = os.environ.get('GEMINI_MODEL', 'gemini-3.1-flash-lite')
    system_prompt = (
        "Đọc văn bản pháp luật sau. Loại bỏ Quốc hiệu, Tiêu ngữ, Tên cơ quan. "
        "Trả về đúng JSON gồm 2 trường: 'title' và 'reference_number'."
    )
    contents = (
        "Văn bản đầu trang:\n\n"
        f"{cleaned_text}\n\n"
        "Trả về đúng JSON gồm 2 trường: 'title' và 'reference_number'."
    )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0,
                response_mime_type='application/json',
            ),
        )
        raw = (response.text or '').strip()
        if raw.startswith('```'):
            raw = raw.strip('`')
            if raw.lower().startswith('json'):
                raw = raw[4:].strip()
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return {
                'title': parsed.get('title'),
                'reference_number': parsed.get('reference_number'),
            }
        return {'title': None, 'reference_number': None}
    except Exception as exc:
        logger.exception('AI header extraction failed: %s', exc)
        return {'title': None, 'reference_number': None}


def extract_metadata_via_ai(text_content: str) -> Dict[str, Optional[str]]:
    """Fallback to AI to extract metadata. Returns dict with title, reference_number, issued_date or all None."""
    try:
        from google import genai
        from google.genai import types
    except Exception as exc:
        logger.error('AI metadata extraction failed because google-genai is unavailable: %s', exc)
        return {'title': None, 'reference_number': None, 'issued_date': None}

    # Require an API key configured in env to avoid accidental network calls during tests
    if not (os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_GENAI_API_KEY')):
        logger.error('AI metadata extraction skipped: no Gemini API key was available in the container environment')
        return {'title': None, 'reference_number': None, 'issued_date': None}

    client = genai.Client()  # expects environment-configured API key
    system_prompt = (
        'You are a strict extractor. Given the document header text, return a JSON object with keys: "title", "reference_number", "issued_date" (YYYY-MM-DD) or null if missing. '
        'ONLY return a JSON object and nothing else. Do NOT invent or modify words: extract only exact words that appear in the provided text. If a field is not present, return null.'
    )

    contents = f"Document header:\n\n{text_content}\n\nExtract the fields exactly."
    try:
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=system_prompt, temperature=0.0, response_mime_type='application/json')
        )
        raw = response.text or ''
        parsed = json.loads(raw)
        return {
            'title': parsed.get('title'),
            'reference_number': parsed.get('reference_number'),
            'issued_date': parsed.get('issued_date'),
        }
    except Exception as exc:
        logger.exception('AI fallback failed: %s', exc)
        return {'title': None, 'reference_number': None, 'issued_date': None}


def extract_document_metadata(lines: List[str], fallback_title: Optional[str] = None) -> Dict[str, Optional[str]]:
    """Primary entry: lines = cleaned lines from PDF first page.

    The header is split first and AI is used to extract the official title and reference number
    before falling back to legacy regex heuristics.
    """
    _load_service_env_if_needed()
    cleaned = [normalize_text(l) for l in (lines or []) if l and len(str(l).strip()) >= 2]
    zone_1_text = extract_zone_1(cleaned)
    ai_header = extract_header_with_ai(zone_1_text) if zone_1_text else {}

    meta = extract_metadata_from_lines(cleaned, fallback_title=fallback_title)

    if ai_header.get('title') or ai_header.get('reference_number'):
        if ai_header.get('title'):
            meta['title'] = ai_header['title'].strip()
        if ai_header.get('reference_number'):
            meta['reference_number'] = ai_header['reference_number'].strip()

    if not meta.get('title') or not meta.get('reference_number'):
        text_content = '\n'.join(cleaned[:50])
        ai_meta = extract_metadata_via_ai(text_content)
        meta['title'] = meta.get('title') or ai_meta.get('title')
        meta['reference_number'] = meta.get('reference_number') or ai_meta.get('reference_number')
        meta['issued_date'] = meta.get('issued_date') or ai_meta.get('issued_date')
    return meta


def parse_paragraphs(paragraphs: List[str]) -> List[Dict]:
    # Stateful paragraph parser for Vietnamese legal documents.
    # Goals: filter header/footer, detect Part/Chapter/Section/Article/Clause/Point
    nodes: List[Dict] = []
    order = 0

    # regexes for structure
    RE_PART = re.compile(r'^\s*Phần\b', re.IGNORECASE)
    RE_CHAPTER = re.compile(r'^\s*Chương\s+([IVXLCDM]+|\d+)\b', re.IGNORECASE)
    RE_SECTION = re.compile(r'^\s*(Mục|Phần)\s+\d+\b', re.IGNORECASE)
    RE_ARTICLE = re.compile(r'^\s*Điều\s+(\d+)\.?\s*(?:[-:\.]\s*)?(.*)$', re.IGNORECASE)
    RE_CLAUSE = re.compile(r'^\s*(\d+)\.\s+(.*)$')
    RE_POINT = re.compile(r'^\s*([a-zA-Zđêơưảạáàóồỏơư]+)\)\s+(.*)$', re.IGNORECASE)
    RE_PAGE = re.compile(r'^\s*Trang\b|^\s*\d+\s*$', re.IGNORECASE)

    def roman_to_int(s: str) -> Optional[int]:
        s = s.upper().strip()
        ROMAN = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        total = 0
        prev = 0
        for ch in reversed(s):
            val = ROMAN.get(ch, 0)
            if val < prev:
                total -= val
            else:
                total += val
            prev = val
        return total if total > 0 else None

    # header/footer filter heuristics
    HEADER_KEYWORDS = ['công báo', 'công  báo', 'cộng hòa', 'xã hội chủ nghĩa', 'bản in', 'trang']

    # current state
    current = {
        'part': None,
        'section': None,
        'subsection': None,
        'chapter': None,
        'chapter_index': None,
        'article_number': None,
        'article_title': None,
        'clause_number': None,
        'point_label': None,
    }

    def flush_node(content: str, start_idx: int, end_idx: int):
        nonlocal order
        text = normalize_text(content)
        if not text:
            return
        node = {
            'part': current.get('part'),
            'section': current.get('section'),
            'subsection': current.get('subsection'),
            'chapter': current.get('chapter'),
            'chapter_index': current.get('chapter_index'),
            'article_number': current.get('article_number'),
            'article_title': current.get('article_title'),
            'clause_number': current.get('clause_number'),
            'point_label': current.get('point_label'),
            'content': text,
            'order_index': order,
            'start_paragraph_index': start_idx,
            'end_paragraph_index': end_idx,
            'raw_context': {},
            'is_needs_review': False,
            'review_reason': None,
        }
        nodes.append(node)
        order += 1

    # accumulator for multi-line clause/point content
    acc = None
    acc_start = 0

    for idx, p in enumerate(paragraphs):
        line = normalize_text(p if isinstance(p, str) else str(p))
        if not line:
            continue

        low = line.lower()
        # header/footer heuristics: skip lines dominated by header keywords or page numbers
        if any(k in low for k in HEADER_KEYWORDS) and len(line) < 80:
            continue
        if RE_PAGE.match(line):
            continue

        # detect structural tokens
        m_part = RE_PART.match(line)
        m_chapter = RE_CHAPTER.match(line)
        m_section = RE_SECTION.match(line)
        m_article = RE_ARTICLE.match(line)
        m_clause = RE_CLAUSE.match(line)
        m_point = RE_POINT.match(line)

        if m_part:
            # flush any outstanding accumulator
            if acc:
                flush_node(acc, acc_start, idx - 1)
                acc = None
            current['part'] = line.strip()
            # reset lower-level context
            current['chapter'] = None
            current['chapter_index'] = None
            current['section'] = None
            current['article_number'] = None
            current['article_title'] = None
            current['clause_number'] = None
            current['point_label'] = None
            continue

        if m_chapter:
            if acc:
                flush_node(acc, acc_start, idx - 1)
                acc = None
            chap = m_chapter.group(1)
            # try roman to int
            chap_idx = None
            if re.match(r'^[IVXLCDM]+$', chap, re.IGNORECASE):
                chap_idx = roman_to_int(chap)
            else:
                try:
                    chap_idx = int(chap)
                except Exception:
                    chap_idx = None
            current['chapter'] = line.strip()
            current['chapter_index'] = chap_idx
            # reset article/clause context
            current['article_number'] = None
            current['article_title'] = None
            current['clause_number'] = None
            current['point_label'] = None
            continue

        if m_section:
            if acc:
                flush_node(acc, acc_start, idx - 1)
                acc = None
            current['section'] = line.strip()
            current['subsection'] = None
            continue

        if m_article:
            # flush previous accumulator
            if acc:
                flush_node(acc, acc_start, idx - 1)
                acc = None
            art_num = None
            try:
                art_num = int(m_article.group(1))
            except Exception:
                art_num = None
            art_title = m_article.group(2).strip() if m_article.group(2) else None
            current['article_number'] = art_num
            current['article_title'] = art_title if art_title else None
            # reset clause/point
            current['clause_number'] = None
            current['point_label'] = None
            # if article has trailing text beyond title, consider flushing it as content
            if art_title:
                # create an article title node (empty content except title)
                flush_node(art_title, idx, idx)
            continue

        if m_clause and current.get('article_number') is not None:
            # new clause within current article
            if acc:
                flush_node(acc, acc_start, idx - 1)
                acc = None
            cnum = None
            try:
                cnum = int(m_clause.group(1))
            except Exception:
                cnum = None
            ctext = m_clause.group(2).strip()
            current['clause_number'] = cnum
            current['point_label'] = None
            # start new accumulator for clause content
            acc = ctext
            acc_start = idx
            continue

        if m_point and current.get('clause_number') is not None:
            # new point inside current clause
            if acc:
                # flush clause accumulator before point
                flush_node(acc, acc_start, idx - 1)
                acc = None
            plabel = m_point.group(1).strip()
            ptext = m_point.group(2).strip()
            current['point_label'] = plabel
            # directly flush this point as its own node
            flush_node(ptext, idx, idx)
            # keep clause context
            continue

        # default: continuation line -> append to accumulator or start new free node
        if acc:
            acc = acc + ' ' + line
        else:
            # treat as a paragraph within current clause/article context
            acc = line
            acc_start = idx

    # end for: flush remaining accumulator
    if acc:
        flush_node(acc, acc_start, acc_start)

    return nodes
