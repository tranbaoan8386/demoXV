from importlib import util
import os

ROOT = os.path.dirname(__file__)
# load validation engine
spec = util.spec_from_file_location('validation_engine', os.path.join(ROOT, '..', 'src', 'infrastructure', 'validation_engine.py'))
ve = util.module_from_spec(spec)
spec.loader.exec_module(ve)

# helper to run engine
def run_engine(artifact, nodes):
    engine = ve.ValidationEngine()
    res = engine.validate(artifact, nodes)
    return res


def test_orphan_clause_sets_issue_and_flag():
    # artifact: simple paragraphs
    artifact = [
        {'type':'paragraph','text':'Điều 1. Title'},
        {'type':'paragraph','text':'1. Orphan clause'},
    ]
    # parser produced nodes: clause without article
    nodes = [
        {'article_number': None, 'clause_number': 1, 'content':'Orphan clause', 'start_paragraph_index':1, 'end_paragraph_index':1},
    ]
    res = run_engine(artifact, nodes)
    # Expect preservation_loss as artifact vs nodes may mismatch OR orphan clause
    codes = [i.issue_code for i in res.issues]
    assert 'orphan_clause' in codes
    # dynamic review should set flag on node (engine's DynamicReviewRule mutates nodes)
    assert nodes[0].get('is_needs_review') is True
    assert nodes[0].get('review_reason') == 'orphan_clause'


def test_numbering_gap_detected():
    artifact = [
        {'type':'paragraph','text':'Điều 1. Title'},
        {'type':'paragraph','text':'1. First'},
        {'type':'paragraph','text':'3. Third'},
    ]
    nodes = [
        {'article_number':1,'clause_number':1,'content':'First','start_paragraph_index':1,'end_paragraph_index':1},
        {'article_number':1,'clause_number':3,'content':'Third','start_paragraph_index':2,'end_paragraph_index':2},
    ]
    res = run_engine(artifact, nodes)
    codes = [i.issue_code for i in res.issues]
    assert 'gap_clause_number' in codes


def test_text_preservation_detects_missing_paragraphs():
    artifact = [
        {'type':'paragraph','text':'Header'},
        {'type':'paragraph','text':'Keep this text'},
        {'type':'paragraph','text':'Lost text'},
    ]
    # parser missed the last paragraph
    nodes = [
        {'article_number':1,'clause_number':1,'content':'Keep this text','start_paragraph_index':1,'end_paragraph_index':1},
    ]
    res = run_engine(artifact, nodes)
    codes = [i.issue_code for i in res.issues]
    assert 'preservation_loss' in codes
