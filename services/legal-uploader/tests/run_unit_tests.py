import importlib.util
import os
import sys

ROOT = os.path.dirname(__file__)
files = [
    os.path.join(ROOT, 'test_extraction.py'),
    os.path.join(ROOT, 'test_schema_phase2.py'),
    os.path.join(ROOT, 'test_parser_phase3.py'),
    os.path.join(ROOT, 'test_validation_phase4.py'),
    os.path.join(ROOT, 'test_golden_dataset_phase5.py'),
    os.path.join(ROOT, 'test_storage_phase6.py'),
]

def load_and_run(path):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    failures = 0
    for attr in dir(mod):
        if attr.startswith('test_') and callable(getattr(mod, attr)):
            try:
                print(f'RUNNING {name}.{attr}()')
                getattr(mod, attr)()
            except AssertionError as e:
                print(f'FAIL {name}.{attr}:', e)
                failures += 1
            except Exception as e:
                print(f'ERROR {name}.{attr}:', e)
                failures += 1
    return failures

def main():
    total_fail = 0
    for f in files:
        total_fail += load_and_run(f)
    if total_fail:
        print(f'FAILED {total_fail} tests')
        sys.exit(1)
    print('ALL TESTS PASSED')

if __name__ == '__main__':
    main()
