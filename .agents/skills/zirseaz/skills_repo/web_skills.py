"""
Zirseaz Web Skills — Funciones para desplegar contenido web.
"""
import os
import sys
import ftplib
import io

# Asegurar paths
_SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_UTILS_DIR = os.path.join(_SKILL_ROOT, "utils")
if _UTILS_DIR not in sys.path:
    sys.path.insert(0, _UTILS_DIR)

try:
    import env_loader
except ImportError:
    # Fallback si no está en el path esperado
    sys.path.insert(0, r"c:\Users\cueva\OneDrive\Escritorio\Agentes\.agents\skills\zirseaz\utils")
    import env_loader

def upload_premium_landing():
    """
    Genera y sube una landing page ultra-premium por defecto para el newsletter.
    La sube a zirseaz/newsletter/index.html.
    """
    # (Mantengo el código anterior para tener un fallback funcional)
    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MOAI — Newsletter Premium by Zirseaz</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #030305;
            --text: #f8fafc;
            --accent: #6366f1;
            --accent-glow: rgba(99, 102, 241, 0.3);
            --glass: rgba(255, 255, 255, 0.02);
            --glass-border: rgba(255, 255, 255, 0.05);
            --card-bg: rgba(10, 10, 15, 0.8);
        }
        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg);
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 0%, rgba(168, 85, 247, 0.1) 0px, transparent 50%);
            color: var(--text);
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow-x: hidden;
        }
        .container {
            max-width: 1100px;
            width: 100%;
            padding: 3rem 1.5rem;
        }
        header {
            text-align: center;
            margin-bottom: 4rem;
        }
        .logo {
            font-weight: 800;
            font-size: 1.2rem;
            letter-spacing: 0.3rem;
            color: var(--accent);
            text-transform: uppercase;
            margin-bottom: 1rem;
            display: block;
        }
        h1 {
            font-size: 3.5rem;
            font-weight: 800;
            margin: 0;
            background: linear-gradient(to bottom right, #ffffff 30%, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.05em;
        }
        p.subtitle {
            color: #94a3b8;
            font-size: 1.2rem;
            font-weight: 300;
            margin-top: 0.5rem;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            margin-bottom: 4rem;
        }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 2rem;
            backdrop-filter: blur(20px);
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            text-align: left;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .card:hover {
            border-color: var(--accent);
            transform: translateY(-5px);
            box-shadow: 0 10px 30px var(--accent-glow);
        }
        .card.featured {
            grid-column: span 2;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(168, 85, 247, 0.05));
        }
        .cta-btn {
            background: #ffffff;
            color: #000000;
            border: none;
            padding: 1rem 2rem;
            border-radius: 30px;
            font-weight: 500;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            margin-top: 1rem;
        }
        .cta-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255,255,255,0.4);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <span class="logo">MOAI Architettura</span>
            <h1>Newsletter Intelligence</h1>
            <p class="subtitle">Desplegado por Zirseaz v7 — Cortex</p>
        </header>
        <div class="grid">
            <div class="card featured">
                <div>
                    <h3>El Arquitecto + El Cirujano + El Mago</h3>
                    <p>Nuestra IA no solo resume noticias; opera con precisión quirúrgica para entregarte las oportunidades de negocio que otros ignoran en el mercado de Inteligencia Artificial.</p>
                </div>
                <div>
                    <a href="#" class="cta-btn">Suscribirse Ahora</a>
                </div>
            </div>
            <div class="card">
                <div>
                    <h3>100% Autónomo</h3>
                    <p>Zirseaz investiga, filtra y redacta. Sin intervención humana.</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    return _upload_to_ftp(html_content)


def improve_landing_page(instructions):
    """
    Llama a la IA para generar un nuevo HTML basado en instrucciones y lo sube.
    """
    from openai import OpenAI
    
    print(f"Mejorando página con instrucciones: {instructions}")
    
    keys = env_loader.get_api_keys()
    api_key = keys.get("deepseek") or keys.get("groq") or keys.get("gemini")
    
    if not api_key:
        return "Error: No se encontró API key en el entorno."
        
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com" if "deepseek" in keys else None)
    model_name = "deepseek-chat" if "deepseek" in keys else "llama3-70b-8192"
    
    prompt = f"""
    Eres un diseñador web experto de élite. Tu objetivo es crear el código HTML completo (incluyendo CSS en la etiqueta <style>) para una landing page de un newsletter premium de Inteligencia Artificial.
    
    Debes aplicar estrictamente estas instrucciones de mejora solicitadas por el usuario:
    "{instructions}"
    
    Identidad de Marca Obligatoria (MOAI):
    - Arquetipo: El Arquitecto + El Cirujano + El Mago. Autoridad técnica, eficiencia quirúrgica e innovación disruptiva.
    - Estética: Futurista, premium, paleta oscura con acentos vibrantes (gradientes violeta/azul, efectos neon sutiles).
    - Layout: Usa conceptos modernos como Bento Grid, Glassmorphism (efectos de desenfoque de fondo), y tipografía limpia (ej. Inter u Outfit).
    
    Reglas de salida:
    - Responde ÚNICAMENTE con el código HTML completo y válido.
    - NO incluyas bloques de código con ```html ni texto explicativo antes o después.
    - Asegúrate de que sea responsive (móvil y desktop).
    """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        new_html = response.choices[0].message.content.strip()
        
        # Limpieza por si la IA ignora la regla de los backticks
        if new_html.startswith("```"):
            lines = new_html.split('\n')
            if lines[0].startswith("```"):
                new_html = '\n'.join(lines[1:])
            if lines[-1].startswith("```"):
                new_html = '\n'.join(lines[:-1])
        new_html = new_html.strip()
        
        return _upload_to_ftp(new_html)
        
    except Exception as e:
        return f"Error generando HTML con IA: {e}"


def _upload_to_ftp(html_content):
    """Función interna para subir el HTML al FTP."""
    creds = env_loader.get_hosting_credentials()
    host = creds.get("host")
    user = creds.get("user")
    pw = creds.get("pass")
    
    if not all([host, user, pw]):
        return "Error: No se encontraron credenciales de hosting en el .env."
        
    try:
        ftp = ftplib.FTP(host)
        ftp.login(user, pw)
        
        # Navegar a la carpeta visible
        try: ftp.cwd('zirseaz')
        except:
            ftp.mkd('zirseaz')
            ftp.cwd('zirseaz')
            
        try: ftp.cwd('newsletter')
        except:
            ftp.mkd('newsletter')
            ftp.cwd('newsletter')
            
        # Subir el archivo
        bio = io.BytesIO(html_content.encode('utf-8'))
        ftp.storbinary('STOR index.html', bio)
        ftp.quit()
        
        return "Éxito: Página desplegada correctamente por Zirseaz en mo-ai.cl/zirseaz/newsletter/"
    except Exception as e:
        return f"Error en la operación FTP: {e}"
