from typing import List, Dict, Tuple


def validate_extraction_items(items: List[Dict], min_paragraphs: int = 1) -> Tuple[bool, str]:
    """Simple extraction validator.

    Returns (is_valid, error_message).
    - Ensures at least min_paragraphs paragraphs exist
    - Ensures items are not empty
    """
    if not items:
        return False, 'no extracted items'

    para_count = sum(1 for it in items if it.get('type') == 'paragraph' and (it.get('text') or '').strip())
    if para_count < min_paragraphs:
        return False, f'paragraph_count_too_small: {para_count} < {min_paragraphs}'

    # Additional simple checks: ensure string types
    for it in items:
        if it.get('type') == 'paragraph' and not isinstance(it.get('text', ''), str):
            return False, 'paragraph_not_string'
        if it.get('type') == 'table' and not isinstance(it.get('rows', []), list):
            return False, 'table_structure_invalid'

    return True, ''
