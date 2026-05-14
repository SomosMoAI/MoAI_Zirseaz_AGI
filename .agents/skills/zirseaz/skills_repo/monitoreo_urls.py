
def verificar_url(url, expected_text=None):
    """Verifica que una URL responda 200 y contenga texto esperado"""
    import urllib.request, ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        html = resp.read().decode('utf-8')
        status = f"OK 200 — {len(html)} bytes"
        if expected_text and expected_text in html:
            status += f" — Contiene: {expected_text[:50]}"
        elif expected_text:
            status += f" — FALTA texto esperado"
        return {"url": url, "status": status, "ok": True}
    except Exception as e:
        return {"url": url, "status": f"ERROR: {str(e)[:100]}", "ok": False}
