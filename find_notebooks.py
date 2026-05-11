import json
import traceback
from notebooklm_mcp.server import notebook_list, notebook_query, notebook_get

def find_notebooks():
    try:
        # Get list of notebooks
        res = notebook_list(max_results=50)
        if res.get('status') != 'success':
            print(f"Error fetching notebooks: {res}")
            return
            
        notebooks = res.get('notebooks', [])
        found_moai = None
        found_cuatico = None
        
        for nb in notebooks:
            title = nb.get('title', '').lower()
            if 'moai' in title:
                found_moai = nb
            elif 'cuático' in title or 'cuatico' in title:
                found_cuatico = nb
                
        # If we didn't find specific ones, maybe the info is in the same notebook we used before?
        # Let's just dump the notebooks list
        with open('notebook_list_result.json', 'w', encoding='utf-8') as f:
            json.dump({
                'all_notebooks': notebooks,
                'found_moai': found_moai,
                'found_cuatico': found_cuatico
            }, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(traceback.format_exc())

if __name__ == "__main__":
    find_notebooks()
