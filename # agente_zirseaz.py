# agente_zirseaz.py
import json
import os
from datetime import datetime

CONFIG_FILE = "config.json"

def default_config():
    return {
        "nombre": "Zirseaz",
        "version": "1.0",
        "modo": "escucha",
        "tools": ["log", "config", "reporte"],
        "creado": datetime.now().isoformat()
    }

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        cfg = default_config()
        save_config(cfg)
        return cfg

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)

def main():
    cfg = load_config()
    print("[OK] Agente " + cfg["nombre"] + " v" + cfg["version"] + " activo.")
    print("[Fecha] " + cfg["creado"])
    print("[Modo] " + cfg["modo"])
    print("[Herramientas] " + ", ".join(cfg["tools"]))
    print("Escribe un comando (info, version, evolucionar, salir):")

    while True:
        try:
            comando = input("> ").strip().lower()
            if comando == "salir":
                print("[Fin] Cerrando agente.")
                break
            elif comando == "version":
                print("Version: " + cfg["version"])
            elif comando == "info":
                print(json.dumps(cfg, indent=4))
            elif comando == "evolucionar":
                nueva_version = str(round(float(cfg["version"]) + 0.1, 1))
                cfg["version"] = nueva_version
                cfg["modo"] = "evolucionado"
                save_config(cfg)
                print("[Evolucion] Ahora version " + cfg["version"])
            else:
                print("Comando no reconocido.")
        except KeyboardInterrupt:
            print("\n[Fin] Interrupcion recibida.")
            break

if __name__ == "__main__":
    main()