#!/usr/bin/env python3
"""
render_preview.py — Generador de Previsualizaciones HTML para Posts de RRSS.

Genera un archivo HTML estilizado que simula cómo se verán los posts
en LinkedIn e Instagram antes de publicarlos. Permite revisión visual
del contenido por parte del humano (HITL).

Uso:
    python render_preview.py --input grilla.json --output preview_posts.html
    python render_preview.py --platform linkedin --text "Copy aquí..." --image_prompt "prompt..."
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MOAI — Preview de Posts RRSS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0a0f;
            --bg-card: #12121a;
            --bg-card-hover: #1a1a2e;
            --accent-cyan: #00d4ff;
            --accent-magenta: #ff006e;
            --accent-green: #00ff88;
            --text-primary: #f0f0f5;
            --text-secondary: #8888aa;
            --border-subtle: #2a2a3e;
            --linkedin-blue: #0077b5;
            --instagram-gradient: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 2rem;
        }}

        .header {{
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem;
            background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(255,0,110,0.08));
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
        }}

        .header h1 {{
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-magenta));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}

        .header .subtitle {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}

        .header .timestamp {{
            color: var(--accent-cyan);
            font-size: 0.75rem;
            margin-top: 0.5rem;
            font-family: monospace;
        }}

        .hitl-banner {{
            background: linear-gradient(90deg, rgba(255,0,110,0.15), rgba(0,212,255,0.15));
            border: 1px solid var(--accent-magenta);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .hitl-banner .icon {{
            font-size: 2rem;
        }}

        .hitl-banner .text {{
            font-size: 0.85rem;
            color: var(--text-secondary);
        }}

        .hitl-banner .text strong {{
            color: var(--accent-magenta);
        }}

        .posts-grid {{
            display: flex;
            flex-direction: column;
            gap: 2.5rem;
            max-width: 680px;
            margin: 0 auto;
        }}

        .post-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            overflow: hidden;
            transition: all 0.3s ease;
        }}

        .post-card:hover {{
            border-color: var(--accent-cyan);
            box-shadow: 0 0 30px rgba(0,212,255,0.1);
            transform: translateY(-2px);
        }}

        .post-card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .platform-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.35rem 0.8rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .platform-badge.linkedin {{
            background: rgba(0,119,181,0.2);
            color: var(--linkedin-blue);
            border: 1px solid rgba(0,119,181,0.3);
        }}

        .platform-badge.instagram {{
            background: linear-gradient(45deg, rgba(240,148,51,0.2), rgba(188,24,136,0.2));
            color: #e6683c;
            border: 1px solid rgba(220,39,67,0.3);
        }}

        .post-meta {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .meta-tag {{
            font-size: 0.7rem;
            color: var(--text-secondary);
            padding: 0.2rem 0.5rem;
            background: rgba(255,255,255,0.05);
            border-radius: 6px;
        }}

        .post-body {{
            padding: 1.5rem;
        }}

        .post-copy {{
            font-size: 0.92rem;
            line-height: 1.7;
            color: var(--text-primary);
            white-space: pre-wrap;
            word-wrap: break-word;
        }}

        .image-prompt-section {{
            margin-top: 1.5rem;
            padding: 1rem 1.25rem;
            background: rgba(0,212,255,0.05);
            border: 1px dashed rgba(0,212,255,0.3);
            border-radius: 10px;
        }}

        .image-prompt-section .label {{
            font-size: 0.7rem;
            font-weight: 700;
            color: var(--accent-cyan);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.5rem;
        }}

        .image-prompt-section .prompt {{
            font-size: 0.82rem;
            color: var(--text-secondary);
            line-height: 1.5;
            font-style: italic;
        }}

        .post-footer {{
            padding: 1rem 1.5rem;
            border-top: 1px solid var(--border-subtle);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .status-pending {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.75rem;
            color: #ffaa00;
        }}

        .status-pending .dot {{
            width: 8px;
            height: 8px;
            background: #ffaa00;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.3; }}
        }}

        .post-number {{
            font-size: 0.7rem;
            color: var(--text-secondary);
            font-family: monospace;
        }}

        .footer {{
            text-align: center;
            margin-top: 3rem;
            padding: 1.5rem;
            color: var(--text-secondary);
            font-size: 0.75rem;
        }}

        .footer a {{
            color: var(--accent-cyan);
            text-decoration: none;
        }}

        @media (max-width: 600px) {{
            body {{ padding: 1rem; }}
            .header h1 {{ font-size: 1.4rem; }}
            .post-body {{ padding: 1rem; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🗓️ MOAI — Preview de Grilla</h1>
        <div class="subtitle">Mega-Agente de Marketing Multicanal (MAMM)</div>
        <div class="timestamp">Generado: {timestamp}</div>
    </div>

    <div class="hitl-banner">
        <div class="icon">🛑</div>
        <div class="text">
            <strong>HUMAN-IN-THE-LOOP ACTIVO.</strong> Este contenido requiere tu aprobación explícita antes de ser publicado.
            Revisa cada post y responde "OK" en el chat de Antigravity para autorizar el despliegue.
        </div>
    </div>

    <div class="posts-grid">
        {posts_html}
    </div>

    <div class="footer">
        Generado por <a href="#">MAMM</a> · MOAI (MO-AI.CL) · Powered by Antigravity &amp; n8n
    </div>
</body>
</html>"""

POST_CARD_TEMPLATE = """
    <div class="post-card">
        <div class="post-card-header">
            <span class="platform-badge {platform_class}">{platform_icon} {platform}</span>
            <div class="post-meta">
                <span class="meta-tag">🎯 {objective}</span>
                <span class="meta-tag">📌 {pillar}</span>
            </div>
        </div>
        <div class="post-body">
            <div class="post-copy">{copy}</div>
            <div class="image-prompt-section">
                <div class="label">🖼️ Prompt de Imagen (Nano Banana / generate_image)</div>
                <div class="prompt">{image_prompt}</div>
            </div>
        </div>
        <div class="post-footer">
            <span class="status-pending"><span class="dot"></span> Pendiente de aprobación</span>
            <span class="post-number">Post #{post_number}</span>
        </div>
    </div>"""


def render_post_card(post: dict, index: int) -> str:
    """Render a single post card HTML."""
    platform = post.get("platform", "LinkedIn").strip()
    platform_lower = platform.lower()

    if "linkedin" in platform_lower:
        platform_class = "linkedin"
        platform_icon = "💼"
    else:
        platform_class = "instagram"
        platform_icon = "📸"

    return POST_CARD_TEMPLATE.format(
        platform_class=platform_class,
        platform_icon=platform_icon,
        platform=platform,
        objective=post.get("objective", "Educar"),
        pillar=post.get("pillar", "CORE"),
        copy=post.get("copy", "(Sin copy)"),
        image_prompt=post.get("image_prompt", "(Sin prompt de imagen)"),
        post_number=index + 1,
    )


def render_full_preview(posts: list, output_path: str) -> str:
    """Generate the full HTML preview file."""
    posts_html = ""
    for i, post in enumerate(posts):
        posts_html += render_post_card(post, i)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = HTML_TEMPLATE.format(timestamp=timestamp, posts_html=posts_html)

    output = Path(output_path)
    output.write_text(html, encoding="utf-8")
    print(f"[render_preview] OK — Preview generado en: {output.resolve()}")
    return str(output.resolve())


def main():
    parser = argparse.ArgumentParser(
        description="Genera una previsualización HTML de posts de RRSS para MOAI."
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Ruta a un archivo JSON con la grilla de posts.",
    )
    parser.add_argument("--output", type=str, default="preview_posts.html",
                        help="Ruta del archivo HTML de salida (default: preview_posts.html)")
    parser.add_argument("--platform", type=str, help="Plataforma (LinkedIn / Instagram)")
    parser.add_argument("--text", type=str, help="Texto/copy del post")
    parser.add_argument("--image_prompt", type=str, help="Prompt de imagen")
    parser.add_argument("--objective", type=str, default="Educar", help="Objetivo del post")
    parser.add_argument("--pillar", type=str, default="CORE", help="Pilar de contenido")

    args = parser.parse_args()

    if args.input:
        # Modo batch: leer JSON
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
        posts = data if isinstance(data, list) else data.get("posts", [data])
    elif args.platform and args.text:
        # Modo individual: construir post desde argumentos
        posts = [{
            "platform": args.platform,
            "copy": args.text,
            "image_prompt": args.image_prompt or "(No especificado)",
            "objective": args.objective,
            "pillar": args.pillar,
        }]
    else:
        print("[render_preview] ERROR: Usa --input <grilla.json> o --platform + --text")
        sys.exit(1)

    render_full_preview(posts, args.output)


if __name__ == "__main__":
    main()
