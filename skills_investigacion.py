
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re

def buscar_en_web(query, num_results=5):
    """Busqueda simple usando DuckDuckGo (sin API key)"""
    url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for result in soup.select(".result__a")[:num_results]:
            title = result.get_text(strip=True)
            link = result.get("href", "")
            # Extraer URL real de redireccion
            if "//uddg=" in link:
                link = link.split("uddg=")[-1].split("&")[0]
                from urllib.parse import unquote
                link = unquote(link)
            results.append({"title": title, "url": link})
        return results
    except Exception as e:
        return [{"error": str(e)}]

def leer_contenido_url(url):
    """Lee el contenido HTML de una URL y extrae texto limpio"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        # Eliminar scripts, estilos, etc
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        # Limpiar lineas vacias multiples
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        return "\n".join(lines[:300])  # Limitar a 300 lineas
    except Exception as e:
        return f"Error al leer {url}: {str(e)}"
