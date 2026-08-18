from typing import List, Dict


class DynamicReviewRule:
    name = 'dynamic_review_rule'

    def run(self, ctx: Dict) -> List[Dict]:
        nodes = ctx.get('nodes', [])
        prev_issues = ctx.get('issues', [])
        severity_map = {}
        for pi in prev_issues:
            ni = pi.get('node_index')
            sev = pi.get('severity', 'info')
            if ni is not None:
                prev = severity_map.get(ni)
                order = {'info': 0, 'warn': 1, 'error': 2}
                if prev is None or order.get(sev, 0) > order.get(prev, 0):
                    severity_map[ni] = sev
        for idx, n in enumerate(nodes):
            sev = severity_map.get(idx)
            if sev in ('warn', 'error'):
                n['is_needs_review'] = True
                reasons = [pi.get('issue_code') for pi in prev_issues if pi.get('node_index') == idx]
                n['review_reason'] = reasons[0] if reasons else 'validation_issue'
                continue
            # if node has no issue but is in a doc with global validation issue, still flag minimally
            if not n.get('is_needs_review') and any(pi.get('issue_code') in {'preservation_loss', 'orphan_clause', 'gap_clause_number'} for pi in prev_issues if pi.get('node_index') is None):
                n['is_needs_review'] = True
                n['review_reason'] = 'document_validation_issue'
        return []
