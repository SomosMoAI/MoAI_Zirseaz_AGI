"""
Zirseaz Cortex v1 — Motor de Planificación Multi-Paso (ReAct Loop).

Transforma a Zirseaz de un bot reactivo a un agente cognitivo que:
1. PIENSA (Thought): Analiza qué se necesita
2. PLANIFICA (Plan): Descompone en pasos
3. ACTÚA (Action): Ejecuta un paso
4. OBSERVA (Observe): Evalúa el resultado
5. REPLANTEA (Replan): Ajusta si algo falló

Protocolo XML:
  <CORTEX_PLAN>JSON con lista de pasos</CORTEX_PLAN>
  <CORTEX_STEP>Código o acción del paso actual</CORTEX_STEP>
  <CORTEX_REFLECT>Evaluación del resultado</CORTEX_REFLECT>
"""
import json
import time
import os


class CortexPlan:
    """Representa un plan multi-paso con estado de ejecución."""
    
    def __init__(self, goal, steps=None):
        self.goal = goal
        self.steps = steps or []
        self.current_step = 0
        self.status = "planning"  # planning | executing | completed | failed
        self.created_at = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.results = []
        self.max_replans = 2
        self.replan_count = 0
    
    def add_step(self, description, action_type="code", code=""):
        """Agrega un paso al plan."""
        self.steps.append({
            "id": len(self.steps) + 1,
            "description": description,
            "action_type": action_type,  # code | query | hitl
            "code": code,
            "status": "pending",  # pending | running | success | failed | skipped
            "result": None,
            "started_at": None,
            "completed_at": None
        })
    
    def get_current_step(self):
        """Retorna el paso actual o None si el plan está completo."""
        if self.current_step >= len(self.steps):
            return None
        return self.steps[self.current_step]
    
    def mark_step_success(self, result=""):
        """Marca el paso actual como exitoso y avanza."""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            step["status"] = "success"
            step["result"] = result[:500]  # Truncar para no saturar contexto
            step["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            self.results.append({"step": step["id"], "success": True, "result": result[:200]})
            self.current_step += 1
            
            if self.current_step >= len(self.steps):
                self.status = "completed"
    
    def mark_step_failed(self, error=""):
        """Marca el paso actual como fallido."""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            step["status"] = "failed"
            step["result"] = f"ERROR: {error[:500]}"
            step["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            self.results.append({"step": step["id"], "success": False, "error": error[:200]})
    
    def can_replan(self):
        """Verifica si se puede intentar replantear."""
        return self.replan_count < self.max_replans
    
    def replan(self, new_steps_from_current):
        """Reemplaza los pasos restantes con nuevos pasos (replanning)."""
        self.replan_count += 1
        # Mantener los pasos ya completados, reemplazar desde current
        completed = self.steps[:self.current_step]
        self.steps = completed + new_steps_from_current
        # No avanzar current_step — el paso fallido se reintentará con nuevo código
    
    def to_context_string(self):
        """Genera un resumen del plan para inyectar en el contexto del LLM."""
        lines = [f"PLAN ACTIVO: {self.goal}"]
        lines.append(f"Estado: {self.status} | Paso {self.current_step + 1}/{len(self.steps)} | Replans: {self.replan_count}/{self.max_replans}")
        
        for s in self.steps:
            icon = {"pending": "[ ]", "running": "[>]", "success": "[OK]", "failed": "[X]", "skipped": "[-]"}.get(s["status"], "[?]")
            lines.append(f"  {icon} Paso {s['id']}: {s['description']}")
            if s["result"]:
                lines.append(f"       -> {s['result'][:100]}")
        
        return "\n".join(lines)
    
    def to_dict(self):
        """Serializa el plan a dict."""
        return {
            "goal": self.goal,
            "steps": self.steps,
            "current_step": self.current_step,
            "status": self.status,
            "created_at": self.created_at,
            "results": self.results,
            "replan_count": self.replan_count
        }
    
    @classmethod
    def from_dict(cls, data):
        """Deserializa un plan desde dict."""
        plan = cls(data.get("goal", ""))
        plan.steps = data.get("steps", [])
        plan.current_step = data.get("current_step", 0)
        plan.status = data.get("status", "planning")
        plan.created_at = data.get("created_at", "")
        plan.results = data.get("results", [])
        plan.replan_count = data.get("replan_count", 0)
        return plan


def parse_plan_from_response(response_text):
    """
    Extrae un plan JSON del response del LLM si contiene <CORTEX_PLAN>...</CORTEX_PLAN>.
    
    Formato esperado dentro del tag:
    {
        "goal": "Descripción del objetivo",
        "steps": [
            {"description": "Paso 1", "action_type": "code", "code": "..."},
            {"description": "Paso 2", "action_type": "code", "code": "..."}
        ]
    }
    """
    if "<CORTEX_PLAN>" not in response_text:
        return None
    
    try:
        start = response_text.find("<CORTEX_PLAN>") + len("<CORTEX_PLAN>")
        end = response_text.find("</CORTEX_PLAN>", start)
        if end == -1:
            return None
        
        plan_json = response_text[start:end].strip()
        plan_data = json.loads(plan_json)
        
        plan = CortexPlan(plan_data.get("goal", "Sin objetivo"))
        for step_data in plan_data.get("steps", []):
            plan.add_step(
                description=step_data.get("description", "Sin descripcion"),
                action_type=step_data.get("action_type", "code"),
                code=step_data.get("code", "")
            )
        
        plan.status = "executing"
        return plan
        
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"[Cortex] Error parseando plan: {e}")
        return None


def build_react_prompt_injection(active_plan=None):
    """
    Genera el bloque de instrucciones ReAct para inyectar en el system prompt.
    Si hay un plan activo, incluye su estado.
    """
    base = """
PLANIFICACION MULTI-PASO (ReAct Cortex):
Para tareas complejas (mas de 2 pasos), usa planificacion estructurada:

1. Si la tarea requiere multiples pasos, crea un plan:
<CORTEX_PLAN>
{
    "goal": "Que quiero lograr",
    "steps": [
        {"description": "Paso 1: ...", "action_type": "code", "code": "# codigo python"},
        {"description": "Paso 2: ...", "action_type": "code", "code": "# codigo python"}
    ]
}
</CORTEX_PLAN>

2. El sistema ejecutara cada paso secuencialmente y te mostrara los resultados.
3. Si un paso falla, puedes replantear los pasos restantes.
4. Para tareas simples (1-2 pasos), sigue usando <CMD_EXECUTE> directamente.

REGLA: Solo crea un CORTEX_PLAN si la tarea necesita 3+ pasos coordinados.
"""
    
    if active_plan:
        base += f"\n\nPLAN EN EJECUCION:\n{active_plan.to_context_string()}\n"
        
        current = active_plan.get_current_step()
        if current:
            if current["status"] == "failed":
                base += f"\nEl ultimo paso FALLO. Debes decidir:\n"
                base += f"- Generar un <CMD_EXECUTE> con codigo corregido para reintentar\n"
                base += f"- O responder al usuario explicando el error\n"
            else:
                base += f"\nEjecuta el siguiente paso del plan usando <CMD_EXECUTE>.\n"
    
    return base


def should_use_cortex(message_text):
    """
    Heurística simple para determinar si un mensaje necesita planificación multi-paso.
    Retorna True si la tarea parece compleja.
    """
    complexity_signals = [
        # Señales de tarea multi-paso
        "paso a paso", "step by step",
        "crea un", "genera un", "construye",
        "investiga", "analiza y",
        "primero", "luego", "despues",
        "completo", "completa",
        # Señales de tareas complejas
        "pagina web", "sitio web", "landing",
        "agente", "sub-agente",
        "pipeline", "flujo",
        "audita", "evoluciona",
    ]
    
    text_lower = message_text.lower()
    matches = sum(1 for signal in complexity_signals if signal in text_lower)
    
    # Si tiene 2+ señales de complejidad, probablemente necesita plan
    return matches >= 2


# ─── Persistencia de planes ───

PLANS_DIR = os.path.join(os.getcwd(), ".agents", "skills", "zirseaz", "state")


def save_plan(plan):
    """Guarda el plan activo a disco."""
    os.makedirs(PLANS_DIR, exist_ok=True)
    filepath = os.path.join(PLANS_DIR, "active_plan.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(plan.to_dict(), f, indent=2, ensure_ascii=False)


def load_plan():
    """Carga el plan activo desde disco (si existe)."""
    filepath = os.path.join(PLANS_DIR, "active_plan.json")
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        plan = CortexPlan.from_dict(data)
        # Solo cargar si no está completado/fallido
        if plan.status in ("executing", "planning"):
            return plan
        return None
    except Exception:
        return None


def clear_plan():
    """Limpia el plan activo."""
    filepath = os.path.join(PLANS_DIR, "active_plan.json")
    if os.path.exists(filepath):
        os.remove(filepath)
