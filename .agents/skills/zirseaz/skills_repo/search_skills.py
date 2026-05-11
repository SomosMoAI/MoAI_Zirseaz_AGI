import urllib.request
import urllib.parse
import re
import os
import sys
import json

# Asegurar imports desde utils/
_SKILL_ROOT = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz")
_UTILS_DIR = os.path.join(_SKILL_ROOT, "utils")
if _UTILS_DIR not in sys.path:
    sys.path.insert(0, _UTILS_DIR)

try:
    import env_loader
except ImportError:
    env_loader = None

def buscar_en_web(query):
    """Busca en la web usando DuckDuckGo (HTML) y devuelve los primeros resultados."""
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({'q': query})
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        
        if not snippets:
            return "No se encontraron resultados o DuckDuckGo bloqueó la petición."
            
        clean_snippets = []
        for s in snippets[:3]:
            clean = re.sub(r'<[^>]+>', '', s)
            clean = clean.replace('&amp;', '&').replace('&quot;', '"').strip()
            clean_snippets.append("- " + clean)
            
        return f"Resultados de búsqueda para '{query}':\n\n" + "\n\n".join(clean_snippets)
        
    except Exception as e:
        return f"Error al buscar en la web: {e}"

def leer_contenido_url(url):
    """Lee el contenido de texto de una URL pública (Scraping básico)."""
    if not url.startswith("http"):
        url = "https://" + url
        
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
        # Quitar scripts y estilos
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        
        # Quitar todas las etiquetas HTML
        text = re.sub(r'<[^>]+>', ' ', html)
        
        # Limpiar espacios en blanco múltiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Retornar un extracto (los primeros 2000 caracteres para no saturar el contexto)
        return f"Contenido extraído de {url}:\n\n" + text[:2000] + "..."
        
    except Exception as e:
        return f"Error al leer la URL: {e}"

def _get_news_api_key():
    """Busca la API key de NewsAPI usando env_loader o fallback manual."""
    if env_loader:
        return env_loader.get("NEWS_API_KEY")
    key = os.environ.get("NEWS_API_KEY")
    if key:
        return key
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("NEWS_API_KEY="):
                    return line.split("=")[1].strip()
    return None

def buscar_noticias_newsapi(query):
    """Busca noticias recientes usando la API de NewsAPI con la key del usuario."""
    api_key = _get_news_api_key()
    if not api_key:
        return "Error: No se encontró NEWS_API_KEY en las variables de entorno ni en el archivo .env."
        
    try:
        url = "https://newsapi.org/v2/everything?" + urllib.parse.urlencode({
            'q': query,
            'apiKey': api_key,
            'language': 'es',
            'sortBy': 'publishedAt',
            'pageSize': 5
        })
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        if data.get("status") != "ok":
            return f"Error de NewsAPI: {data.get('message', 'Desconocido')}"
            
        articles = data.get("articles", [])
        if not articles:
            return f"No se encontraron noticias para: '{query}'"
            
        results = []
        for a in articles:
            title = a.get("title", "Sin título")
            date = a.get("publishedAt", "")[:10]
            desc = a.get("description", "Sin descripción")
            link = a.get("url", "#")
            results.append(f"- <b>{title}</b> ({date})\n  {desc}\n  Link: {link}")
            
        return f"Noticias encontradas en NewsAPI para '{query}':\n\n" + "\n\n".join(results)
        
    except Exception as e:
        return f"Error al conectar con NewsAPI: {e}"
