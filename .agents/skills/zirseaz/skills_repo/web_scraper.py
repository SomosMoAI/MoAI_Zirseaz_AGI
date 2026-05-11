import urllib.request
import re
from html.parser import HTMLParser


class MLStripper(HTMLParser):
    """Parser HTML que extrae solo texto visible, usando stack de tags para manejar anidamiento."""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
        self.skip_tags = {'script', 'style', 'head', 'meta', 'noscript', 'svg'}
        self._tag_stack = []  # Stack para manejar tags anidados correctamente

    def handle_starttag(self, tag, attrs):
        self._tag_stack.append(tag)

    def handle_endtag(self, tag):
        # Pop hasta encontrar el tag correspondiente (tolerante a HTML malformado)
        while self._tag_stack and self._tag_stack[-1] != tag:
            self._tag_stack.pop()
        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, d):
        # Solo incluir texto si no estamos dentro de ningún tag a ignorar
        if not any(t in self.skip_tags for t in self._tag_stack):
            text = d.strip()
            if text:
                self.text.append(text)

    def get_data(self):
        return '\n'.join(self.text)


def scrape_url(url, max_chars=8000):
    """
    Descarga el contenido de una URL y extrae solo el texto visible.
    Útil para leer documentación o artículos.
    """
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            stripper = MLStripper()
            stripper.feed(html)
            text = stripper.get_data()
            
            # Limpieza básica de espacios extra
            text = re.sub(r'\n\s*\n', '\n\n', text)
            
            if len(text) > max_chars:
                return text[:max_chars] + "\n...[CONTENIDO TRUNCADO POR LONGITUD]..."
            return text
    except Exception as e:
        return f"Error leyendo {url}: {str(e)}"
