from importlib.util import spec_from_file_location, module_from_spec
import os
p = os.path.join('src','infrastructure','validation_engine.py')
spec = spec_from_file_location('ve', p)
mod = module_from_spec(spec)
spec.loader.exec_module(mod)
engine = mod.ValidationEngine()
art = [
    {'type':'paragraph','text':'Điều 1. Title'},
    {'type':'paragraph','text':'1. First'},
    {'type':'paragraph','text':'3. Third'},
]
nodes = [
    {'article_number':1,'clause_number':1,'content':'First','start_paragraph_index':1,'end_paragraph_index':1},
    {'article_number':1,'clause_number':3,'content':'Third','start_paragraph_index':2,'end_paragraph_index':2},
]
res = engine.validate(art, nodes)
print(res.issues)
for n in nodes:
    print(n)
