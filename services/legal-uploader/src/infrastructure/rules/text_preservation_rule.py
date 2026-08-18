from typing import List, Dict
import unicodedata
import hashlib


def normalize_text(s: str) -> str:
    if s is None:
        return ''
    s = unicodedata.normalize('NFC', s)
    # drop legal-document numbering markers that are structural metadata rather than content
    s = s.strip()
    s = __import__('re').sub(r'^\s*(?:Điều\s*\d+\.|Khoản\s*\d+\.|Điểm\s*[a-zđê]+\)|\d+\.|[a-zđê]+\))\s*', '', s, flags=__import__('re').UNICODE | __import__('re').IGNORECASE)
    return ' '.join(s.split())


class TextPreservationRule:
    name = 'text_preservation_rule'

    def run(self, ctx: Dict) -> List[Dict]:
        artifact = ctx.get('artifact', [])
        nodes = ctx.get('nodes', [])
        issues = []
        # Build artifact concatenation by paragraph order, stripping numbering metadata that is not semantic content.
        parts = []
        for it in artifact:
            if it.get('type') == 'paragraph':
                parts.append(normalize_text(it.get('text', '')))
            elif it.get('type') == 'table':
                rows = it.get('rows', [])
                for r in rows:
                    parts.append(normalize_text('\t'.join([c or '' for c in r])))
        artifact_text = ' '.join([p for p in parts if p])
        # Build nodes text concatenation
        node_parts = []
        for n in nodes:
            c = n.get('content')
            if c:
                node_parts.append(normalize_text(c))
            rc = n.get('raw_context') or {}
            if rc.get('table_rows'):
                for r in rc.get('table_rows'):
                    node_parts.append(normalize_text('\t'.join([c or '' for c in r])))
        nodes_text = ' '.join([p for p in node_parts if p])
        # Compare checksums on normalized content.
        ah = hashlib.sha256(artifact_text.encode('utf-8')).hexdigest()
        nh = hashlib.sha256(nodes_text.encode('utf-8')).hexdigest()
        if ah != nh:
            missing = []
            covered = set()
            for n in nodes:
                sp = n.get('start_paragraph_index')
                ep = n.get('end_paragraph_index')
                if sp is not None and ep is not None:
                    for i in range(sp, ep + 1):
                        covered.add(i)
            for idx, it in enumerate(artifact):
                if idx not in covered:
                    missing.append(idx)
            issues.append({
                'rule_name': self.name,
                'issue_code': 'preservation_loss',
                'message': 'Artifact text not fully preserved in parsed nodes',
                'severity': 'error',
                'node_index': None,
                'payload': {'missing_paragraph_indices': missing, 'artifact_hash': ah, 'nodes_hash': nh}
            })
        return issues
