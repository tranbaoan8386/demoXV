from typing import List, Dict


class HierarchyRule:
    name = 'hierarchy_rule'

    def run(self, ctx: Dict) -> List[Dict]:
        nodes = ctx.get('nodes', [])
        issues = []
        # Build simple stacks: find articles and clauses
        # Map paragraph ranges to node indices
        for idx, n in enumerate(nodes):
            # Orphan clause: clause present but no article_number
            if n.get('clause_number') is not None and n.get('article_number') is None:
                issues.append({
                    'rule_name': self.name,
                    'issue_code': 'orphan_clause',
                    'message': 'Clause without parent article',
                    'severity': 'error',
                    'node_index': idx,
                    'payload': {
                        'start_paragraph_index': n.get('start_paragraph_index'),
                        'end_paragraph_index': n.get('end_paragraph_index'),
                    }
                })
            # Orphan point: point without clause
            if n.get('point_label') and n.get('clause_number') is None:
                issues.append({
                    'rule_name': self.name,
                    'issue_code': 'orphan_point',
                    'message': 'Point label without parent clause',
                    'severity': 'warn',
                    'node_index': idx,
                    'payload': {}
                })
        return issues
