
def backup_sistema():
    """Respaldar todas las skills, memorias y config en un archivo comprimido"""
    import os, json, zipfile
    from datetime import datetime
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre = f"backup_zirseaz_{ts}.zip"
    
    with zipfile.ZipFile(nombre, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Skills
        skills_dir = os.path.join(".agents", "skills", "zirseaz", "skills_repo")
        if os.path.exists(skills_dir):
            for f in os.listdir(skills_dir):
                if f.endswith('.py'):
                    zf.write(os.path.join(skills_dir, f), f"skills/{f}")
        
        # Memoria
        for mem_file in ["memoria_largo_plazo.json", "reglas_aprendidas.json", "operaciones_log.json"]:
            if os.path.exists(mem_file):
                zf.write(mem_file)
        
        # Config
        for cfg in [".env", "plugins.json"]:
            if os.path.exists(cfg):
                zf.write(cfg)
    
    return {"backup": nombre, "tamaño": os.path.getsize(nombre), "ok": True}
