import os
import re
from huggingface_hub import HfApi

def get_env_var(var_name):
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{var_name}="):
                    return line.split("=")[1].strip()
    return None

def deploy():
    token = get_env_var("HUGGINGFACE_TOKEN")
    if not token:
        print("Falta HUGGINGFACE_TOKEN en el .env")
        return
        
    api = HfApi()
    repo_id = "ZirseazAI/Zirseaz"
    
    # 1. Crear y subir requirements.txt
    print("Creando y subiendo requirements.txt...")
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write("openai\nrequests\n")
        
    try:
        api.upload_file(
            path_or_fileobj="requirements.txt",
            path_in_repo="requirements.txt",
            repo_id=repo_id,
            repo_type="space",
            token=token
        )
        print("requirements.txt subido exitosamente.")
        os.remove("requirements.txt")
    except Exception as e:
        print(f"Error al subir requirements.txt: {e}")
        return
        
    # 2. Leer el archivo original y modificarlo
    with open(".agents/skills/zirseaz/scripts/zirseaz_listener.py", "r", encoding="utf-8") as f:
        code = f.read()
        
    main_block = """if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zirseaz Recursive Agent")
    parser.add_argument("skill_name", help="Nombre de la skill a escuchar")
    args = parser.parse_args()
    listen_for_approval(args.skill_name)"""
    
    # También buscamos el bloque del agente modular por si acaso
    main_block_modular = """if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zirseaz Modular Agent")
    parser.add_argument("skill_name", help="Nombre de la skill a escuchar")
    args = parser.parse_args()
    listen_for_approval(args.skill_name)"""
    
    gradio_block = """import threading
import gradio as gr
import os

if __name__ == "__main__":
    # Iniciar el hilo de Telegram en segundo plano
    threading.Thread(target=listen_for_approval, args=("marketing",), daemon=True).start()
    
    def get_logs():
        log_file = os.path.join(os.getcwd(), "zirseaz.log")
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    return content[-5000:] # Devolvemos los ultimos 5000 caracteres
            except Exception as e:
                return f"Error al leer logs: {e}"
        return "No hay archivo de logs todavia o esta vacio."
        
    demo = gr.Interface(fn=get_logs, inputs=[], outputs="text", title="Zirseaz Meta-Agent Logs")
    demo.launch(server_name="0.0.0.0", server_port=7860)
"""

    if main_block in code:
        code = code.replace(main_block, gradio_block)
    elif main_block_modular in code:
        code = code.replace(main_block_modular, gradio_block)
    else:
        # Buscar cualquier bloque if __name__ == "__main__":
        code = re.sub(r'if __name__ == ["\']__main__[\'"]:(.|\n)*$', gradio_block, code)
        
    # Guardar temporalmente como app.py
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(code)
        
    # Subir app.py
    print(f"Subiendo app.py a {repo_id}...")
    try:
        api.upload_file(
            path_or_fileobj="app.py",
            path_in_repo="app.py",
            repo_id=repo_id,
            repo_type="space",
            token=token
        )
        print("[OK] app.py subida.")
        os.remove("app.py")
    except Exception as e:
        print(f"Error al subir app.py: {e}")
        return

    # Subir .env filtrado (sin el token de HF para evitar que sea bloqueado por seguridad)
    print("Subiendo .env filtrado...")
    try:
        with open(".env", "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        # Filtrar TODOS los secretos sensibles para no exponerlos en un Space público
        SENSITIVE_PREFIXES = [
            "HUGGINGFACE_TOKEN=",
            "TELEGRAM_BOT_TOKEN=",
            "TELEGRAM_CHAT_ID=",
            "DEEPSEEK_API_KEY=",
            "GROQ_API_KEY=",
            "GEMINI_API_KEY=",
            "ZIRSEAZ_EMAIL=",
            "ZIRSEAZ_PASSWORD=",
            "HOSTING_HOST=",
            "HOSTING_USER=",
            "HOSTING_PASS=",
            "NEWS_API_KEY=",
        ]
        clean_lines = [
            l for l in lines 
            if not any(l.strip().startswith(prefix) for prefix in SENSITIVE_PREFIXES)
        ]
        
        with open(".env_tmp", "w", encoding="utf-8") as f:
            f.writelines(clean_lines)
            
        api.upload_file(
            path_or_fileobj=".env_tmp",
            path_in_repo=".env",
            repo_id=repo_id,
            repo_type="space",
            token=token
        )
        print("[OK] .env subida (filtrada).")
        os.remove(".env_tmp")
    except Exception as e:
        print(f"Error al subir .env: {e}")

    # 3. Subir la carpeta de habilidades
    print("Subiendo carpeta de habilidades...")
    try:
        api.upload_folder(
            folder_path=".agents/skills/zirseaz/skills_repo",
            path_in_repo="skills_repo",
            repo_id=repo_id,
            repo_type="space",
            token=token
        )
        print("[OK] Carpeta de habilidades subida.")
    except Exception as e:
        print(f"Error al subir carpeta de habilidades: {e}")

if __name__ == "__main__":
    deploy()
