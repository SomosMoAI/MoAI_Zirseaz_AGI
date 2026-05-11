import streamlit as st
import os
import json
from openai import OpenAI

st.set_page_config(page_title="Meta-Agent Builder", page_icon="🤖", layout="wide")

# Leer API key desde el archivo .env
api_key = None
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("DEEPSEEK_API_KEY="):
                api_key = line.split("=")[1].strip()

# Inicializar Cliente de DeepSeek (usando cliente compatible con OpenAI)
client = None
if api_key:
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    except Exception as e:
        st.sidebar.error(f"Error al inicializar cliente: {e}")

st.title("🤖 Meta-Agent Builder")
st.caption("Arquitectura y Despliegue de Agentes de manera Quirúrgica.")

# Inicializar estado de la sesión
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'step' not in st.session_state:
    st.session_state.step = 1 # 1: Pinponeo, 2: Propuesta, 3: Creación

# Escanear stack local
skills = []
if os.path.exists(".agents/skills"):
    skills = os.listdir(".agents/skills")

# Barra lateral con el stack
st.sidebar.title("Tu Stack Actual")
st.sidebar.write("**Skills detectadas:**")
for skill in skills:
    st.sidebar.write(f"- `{skill}`")
st.sidebar.write("**MCPs detectados:**")
st.sidebar.write("- `notebooklm`")

# Paso 1: Pinponeo (Chat)
if st.session_state.step == 1:
    st.subheader("Paso 1: Pinponeo de la Idea")
    st.info("Tira tu idea. Chatearemos para pulirla. Cuando estemos listos, avanzaremos a la arquitectura.")
    
    # Mostrar mensajes del historial
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    # Mensaje inicial si está vacío
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.write("¡Hola! Cuéntame qué idea tienes en mente y la trabajamos juntos.")
            st.session_state.messages.append({"role": "assistant", "content": "¡Hola! Cuéntame qué idea tienes en mente y la trabajamos juntos."})

    # Entrada de chat
    if prompt := st.chat_input("Escribe aquí tu respuesta o idea..."):
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        # Generar respuesta con DeepSeek
        if client:
            with st.spinner("Pensando..."):
                try:
                    # Construir historial para el prompt
                    messages = []
                    system_prompt = f"""Eres el Meta-Agent Builder. Tu objetivo es ayudar al usuario a pulir su idea de automatización antes de crear los agentes.
                    Stack disponible del usuario: Skills: {skills}, MCPs: ['notebooklm'].
                    
                    Instrucciones:
                    1. Pinponea la idea. Haz preguntas para entender el alcance, los triggers (Telegram, Sheets, etc.) y el resultado esperado.
                    2. Sugiere si se puede usar alguna Skill existente o si hay que crear nuevas.
                    3. Mantén la conversación enfocada. Cuando sientas que la idea está madura y el usuario esté de acuerdo, dile EXPLÍCITAMENTE que haga clic en el botón 'Pasar a Propuesta' que aparecerá abajo, o que diga 'OK' para continuar.
                    """
                    messages.append({"role": "system", "content": system_prompt})
                    for m in st.session_state.messages:
                        # Asegurar roles compatibles
                        role = "assistant" if m["role"] == "assistant" else "user"
                        messages.append({"role": role, "content": m["content"]})
                        
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=messages
                    )
                    bot_response = response.choices[0].message.content
                except Exception as e:
                    bot_response = f"Error al generar respuesta: {str(e)}"
        else:
            bot_response = "No se pudo conectar con DeepSeek (falta API Key o error). Modo simulación activo."

        # Agregar respuesta del asistente
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.write(bot_response)

    # Botón para avanzar (visible siempre que haya conversación)
    if len(st.session_state.messages) > 1:
        st.write("---")
        if st.button("Pasar a Propuesta de Arquitectura ➡️"):
            st.session_state.step = 2
            st.rerun()

# Paso 2: Propuesta de Arquitectura
elif st.session_state.step == 2:
    st.subheader("Paso 2: Propuesta de Arquitectura e Integraciones")
    
    if client:
        with st.spinner("Diseñando la mejor jerarquía de agentes para ti..."):
            messages = []
            system_prompt = f"""Basado en la conversación anterior, diseña una arquitectura de agentes.
            Stack actual del usuario: Skills: {skills}, MCPs: ['notebooklm'].
            
            Debes proponer la mejor jerarquía. Si falta algo (ej. una conexión a n8n o una base de datos), menciónalo.
            
            IMPORTANTE: Devuelve la respuesta ÚNICAMENTE en formato JSON válido (un array de objetos). No agregues texto antes ni después.
            Formato requerido:
            [
                {{
                    "name": "Nombre del Agente",
                    "role": "Qué hará específicamente",
                    "type": "Python / n8n / Skill existente",
                    "reason": "Por qué es la mejor opción para el stack"
                }}
            ]
            """
            messages.append({"role": "system", "content": system_prompt})
            for m in st.session_state.messages:
                role = "assistant" if m["role"] == "assistant" else "user"
                messages.append({"role": role, "content": m["content"]})
                
            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages
                )
                text = response.choices[0].message.content
                # Extraer JSON por si acaso viene con markdown
                start = text.find("[")
                end = text.rfind("]") + 1
                if start != -1 and end != -1:
                    proposal = json.loads(text[start:end])
                    st.session_state.proposal = proposal
                else:
                    proposal = [{"name": "Error", "role": "No se pudo parsear el JSON", "type": "Error", "reason": text}]
            except Exception as e:
                proposal = [{"name": "Error", "role": "Fallo en la llamada", "type": "Error", "reason": str(e)}]
    else:
        # Mock en caso de no haber cliente
        proposal = [
            {"name": "El Estratega", "role": "Analiza la idea y estructura el plan", "type": "Skill (marketing)", "reason": "Ya tienes una skill de marketing que podemos adaptar."},
            {"name": "El Obrero", "role": "Escribe el código o conecta n8n", "type": "Python", "reason": "Para lógica que no cubren tus skills actuales."}
        ]
        st.session_state.proposal = proposal

    st.write("Yo considero que esta es la mejor opción basada en lo conversado:")
    
    selected_agents = []
    for i, agent in enumerate(proposal):
        col1, col2 = st.columns([1, 4])
        with col1:
            checked = st.checkbox(agent.get("name", f"Agente {i}"), value=True, key=f"agent_{i}")
            if checked:
                selected_agents.append(agent.get("name"))
        with col2:
            st.write(f"**Rol:** {agent.get('role')}")
            st.write(f"**Tipo:** `{agent.get('type')}`")
            st.write(f"**Razón:** {agent.get('reason')}")
            st.write("---")

    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("⬅️ Volver al Chat"):
            st.session_state.step = 1
            st.rerun()
    with col_next:
        if st.button("¡Pam! Crear Todo", type="primary"):
            st.session_state.step = 3
            st.rerun()

# Paso 3: Despliegue
elif st.session_state.step == 3:
    st.subheader("Paso 3: Despliegue y Orquestación")
    st.success("¡Todo listo! He diseñado la jerarquía.")
    
    proposal = st.session_state.get('proposal', [])
    
    if proposal:
        st.write("Generando archivos para los siguientes agentes:")
        for agent in proposal:
            name = agent.get("name", "Agente_Sin_Nombre").replace(" ", "_").lower()
            role = agent.get("role", "")
            agent_type = agent.get("type", "")
            
            # Crear directorio
            dir_path = f"generated_agents/{name}"
            os.makedirs(dir_path, exist_ok=True)
            
            # Crear SKILL.md
            skill_content = f"""---
name: {name}
description: {role}
---
# {agent.get("name")}
**Rol:** {role}
**Tipo:** {agent_type}
"""
            with open(f"{dir_path}/SKILL.md", "w", encoding="utf-8") as f:
                f.write(skill_content)
                
            # Crear script dummy si es Python
            if "python" in agent_type.lower():
                with open(f"{dir_path}/{name}.py", "w", encoding="utf-8") as f:
                    f.write(f"# Script para {agent.get('name')}\n# Rol: {role}\n\nprint('Hola, soy {agent.get('name')}')\n")
                    
            st.write(f"- ✅ Creada carpeta `{dir_path}` con SKILL.md")
            
    st.info("Archivos generados en la carpeta `generated_agents/`. ¡Ya puedes empezar a usarlos!")
    
    if st.button("Empezar un nuevo proyecto"):
        st.session_state.step = 1
        st.session_state.messages = []
        if 'proposal' in st.session_state:
            del st.session_state.proposal
        st.rerun()
