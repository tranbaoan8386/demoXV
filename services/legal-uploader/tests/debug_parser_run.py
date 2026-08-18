from importlib import util
import os
P = os.path.join(os.path.dirname(__file__), '..', 'src', 'infrastructure', 'parser.py')
spec = util.spec_from_file_location('parser', P)
mod = util.module_from_spec(spec)
spec.loader.exec_module(mod)
els = ['Phần I','Chương I. Những quy định chung','Điều 2. Title here','1. First clause',{'type':'table','rows':[['H1','H2'],['v1','v2']]},'2. Second clause after table']
nodes = mod.parse_paragraphs(els)
print('NODES:')
for n in nodes:
    print(n)
