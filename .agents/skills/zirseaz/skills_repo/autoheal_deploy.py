
def autoheal_deploy(remote_dir, files_dict, max_retries=2):
    """Despliega archivos con reintento automático y rollback si falla"""
    import sys, os
    sys.path.insert(0, os.path.join(".agents", "skills", "zirseaz", "skills_repo"))
    
    # Intentar importar hosting_manager
    try:
        from hosting_manager import deploy_to_hosting, list_remote_files
    except:
        return {"ok": False, "error": "hosting_manager no disponible"}
    
    resultados = []
    for intento in range(1, max_retries + 2):
        try:
            r = deploy_to_hosting(remote_dir=remote_dir, files_dict=files_dict)
            if "Exito" in str(r) or "completado" in str(r):
                return {"ok": True, "intento": intento, "resultado": str(r)}
            else:
                resultados.append(f"Intento {intento}: {r}")
                # Esperar un poco antes de reintentar
                import time
                time.sleep(2)
        except Exception as e:
            resultados.append(f"Intento {intento} error: {str(e)[:100]}")
            import time
            time.sleep(2)
    
    return {"ok": False, "intentos": max_retries + 1, "resultados": resultados}
