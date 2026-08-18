import json
import os
from importlib import util

ROOT = os.path.dirname(__file__)
SERVICE_ROOT = os.path.join(ROOT, '..')

# import validation engine
spec = util.spec_from_file_location(
    'validation_engine',
    os.path.join(SERVICE_ROOT, 'src', 'infrastructure', 'validation_engine.py')
)
validation_engine_mod = util.module_from_spec(spec)
spec.loader.exec_module(validation_engine_mod)


VALIDATION_ENGINE = validation_engine_mod.ValidationEngine()


def _load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _load_artifact(path):
    items = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def _build_parsed_nodes_for_fixture(artifact_items):
    nodes = []
    article_no = None
    for idx, item in enumerate(artifact_items):
        text = item.get('text', '')
        if not text:
            continue
        if not text.startswith('Điều ') and not text.startswith(tuple(str(i) + '.' for i in range(1, 10))):
            nodes.append({
                'article_number': None,
                'clause_number': None,
                'content': text,
                'start_paragraph_index': idx,
                'end_paragraph_index': idx,
                'raw_context': {'original': text},
            })
            continue
        if text.startswith('Điều '):
            article_no = int(text.split('Điều ', 1)[1].split('.', 1)[0])
            nodes.append({
                'article_number': article_no,
                'article_title': text.split('.', 1)[1].strip() if '.' in text else '',
                'content': text.split('.', 1)[1].strip() if '.' in text else text,
                'start_paragraph_index': idx,
                'end_paragraph_index': idx,
                'raw_context': {'original': text},
            })
            continue
        if text.startswith(tuple(str(i) + '.' for i in range(1, 10))):
            clause_no = int(text.split('.', 1)[0])
            nodes.append({
                'article_number': article_no,
                'clause_number': clause_no,
                'content': text.split('.', 1)[1].strip(),
                'start_paragraph_index': idx,
                'end_paragraph_index': idx,
                'raw_context': {'original': text},
            })
    return nodes


def _assert_invariants(fixture_dir, metric_file):
    artifact_path = os.path.join(fixture_dir, 'artifact.jsonl')
    metrics = _load_json(metric_file)
    artifact_items = _load_artifact(artifact_path)
    parsed = _build_parsed_nodes_for_fixture(artifact_items)
    result = VALIDATION_ENGINE.validate(artifact_items, parsed)
    codes = [i.issue_code for i in result.issues]
    # Guard rails: zero tolerance on the critical invariants for golden docs.
    assert metrics['orphan_clause_rate'] == 0.0, 'orphan clause rate must be 0'
    assert metrics['orphan_point_rate'] == 0.0, 'orphan point rate must be 0'
    assert metrics['preservation_loss_count'] == 0, 'preservation loss must be zero'
    assert metrics['is_needs_review_rate'] <= 0.01, 'review rate must be <= 1%'
    assert 'preservation_loss' not in codes, 'no text preservation loss allowed in golden dataset'
    assert 'orphan_clause' not in codes, 'no orphan clause allowed in golden dataset'
    assert 'gap_clause_number' not in codes, 'no numbering gap allowed in golden dataset'


def test_golden_dataset_civil_code_2015():
    fixture_dir = os.path.join(ROOT, 'fixtures', 'golden_v1', 'civil_code_2015')
    _assert_invariants(fixture_dir, os.path.join(fixture_dir, 'expected_metrics.json'))


def test_golden_dataset_real_estate_law_2023():
    fixture_dir = os.path.join(ROOT, 'fixtures', 'golden_v1', 'real_estate_business_law_2023')
    _assert_invariants(fixture_dir, os.path.join(fixture_dir, 'expected_metrics.json'))
