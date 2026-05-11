#!/usr/bin/env python3
"""
n8n_integrator.py — Puente entre Antigravity MAMM y n8n + Telegram.

Acciones disponibles:
  --action notify   → Envía notificación por Telegram al humano con link al preview.
  --action publish  → Dispara el webhook de n8n para publicar el post aprobado.
  --action image    → Dispara el flujo "Nano Banana" en n8n para generar la imagen.

Configuración:
  Las credenciales se leen de variables de entorno o de un archivo .env en el workspace.
  
  Variables requeridas:
    TELEGRAM_BOT_TOKEN   — Token del bot de Telegram (@BotFather)
    TELEGRAM_CHAT_ID     — Chat ID numérico del destinatario
    N8N_WEBHOOK_PUBLISH  — URL del webhook de n8n para publicar posts
    N8N_WEBHOOK_IMAGE    — URL del webhook de n8n para generar imágenes (Nano Banana)

Uso:
    python n8n_integrator.py --action notify --message "Grilla lista para revisión"
    python n8n_integrator.py --action publish --input grilla_aprobada.json
    python n8n_integrator.py --action image --prompt "A futuristic AI robot..." --output imagen_post1.png
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="[MAMM-n8n] %(asctime)s %(levelname)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("n8n_integrator")

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

def load_env():
    """Carga variables desde .env buscando hacia arriba desde la ubicación del script."""
    # Walk up from this file's location until we find a .env
    current = Path(__file__).resolve().parent
    for _ in range(6):  # max 6 levels up
        candidate = current / ".env"
        if candidate.exists():
            for line in candidate.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
            return
        current = current.parent


def get_config():
    """Lee las credenciales del entorno."""
    load_env()
    return {
        "telegram_token": os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        "telegram_chat_id": os.environ.get("TELEGRAM_CHAT_ID", ""),
        "n8n_publish": os.environ.get("N8N_WEBHOOK_PUBLISH", ""),
        "n8n_image": os.environ.get("N8N_WEBHOOK_IMAGE", ""),
    }


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------

def send_telegram(token: str, chat_id: str, message: str) -> bool:
    """Envía un mensaje de texto por Telegram."""
    if not token or not chat_id:
        log.warning("⚠️  TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no configurados.")
        log.info("---> MOCK Telegram: se habría enviado el siguiente mensaje:")
        log.info(f"     {message}")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            log.info(f"✅ Telegram enviado (HTTP {resp.getcode()})")
            return True
    except urllib.error.URLError as e:
        log.error(f"❌ Error Telegram: {e}")
        return False


# ---------------------------------------------------------------------------
# n8n Webhooks
# ---------------------------------------------------------------------------

def trigger_n8n(webhook_url: str, payload: dict, action_label: str) -> dict:
    """Dispara un webhook de n8n con un payload JSON."""
    if not webhook_url:
        log.warning(f"⚠️  Webhook URL para '{action_label}' no configurada.")
        log.info(f"---> MOCK n8n ({action_label}): payload que se habría enviado:")
        log.info(json.dumps(payload, indent=2, ensure_ascii=False))
        return {"status": "mock", "message": f"Webhook '{action_label}' no configurado. Ejecución simulada."}

    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=encoded,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            log.info(f"✅ n8n ({action_label}) respondió HTTP {resp.getcode()}")
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return {"status": "success", "raw": body}
    except urllib.error.URLError as e:
        log.error(f"❌ Error n8n ({action_label}): {e}")
        return {"status": "error", "error": str(e)}


# ---------------------------------------------------------------------------
# Acciones
# ---------------------------------------------------------------------------

def action_notify(args, cfg):
    """Envía notificación por Telegram."""
    message = args.message or "📋 <b>MAMM — Grilla lista para revisión</b>\n\nRevisa el preview en Antigravity y responde 'OK' para publicar."
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    full_message = f"{message}\n\n🕐 {timestamp}\n🤖 Generado por MAMM (MO-AI.CL)"

    success = send_telegram(cfg["telegram_token"], cfg["telegram_chat_id"], full_message)
    if success:
        log.info("Notificación enviada exitosamente.")
    else:
        log.info("Notificación simulada (sin credenciales TG configuradas).")


def action_publish(args, cfg):
    """Dispara la publicación vía n8n."""
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
        posts = data if isinstance(data, list) else data.get("posts", [data])
    elif args.platform and args.text:
        posts = [{
            "platform": args.platform,
            "copy": args.text,
            "image_url": args.image_url or "",
        }]
    else:
        log.error("Se requiere --input <archivo.json> o --platform + --text")
        sys.exit(1)

    for i, post in enumerate(posts):
        log.info(f"📡 Publicando post {i+1}/{len(posts)} en {post.get('platform', '?')}...")
        payload = {
            "action": "PUBLISH",
            "platform": post.get("platform", "linkedin"),
            "content_text": post.get("copy", ""),
            "image_url": post.get("image_url", ""),
            "human_validated": True,
            "timestamp": datetime.now().isoformat(),
            "source": "MAMM-Antigravity",
        }
        result = trigger_n8n(cfg["n8n_publish"], payload, f"publish-{post.get('platform','')}")
        log.info(f"   Resultado: {json.dumps(result, ensure_ascii=False)}")


def action_image(args, cfg):
    """Dispara la generación de imagen vía n8n (Nano Banana)."""
    if not args.prompt:
        log.error("Se requiere --prompt para generar imagen.")
        sys.exit(1)

    payload = {
        "action": "GENERATE_IMAGE",
        "prompt": args.prompt,
        "style": args.style or "modern_digital_art",
        "output_filename": args.output or "generated_image.png",
        "save_to_drive": True,
        "timestamp": datetime.now().isoformat(),
        "source": "MAMM-Antigravity",
    }

    log.info(f"🎨 Generando imagen con Nano Banana...")
    log.info(f"   Prompt: {args.prompt[:80]}...")
    result = trigger_n8n(cfg["n8n_image"], payload, "nano-banana-image")
    log.info(f"   Resultado: {json.dumps(result, ensure_ascii=False)}")
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="MAMM — Puente Antigravity ↔ n8n + Telegram"
    )
    parser.add_argument(
        "--action",
        type=str,
        required=True,
        choices=["notify", "publish", "image"],
        help="Acción a ejecutar.",
    )
    parser.add_argument("--message", type=str, help="Mensaje para Telegram (acción 'notify').")
    parser.add_argument("--input", type=str, help="Archivo JSON con posts (acción 'publish').")
    parser.add_argument("--platform", type=str, help="Plataforma destino.")
    parser.add_argument("--text", type=str, help="Copy del post.")
    parser.add_argument("--image_url", type=str, help="URL de la imagen ya generada.")
    parser.add_argument("--prompt", type=str, help="Prompt de imagen (acción 'image').")
    parser.add_argument("--style", type=str, default="modern_digital_art",
                        help="Estilo visual (default: modern_digital_art).")
    parser.add_argument("--output", type=str, help="Nombre del archivo de imagen de salida.")

    args = parser.parse_args()
    cfg = get_config()

    actions = {
        "notify": action_notify,
        "publish": action_publish,
        "image": action_image,
    }

    actions[args.action](args, cfg)


if __name__ == "__main__":
    main()
