import json
from notebooklm_mcp.server import notebook_query

moai_id = 'dc649b85-61d9-437b-96e6-6a4bd34978ec'
cuatico_id = 'e522b5d3-eb2b-48b9-849a-e92ccbbac2fc'

res_moai = notebook_query(moai_id, "What is the tone of voice, content pillars, and target audience for MOAI?")
res_cuatico = notebook_query(cuatico_id, "What is the tone of voice, content pillars, and target audience for Cine para Cuaticos?")

with open('strategy_results.json', 'w', encoding='utf-8') as f:
    json.dump({'moai': res_moai, 'cuatico': res_cuatico}, f, ensure_ascii=False, indent=2)
