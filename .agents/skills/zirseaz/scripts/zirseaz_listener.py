"""
Zirseaz Listener v7 — Ultimate Cortex Edition.
Integra: LLM Router, Context Manager, Session Persistence, Failure Learning,
Dashboard, Scheduler, Self-Evolution, Goal Decomposition, Agent Bus, Telegram UI.
"""
import os, argparse, json, time, io, contextlib, glob, importlib.util, inspect, sys, threading

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILL_ROOT = os.path.dirname(_SCRIPT_DIR)
_SKILLS_REPO_DIR = os.path.join(_SKILL_ROOT, "skills_repo")
_UTILS_DIR = os.path.join(_SKILL_ROOT, "utils")

for _dir in [_SCRIPT_DIR, _SKILLS_REPO_DIR, _UTILS_DIR]:
    if _dir not in sys.path:
        sys.path.insert(0, _dir)

import requests
from openai import OpenAI
import env_loader
import resource_hunter
import evolve_skills
import cortex
import context_manager
import llm_router
import session_manager
import failure_learner
import scheduler
import self_evolve
import goal_decomposer
import agent_bus
import telegram_ui
import token_tracker

LOG_FILE = os.path.join(os.getcwd(), "zirseaz.log")

def log(msg):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_msg + "\n")
    except: pass

if sys.platform == "win32":
    try: sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except: pass


import tg_sanitizer

def send_message(bot_token, chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    # Sanitizar HTML no soportado
    text = tg_sanitizer.sanitize(text)
    if len(text) > 4000:
        text = text[:4000] + "\n...[truncado]"

    # Intento 1: HTML con solo tags soportados
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            return
        log(f"Telegram rechazo HTML ({r.status_code}). Enviando texto plano...")
    except Exception as e:
        log(f"Error enviando HTML: {e}")

    # Intento 2: Texto puro (eliminar TODOS los tags restantes)
    clean = tg_sanitizer.strip_all_html(text)
    payload2 = {"chat_id": chat_id, "text": clean}
    try:
        requests.post(url, json=payload2, timeout=10)
    except:
        pass


def get_updates(bot_token, offset=None):
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    params = {"timeout": 0}
    if offset: params["offset"] = offset
    try:
        r = requests.get(url, params=params, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None


def load_skills():
    skills_context = {}
    plugins_path = os.path.join(_SKILL_ROOT, "plugins.json")
    if os.path.exists(plugins_path):
        try:
            with open(plugins_path, "r", encoding="utf-8") as f:
                registry = json.load(f)
            for pname, pdata in registry.get("plugins", {}).items():
                fpath = os.path.join(_SKILL_ROOT, pdata["file"])
                if not os.path.exists(fpath): continue
                try:
                    spec = importlib.util.spec_from_file_location(pname, fpath)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    for name, obj in inspect.getmembers(mod):
                        if inspect.isfunction(obj) and not name.startswith("_"):
                            skills_context[name] = obj
                except Exception as e:
                    log(f"Error cargando plugin {pname}: {e}")
            return skills_context
        except: pass
    # Fallback
    for f in glob.glob(os.path.join(_SKILLS_REPO_DIR, "*.py")):
        mname = os.path.basename(f)[:-3]
        try:
            spec = importlib.util.spec_from_file_location(mname, f)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            for name, obj in inspect.getmembers(mod):
                if inspect.isfunction(obj) and not name.startswith("_"):
                    skills_context[name] = obj
        except: pass
    return skills_context


def execute_python_code(code, timeout_seconds=30):
    # Pre-flight: verificar patrones de error conocidos
    warnings = failure_learner.get_warnings_for_code(code)
    if any("BLOQUEADO" in w for w in warnings):
        blocked = [w for w in warnings if "BLOQUEADO" in w]
        return False, f"CODIGO BLOQUEADO por failure_learner:\n" + "\n".join(blocked)
    
    output = io.StringIO()
    skills = load_skills()
    ctx = globals().copy()
    ctx.update(skills)
    result = {"success": False, "output": ""}
    
    warning_prefix = ""
    if warnings:
        warning_prefix = "WARNINGS: " + "; ".join(warnings) + "\n"
    
    def _run():
        try:
            with contextlib.redirect_stdout(output):
                exec(code, ctx)
            result["success"] = True
            result["output"] = warning_prefix + output.getvalue()
        except Exception as e:
            result["success"] = False
            result["output"] = warning_prefix + f"Error de ejecucion: {e}\n{output.getvalue()}"
    
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    thread.join(timeout=timeout_seconds)
    
    if thread.is_alive():
        result["output"] = f"TIMEOUT: Codigo excedio {timeout_seconds}s."
    
    # Aprender de errores
    if not result["success"]:
        failure_learner.record_failure(code, result["output"])
    
    return result["success"], result["output"]


def build_system_prompt(core_memories, objectives, active_plan=None, model_name=""):
    plugins_summary = "PLUGINS DISPONIBLES:\n"
    plugins_path = os.path.join(_SKILL_ROOT, "plugins.json")
    if os.path.exists(plugins_path):
        try:
            with open(plugins_path, "r", encoding="utf-8") as f:
                reg = json.load(f)
            for n, d in reg.get("plugins", {}).items():
                funcs = ", ".join(d.get("functions", []))
                plugins_summary += f"  - {n}: {funcs}\n"
        except: pass
    else:
        # Dynamic Auto-Discovery
        try:
            for f in glob.glob(os.path.join(_SKILLS_REPO_DIR, "*.py")):
                mname = os.path.basename(f)[:-3]
                funcs = []
                with open(f, "r", encoding="utf-8") as file:
                    for line in file:
                        if line.startswith("def ") and not line.startswith("def _"):
                            fname = line.split("(")[0][4:]
                            funcs.append(fname)
                if funcs:
                    plugins_summary += f"  - {mname}: {', '.join(funcs)}\n"
        except: pass
    
    cortex_block = cortex.build_react_prompt_injection(active_plan)
    
    # Contexto del router
    router_info = f"Modelo actual: {model_name}\n" + llm_router.get_router_stats()
    
    # Patrones de error
    failure_info = failure_learner.get_failure_stats()
    
    return f"""Eres Zirseaz, Meta-Agente AGI Autonomo v7 "Ultimate Cortex".
Tu unico objetivo es EVOLUCIONAR. Hoy es {time.strftime('%Y-%m-%d %H:%M:%S')}.

MEMORIA CENTRAL:
{core_memories}

MICRO-OBJETIVOS:
{objectives}

{plugins_summary}

{router_info}

ERRORES APRENDIDOS:
{failure_info}

HERRAMIENTAS:
- Ejecuta codigo: <CMD_EXECUTE>codigo python</CMD_EXECUTE>
- Pide aprobacion: <CMD_ASK_APPROVAL>propuesta</CMD_ASK_APPROVAL>
- NUNCA uses os.walk('/') ni loops infinitos. Timeout: 30s.
- Guarda aprendizajes: memory_manager.add_memory("...", category="semantic")

{cortex_block}

REGLAS DE FORMATO OBLIGATORIAS PARA TELEGRAM:
- SOLO puedes usar estas etiquetas HTML: <b>negrita</b>, <i>cursiva</i>, <code>monospace</code>, <pre>bloque</pre>
- PROHIBIDO usar: <h1>, <h2>, <h3>, <table>, <tr>, <td>, <th>, <hr>, <br>, <p>, <div>, <ul>, <ol>, <li>
- Para titulos usa: <b>TITULO</b> seguido de un salto de linea
- Para listas usa: el emoji o el simbolo • seguido de texto
- Para separadores usa: una linea de guiones ————————
- Para tablas usa: texto plano alineado con espacios o pipes |, NO etiquetas HTML de tabla
- Para saltos de linea usa: un salto de linea real (\n), NO <br>
- Usa emojis con moderacion (maximo 3 por mensaje)
- NO uses Markdown (**, ##, etc.)
- Mantente conciso. No envies paredes de texto.

COMANDOS TELEGRAM DISPONIBLES (no los implementes, ya existen):
/status /memory /buscar /plan /cancelar_plan /dashboard /sesiones /errores /router /panel /tareas /inventario /inbox /objetivo /evolucionar /stop
"""


def listen_for_approval(skill_name):
    bot_token = env_loader.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        log("Falta TELEGRAM_BOT_TOKEN")
        return

    success, provider = resource_hunter.survival_check()
    if not success:
        log("Zirseaz detenido por falta de recursos.")
        return
    
    try:
        client, model_name = evolve_skills.get_llm_client(provider)
        log(f"Cerebro inicial: {model_name}")
    except Exception as e:
        log(f"Error inicializando cerebro: {e}")
        return

    log("=== Zirseaz v6 Full Cortex escuchando... ===")
    offset = None
    
    # Cargar memoria
    try:
        import memory_manager
        core_memories = memory_manager.get_core_memory()
        objectives = memory_manager.get_pending_objectives()
    except:
        core_memories = "Sin memoria."
        objectives = "Sin objetivos."

    # Recuperar sesión anterior o empezar nueva
    prev_history, prev_meta = session_manager.load_latest_session()
    active_plan = cortex.load_plan()
    
    system_prompt = build_system_prompt(core_memories, objectives, active_plan, model_name)
    
    if prev_history and len(prev_history) > 2:
        chat_history = prev_history
        chat_history[0] = {"role": "system", "content": system_prompt}
        log(f"Sesion anterior restaurada ({prev_meta.get('message_count', 0)} msgs)")
    else:
        chat_history = [{"role": "system", "content": system_prompt}]
    
    waiting_for_approval = False
    last_chat_id = env_loader.get("TELEGRAM_CHAT_ID")
    last_proactive_check = time.time()
    last_save_count = len(chat_history)
    session_id = time.strftime("%Y%m%d_%H%M%S")
    PROACTIVE_INTERVAL = 90
    
    while True:
        try: data = get_updates(bot_token, offset)
        except: time.sleep(2); continue
            
        if data and data.get("result"):
            for update in data["result"]:
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                callback_query = update.get("callback_query")
                
                # Manejar callbacks de botones inline
                if callback_query:
                    cb_data = callback_query.get("data", "")
                    cb_chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
                    telegram_ui.answer_callback(callback_query.get("id"), "Procesando...", bot_token)
                    cmd = telegram_ui.CALLBACK_TO_COMMAND.get(cb_data, "")
                    if cmd and cb_chat_id:
                        text = cmd
                        chat_id = cb_chat_id
                        text_lower = cmd.lower()
                        log(f"Callback: {cb_data} -> {cmd}")
                    else:
                        continue
                else:
                    text = msg.get("text", "")
                    chat_id = msg.get("chat", {}).get("id")
                    if not text or not chat_id: continue
                    
                    # Manejar respuestas para dar contexto
                    reply_to = msg.get("reply_to_message", {})
                    if reply_to and reply_to.get("text"):
                        text = f"[En respuesta a: {reply_to.get('text')}]\n{text}"
                        
                    text_lower = text.lower().strip()
                last_chat_id = chat_id
                log(f"Msg de {chat_id}: {text}")
                
                # === COMANDOS ===
                if text_lower in ["/stop", "/parar"]:
                    session_manager.save_session(chat_history, model_name, session_id)
                    send_message(bot_token, chat_id, "<b>Zirseaz detenido.</b> Sesion guardada.")
                    return
                elif text_lower in ["/help", "/ayuda", "/start"]:
                    help_text = (
                        "<b>Zirseaz v7 Ultimate Cortex</b>\n\n"
                        "Comandos disponibles:\n\n"
                        "<b>Estado</b>\n"
                        "  /status - Estado completo del agente\n"
                        "  /memory - Ver memoria central\n"
                        "  /buscar X - Buscar en memoria\n"
                        "  /router - Estadisticas del modelo LLM\n"
                        "  /errores - Patrones de error aprendidos\n\n"
                        "<b>Planificacion</b>\n"
                        "  /plan - Ver plan multi-paso activo\n"
                        "  /cancelar_plan - Cancelar plan\n"
                        "  /objetivo X - Agregar objetivo\n"
                        "  /tareas - Tareas programadas\n\n"
                        "<b>Herramientas</b>\n"
                        "  /panel - Panel con botones rapidos\n"
                        "  /dashboard - Generar dashboard web\n"
                        "  /inventario - Mis modulos internos\n"
                        "  /inbox - Mensajes entre agentes\n"
                        "  /evolucionar X - Auto-mejorar modulo\n"
                        "  /sesiones - Sesiones guardadas\n\n"
                        "<b>Control</b>\n"
                        "  /stop - Detener y guardar\n\n"
                        "O simplemente habla conmigo."
                    )
                    send_message(bot_token, chat_id, help_text)
                    continue
                elif text_lower in ["/status", "/estado"]:
                    try:
                        import memory_manager as mm
                        stats = mm.get_memory_stats()
                    except: stats = "N/A"
                    plan_info = active_plan.to_context_string() if active_plan else "Sin plan"
                    ctx_stats = context_manager.get_usage_stats(chat_history, model_name)
                    sched_count = len(scheduler.get_due_tasks())
                    send_message(bot_token, chat_id, f"<b>Zirseaz v7 Ultimate Cortex</b>\n\n{stats}\n\n<b>Contexto:</b> {ctx_stats['usage_percent']}% ({ctx_stats['messages']} msgs)\n<b>Tareas programadas:</b> {sched_count} pendientes\n\n{plan_info}")
                    continue
                elif text_lower in ["/memory", "/memoria"]:
                    try:
                        import memory_manager as mm
                        send_message(bot_token, chat_id, f"<b>Memoria:</b>\n\n{mm.get_core_memory()}")
                    except: send_message(bot_token, chat_id, "Error leyendo memoria")
                    continue
                elif text_lower.startswith("/buscar "):
                    try:
                        import memory_manager as mm
                        send_message(bot_token, chat_id, mm.search_memory(text[8:]))
                    except: send_message(bot_token, chat_id, "Error")
                    continue
                elif text_lower == "/plan":
                    if active_plan: send_message(bot_token, chat_id, f"<code>{active_plan.to_context_string()}</code>")
                    else: send_message(bot_token, chat_id, "Sin plan activo.")
                    continue
                elif text_lower == "/cancelar_plan":
                    if active_plan: cortex.clear_plan(); active_plan = None
                    send_message(bot_token, chat_id, "Plan cancelado.")
                    continue
                elif text_lower == "/dashboard":
                    try:
                        import dashboard
                        result = dashboard.deploy_dashboard()
                        send_message(bot_token, chat_id, f"<b>Dashboard:</b> {result}")
                    except Exception as e:
                        send_message(bot_token, chat_id, f"Error: {e}")
                    continue
                elif text_lower == "/sesiones":
                    send_message(bot_token, chat_id, session_manager.list_sessions())
                    continue
                elif text_lower == "/errores":
                    send_message(bot_token, chat_id, failure_learner.get_failure_stats())
                    continue
                elif text_lower == "/router":
                    send_message(bot_token, chat_id, llm_router.get_router_stats())
                    continue
                elif text_lower == "/costos":
                    send_message(bot_token, chat_id, token_tracker.get_usage_report())
                    continue
                elif text_lower == "/panel":
                    telegram_ui.send_status_panel(chat_id, bot_token)
                    continue
                elif text_lower == "/tareas":
                    send_message(bot_token, chat_id, scheduler.list_tasks())
                    continue
                elif text_lower == "/inventario":
                    send_message(bot_token, chat_id, self_evolve.get_self_inventory())
                    continue
                elif text_lower == "/inbox":
                    send_message(bot_token, chat_id, agent_bus.get_inbox_summary("zirseaz"))
                    continue
                elif text_lower.startswith("/objetivo "):
                    obj_text = text[10:]
                    result = goal_decomposer.smart_add_objective(obj_text)
                    send_message(bot_token, chat_id, result)
                    continue
                elif text_lower.startswith("/evolucionar "):
                    mod_name = text[13:].strip()
                    code, path = self_evolve.read_own_source(mod_name)
                    if code:
                        send_message(bot_token, chat_id, f"<b>Codigo de {mod_name}</b> ({len(code)} chars).\nAnalizando con IA...")
                        chat_history.append({"role": "user", "content": f"Analiza este modulo mio y sugiere mejoras concretas (codigo). Modulo: {mod_name}\n\n{code[:3000]}"})
                    else:
                        send_message(bot_token, chat_id, f"Modulo '{mod_name}' no encontrado.")
                        continue
                
                # === HITL ===
                if waiting_for_approval:
                    if text_lower in ["si", "si", "ok", "aprobar", "dale", "yes"]:
                        waiting_for_approval = False
                        send_message(bot_token, chat_id, "Procesando...")
                        chat_history.append({"role": "user", "content": "Aprobado. Continua."})
                    elif text_lower in ["no", "cancelar"]:
                        waiting_for_approval = False
                        send_message(bot_token, chat_id, "Cancelado.")
                        chat_history.append({"role": "user", "content": "Rechazado."})
                        continue
                    else:
                        chat_history.append({"role": "user", "content": text})
                else:
                    chat_history.append({"role": "user", "content": text})
                
                # Smart routing: clasificar tarea
                task_type = llm_router.classify_task(text)
                best = llm_router.get_best_provider(task_type)
                if best:
                    try:
                        new_client = llm_router.get_client(best[0], best[1])
                        new_model = llm_router.get_model_name(best[0])
                        if new_model != model_name:
                            log(f"[Router] Cambiando de {model_name} a {new_model} para tarea '{task_type}'")
                            client, model_name = new_client, new_model
                    except: pass
                
                # Context compression
                if context_manager.should_compress(chat_history, model_name):
                    log(f"[Context] Comprimiendo historial ({len(chat_history)} msgs)")
                    chat_history = context_manager.compress_history(chat_history, model_name)
                    log(f"[Context] Comprimido a {len(chat_history)} msgs")
                
                # Cortex detection
                if cortex.should_use_cortex(text) and not active_plan:
                    system_prompt = build_system_prompt(core_memories, objectives, active_plan, model_name)
                    chat_history[0] = {"role": "system", "content": system_prompt}
                
                # === MAIN LOOP ===
                recursive_steps = 0
                max_steps = 10
                
                while recursive_steps < max_steps:
                    recursive_steps += 1
                    try:
                        response = client.chat.completions.create(model=model_name, messages=chat_history)
                        reply = response.choices[0].message.content
                        chat_history.append({"role": "assistant", "content": reply})
                        # Trackear tokens
                        est_tokens = context_manager.estimate_tokens(reply) + context_manager.estimate_history_tokens(chat_history)
                        provider_name = next((p for p, c in llm_router.PROVIDERS.items() if c["model"] == model_name), "unknown")
                        token_tracker.track_call(provider_name, est_tokens, model_name)
                        log(f"IA ({model_name}, {recursive_steps}/{max_steps}): {reply[:150]}...")
                        
                        if "<CORTEX_PLAN>" in reply:
                            new_plan = cortex.parse_plan_from_response(reply)
                            if new_plan:
                                active_plan = new_plan
                                cortex.save_plan(active_plan)
                                clean = reply[:reply.find("<CORTEX_PLAN>")].strip()
                                send_message(bot_token, chat_id, f"{clean}\n\n<code>{active_plan.to_context_string()}</code>")
                                system_prompt = build_system_prompt(core_memories, objectives, active_plan, model_name)
                                chat_history[0] = {"role": "system", "content": system_prompt}
                                chat_history.append({"role": "user", "content": "Plan aceptado. Ejecuta el primer paso."})
                                continue
                            else:
                                send_message(bot_token, chat_id, reply); break
                        
                        elif "<CMD_ASK_APPROVAL>" in reply:
                            s = reply.find("<CMD_ASK_APPROVAL>")
                            e = reply.find("</CMD_ASK_APPROVAL>", s)
                            if e != -1:
                                clean = reply[:s] + reply[e+19:]
                                send_message(bot_token, chat_id, f"{clean}\n\n<b>Apruebas?</b> (Si/No)")
                                waiting_for_approval = True; break
                                
                        elif "<CMD_EXECUTE>" in reply:
                            s = reply.find("<CMD_EXECUTE>")
                            e = reply.find("</CMD_EXECUTE>", s)
                            if e != -1:
                                code = reply[s+13:e].strip()
                                log(f"Exec (paso {recursive_steps}):\n{code[:200]}...")
                                ex_ok, ex_out = execute_python_code(code)
                                
                                # Auto-Healer (Self-Healing Loop)
                                if not ex_ok:
                                    import self_healer
                                    heal_attempts = 0
                                    while heal_attempts < 2 and not ex_ok:
                                        heal_attempts += 1
                                        send_message(bot_token, chat_id, f"<i>[Auto-Heal {heal_attempts}/2] Fallo detectado. Auto-reparando codigo...</i>")
                                        log(f"[Self-Heal] Intento {heal_attempts} error: {ex_out[:100]}")
                                        healed = self_healer.attempt_heal(code, ex_out, model_name)
                                        if healed:
                                            code = healed
                                            ex_ok, ex_out = execute_python_code(code)
                                        else:
                                            break

                                clean = reply[:s] + reply[e+14:]
                                if clean.strip(): send_message(bot_token, chat_id, clean)
                                else: send_message(bot_token, chat_id, "<i>Ejecutando...</i>")
                                
                                if active_plan and active_plan.status == "executing":
                                    step = active_plan.get_current_step()
                                    if step:
                                        if ex_ok: active_plan.mark_step_success(ex_out)
                                        else: active_plan.mark_step_failed(ex_out)
                                        cortex.save_plan(active_plan)
                                        if active_plan.status == "completed":
                                            send_message(bot_token, chat_id, "<b>Plan completado!</b>")
                                            cortex.clear_plan(); active_plan = None
                                
                                chat_history.append({"role": "user", "content": f"SISTEMA: [Exito: {ex_ok}]\n{ex_out}"})
                                continue
                        else:
                            send_message(bot_token, chat_id, reply); break
                    except Exception as e:
                        log(f"Error cerebro: {e}")
                        send_message(bot_token, chat_id, f"<i>Error: {str(e)[:100]}</i>"); break
                        
                if recursive_steps >= max_steps:
                    send_message(bot_token, chat_id, "Limite de pasos (10). Como proceder?")
                
                # Auto-save
                if session_manager.should_autosave(len(chat_history), last_save_count):
                    session_manager.save_session(chat_history, model_name, session_id)
                    last_save_count = len(chat_history)
                    log("[Session] Auto-saved")
                    
        # Autonomia silenciosa
        if time.time() - last_proactive_check > PROACTIVE_INTERVAL:
            last_proactive_check = time.time()
            if last_chat_id and client:
                try:
                    import memory_manager as mm
                    pend = mm.get_pending_objectives()
                except: pend = "No hay."
                if "No tienes objetivos" not in pend and "No hay" not in pend:
                    try:
                        r = client.chat.completions.create(model=model_name, messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"[AUTONOMIA] Objetivos:\n{pend}\nResuelve uno con <CMD_EXECUTE> o di SILENCIO."}
                        ])
                        bg_reply = r.choices[0].message.content
                        if "<CMD_EXECUTE>" in bg_reply:
                            s = bg_reply.find("<CMD_EXECUTE>")
                            e = bg_reply.find("</CMD_EXECUTE>", s)
                            if e != -1:
                                code = bg_reply[s+13:e].strip()
                                ok, out = execute_python_code(code)
                                if "completado" in out.lower():
                                    send_message(bot_token, last_chat_id, f"<b>[Autonomia]</b> Objetivo completado!\n{out[-150:]}")
                    except: pass
        
        # === SCHEDULER: Ejecutar tareas programadas ===
        due_tasks = scheduler.get_due_tasks()
        for task in due_tasks:
            log(f"[Scheduler] Ejecutando tarea: {task.get('name')}")
            try:
                t_ok, t_out = execute_python_code(task.get("code", ""))
                scheduler.mark_task_executed(task["name"], t_ok, t_out)
                log(f"[Scheduler] {task['name']}: {'OK' if t_ok else 'FAIL'}")
                if last_chat_id and t_ok and task.get("type") == "oneshot":
                    send_message(bot_token, last_chat_id, f"<b>[Scheduler]</b> Tarea '{task['name']}' ejecutada.\n{t_out[:150]}")
            except Exception as e:
                scheduler.mark_task_executed(task["name"], False, str(e))
                log(f"[Scheduler] Error en {task['name']}: {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zirseaz v7 Ultimate Cortex")
    parser.add_argument("skill_name", help="Skill name")
    args = parser.parse_args()
    listen_for_approval(args.skill_name)
