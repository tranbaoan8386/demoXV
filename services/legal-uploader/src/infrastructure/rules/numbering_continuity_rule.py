from typing import List, Dict


class NumberingContinuityRule:
    name = 'numbering_continuity_rule'

    def run(self, ctx: Dict) -> List[Dict]:
        nodes = ctx.get('nodes', [])
        issues = []
        current_article = None
        last_clause_num = None
        # We'll walk nodes in order and only reset continuity when the article changes.
        for idx, n in enumerate(nodes):
            art = n.get('article_number')
            if art is not None:
                if current_article is None or art != current_article:
                    current_article = art
                    last_clause_num = None
            if n.get('clause_number') is not None:
                cn = n.get('clause_number')
                if last_clause_num is None:
                    last_clause_num = cn
                elif cn != last_clause_num + 1:
                    issues.append({
                        'rule_name': self.name,
                        'issue_code': 'gap_clause_number',
                        'message': f'Clause numbering jump from {last_clause_num} to {cn} in article {current_article}',
                        'severity': 'warn',
                        'node_index': idx,
                        'payload': {'previous': last_clause_num, 'current': cn, 'article': current_article}
                    })
                last_clause_num = cn
        return issues
