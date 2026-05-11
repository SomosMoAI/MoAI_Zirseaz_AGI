"""
Zirseaz Token Tracker — Monitorea costos de API y uso de tokens.

Trackea:
- Llamadas por proveedor
- Tokens estimados consumidos
- Costo estimado en USD
- Historial diario
"""
import os, json, time

STATE_DIR = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz", "state")
TRACKER_FILE = os.path.join(STATE_DIR, "token_usage.json")

# Precios estimados por 1M tokens (input)
PRICES_PER_M = {
    "groq": 0.0,          # Gratis
    "deepseek": 0.14,     # $0.14/M input
    "gemini": 0.0,        # Free tier
    "gpt-3.5-turbo": 0.5,
    "gpt-4": 30.0,
}


def _load_data():
    if not os.path.exists(TRACKER_FILE):
        return {"daily": {}, "totals": {"calls": 0, "tokens": 0, "cost_usd": 0.0}}
    try:
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"daily": {}, "totals": {"calls": 0, "tokens": 0, "cost_usd": 0.0}}


def _save_data(data):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def track_call(provider, tokens_estimated, model_name=""):
    """Registra una llamada a la API."""
    data = _load_data()
    today = time.strftime("%Y-%m-%d")
    
    if today not in data["daily"]:
        data["daily"][today] = {"calls": 0, "tokens": 0, "cost_usd": 0.0, "by_provider": {}}
    
    price = PRICES_PER_M.get(provider, 0.5)
    cost = (tokens_estimated / 1_000_000) * price
    
    data["daily"][today]["calls"] += 1
    data["daily"][today]["tokens"] += tokens_estimated
    data["daily"][today]["cost_usd"] += cost
    
    if provider not in data["daily"][today]["by_provider"]:
        data["daily"][today]["by_provider"][provider] = {"calls": 0, "tokens": 0}
    data["daily"][today]["by_provider"][provider]["calls"] += 1
    data["daily"][today]["by_provider"][provider]["tokens"] += tokens_estimated
    
    data["totals"]["calls"] += 1
    data["totals"]["tokens"] += tokens_estimated
    data["totals"]["cost_usd"] += cost
    
    # Mantener solo ultimos 30 dias
    dates = sorted(data["daily"].keys())
    if len(dates) > 30:
        for old_date in dates[:-30]:
            del data["daily"][old_date]
    
    _save_data(data)


def get_usage_report():
    """Genera un reporte de uso legible."""
    data = _load_data()
    today = time.strftime("%Y-%m-%d")
    
    lines = ["<b>Uso de API</b>\n"]
    
    # Totales
    t = data["totals"]
    lines.append(f"Total historico: {t['calls']} llamadas, ~{t['tokens']:,} tokens, ~${t['cost_usd']:.4f} USD\n")
    
    # Hoy
    if today in data["daily"]:
        d = data["daily"][today]
        lines.append(f"Hoy ({today}): {d['calls']} llamadas, ~{d['tokens']:,} tokens, ~${d['cost_usd']:.4f} USD")
        for prov, pdata in d.get("by_provider", {}).items():
            price_label = "gratis" if PRICES_PER_M.get(prov, 0) == 0 else f"${PRICES_PER_M.get(prov, 0)}/M"
            lines.append(f"  {prov}: {pdata['calls']} calls ({price_label})")
    else:
        lines.append("Hoy: Sin uso registrado.")
    
    return "\n".join(lines)
