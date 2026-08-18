import os
import sys
from typing import List, Dict, Any
from dataclasses import dataclass, field

try:
    from .rules.hierarchy_rule import HierarchyRule
    from .rules.numbering_continuity_rule import NumberingContinuityRule
    from .rules.text_preservation_rule import TextPreservationRule
    from .rules.dynamic_review_rule import DynamicReviewRule
except ImportError:
    base = os.path.dirname(__file__)
    rules_dir = os.path.join(base, 'rules')
    if rules_dir not in sys.path:
        sys.path.insert(0, rules_dir)
    from hierarchy_rule import HierarchyRule
    from numbering_continuity_rule import NumberingContinuityRule
    from text_preservation_rule import TextPreservationRule
    from dynamic_review_rule import DynamicReviewRule


@dataclass
class Issue:
    rule_name: str
    issue_code: str
    message: str
    severity: str
    node_index: int = None
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    issues: List[Issue] = field(default_factory=list)
    modified_nodes: List[Dict[str, Any]] = field(default_factory=list)


class ValidationEngine:
    def __init__(self, rules=None):
        # default ordered rules
        self.rules = rules or [
            TextPreservationRule(),
            HierarchyRule(),
            NumberingContinuityRule(),
            DynamicReviewRule(),
        ]

    def validate(self, artifact_items: List[Dict], parsed_nodes: List[Dict]) -> ValidationResult:
        ctx = {
            'artifact': artifact_items,
            'nodes': parsed_nodes,
            'issues': [],
        }
        issues: List[Issue] = []
        # run rules
        for rule in self.rules:
            r_issues = rule.run(ctx)
            # convert to Issue dataclass
            for ri in r_issues:
                issue = Issue(**ri)
                issues.append(issue)
                ctx['issues'].append(ri)
        # final pass: dynamic review applies flags based on accumulated issues
        if isinstance(self.rules[-1], DynamicReviewRule):
            self.rules[-1].run(ctx)
        return ValidationResult(issues=issues, modified_nodes=ctx.get('nodes', []))
