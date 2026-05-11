import sys
import json
from notebooklm_mcp.server import notebook_describe, notebook_get

notebook_id = 'f1c1d69c-8054-4d81-b2ba-c41811eaaa87'

desc = notebook_describe(notebook_id)
details = notebook_get(notebook_id)

with open('notebook_data.json', 'w', encoding='utf-8') as f:
    json.dump({'desc': desc, 'details': details}, f, ensure_ascii=False, indent=2)
