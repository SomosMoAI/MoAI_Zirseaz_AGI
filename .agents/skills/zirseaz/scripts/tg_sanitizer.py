"""
Zirseaz Telegram Sanitizer — Limpia HTML para Telegram.

Telegram SOLO soporta estos tags HTML:
  <b>, <i>, <u>, <s>, <code>, <pre>, <a>, <tg-spoiler>

Cualquier otro tag (<h1>, <table>, <tr>, <td>, <li>, <br>, <p>, <div>, etc.)
debe ser convertido a texto plano ANTES de enviar.

Este modulo usa un enfoque WHITELIST: solo los tags permitidos sobreviven.
Todo lo demas se elimina o convierte.
"""
import re

# Tags que Telegram acepta
ALLOWED_TAGS = {'b', 'i', 'u', 's', 'code', 'pre', 'a', 'tg-spoiler'}


def sanitize(text):
    """
    Sanitiza HTML para Telegram.
    
    1. Convierte tags conocidos a equivalentes de texto
    2. Elimina TODOS los tags que no estan en la whitelist
    3. Limpia espacios y saltos de linea excesivos
    """
    if not text:
        return text or ""
    
    # === PASO 1: Convertir tags semanticos a texto ===
    
    # Headers -> MAYUSCULAS en linea propia
    text = re.sub(
        r'<h[1-6][^>]*>(.*?)</h[1-6]>',
        lambda m: '\n' + m.group(1).strip().upper() + '\n',
        text, flags=re.DOTALL | re.IGNORECASE
    )
    
    # Tablas -> texto con pipes
    # Primero procesar filas
    text = re.sub(
        r'<tr[^>]*>(.*?)</tr>',
        lambda m: _process_table_row(m.group(1)) + '\n',
        text, flags=re.DOTALL | re.IGNORECASE
    )
    # Eliminar tags de tabla restantes
    text = re.sub(r'</?(?:table|thead|tbody|tfoot|caption|colgroup|col)[^>]*>', '', text, flags=re.IGNORECASE)
    
    # Listas -> bullets
    text = re.sub(
        r'<li[^>]*>(.*?)</li>',
        lambda m: '  \u2022 ' + m.group(1).strip() + '\n',
        text, flags=re.DOTALL | re.IGNORECASE
    )
    text = re.sub(r'</?(?:ul|ol|dl|dt|dd)[^>]*>', '', text, flags=re.IGNORECASE)
    
    # <br> -> salto de linea
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    
    # <hr> -> separador visual
    text = re.sub(r'<hr\s*/?>', '\n\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n', text, flags=re.IGNORECASE)
    
    # <p> -> salto de linea
    text = re.sub(r'<p[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
    
    # --- (markdown separator) -> separador visual
    text = re.sub(r'\n-{3,}\n', '\n\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n', text)
    
    # === PASO 2: WHITELIST — eliminar todo tag no permitido ===
    text = re.sub(r'<(/?)(\w[\w-]*)([^>]*)>', _filter_tag, text)
    
    # === PASO 3: Limpiar artefactos ===
    text = re.sub(r'\n{3,}', '\n\n', text)      # Max 2 saltos
    text = re.sub(r'[ \t]+\n', '\n', text)       # Trailing spaces
    text = re.sub(r'\n[ \t]+\n', '\n\n', text)   # Lineas vacias con espacios
    text = text.strip()
    
    return text


def _process_table_row(row_html):
    """Extrae celdas de una fila de tabla y las une con pipes."""
    cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row_html, flags=re.DOTALL | re.IGNORECASE)
    if cells:
        return ' | '.join(cell.strip() for cell in cells)
    return row_html


def _filter_tag(match):
    """Filtra tags HTML: mantiene solo los permitidos por Telegram."""
    slash = match.group(1)  # '' o '/'
    tag_name = match.group(2).lower()
    attrs = match.group(3)
    
    if tag_name in ALLOWED_TAGS:
        # Mantener el tag tal cual
        return match.group(0)
    
    # Tag no permitido -> eliminar
    return ''


def strip_all_html(text):
    """Elimina TODOS los tags HTML, dejando solo texto plano."""
    if not text:
        return text or ""
    return re.sub(r'<[^>]+>', '', text)
