import sys
import json
from notebooklm_mcp.server import notebook_query

notebook_id = 'f1c1d69c-8054-4d81-b2ba-c41811eaaa87'

queries = [
    "How to build an agent from scratch in Antigravity including directory structure and basics?",
    "How to implement human-in-the-loop, user validation, or interaction confirmation in Antigravity agents?",
    "What are the best practices or available tools for authoring Skills for things like image generation and social media?"
]

results = {}
for i, q in enumerate(queries):
    res = notebook_query(notebook_id, q)
    results[f'query_{i+1}'] = res

with open('notebook_queries.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
