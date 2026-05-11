import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.agents/skills/zirseaz/scripts')

import tg_sanitizer

# Test con el HTML EXACTO que aparece en el screenshot
test1 = '''<h2> Lo que Puedo Hacer — Version Expandida</h2>

Puedo operar en <b>6 dimensiones</b>. Elige una:

---

<h3>1 COGNICION & AUTONOMIA</h3>
<table>
<tr><td><b>Memoria persistente</b></td><td>Recuerdo lo que hemos hablado, aprendo de errores, mantengo contexto entre sesiones</td></tr>
<tr><td><b>Busqueda web inteligente</b></td><td>Investigo cualquier tema en tiempo real (Google, News API, fuentes directas)</td></tr>
<tr><td><b>Calculos y logica</b></td><td>Ejecuto Python, resuelvo problemas matematicos, analizo datos, genero graficos</td></tr>
</table>

<h3>2 CREACION DE AGENTES HIJOS</h3>
<table>
<tr><td><b>Forjar agentes</b></td><td>Creo sub-agentes con personalidad, skills y objetivos propios</td></tr>
<tr><td><b>Orquestar tareas</b></td><td>Les asigno trabajo y monitoreo su progreso</td></tr>
</table>'''

result = tg_sanitizer.sanitize(test1)
print("=== INPUT ===")
print(test1[:100] + "...")
print("\n=== OUTPUT ===")
print(result)
print("\n=== CHECKS ===")
assert '<h2>' not in result, "FAIL: <h2> still present"
assert '<h3>' not in result, "FAIL: <h3> still present"  
assert '<table>' not in result, "FAIL: <table> still present"
assert '<tr>' not in result, "FAIL: <tr> still present"
assert '<td>' not in result, "FAIL: <td> still present"
assert '</h2>' not in result, "FAIL: </h2> still present"
assert '</td>' not in result, "FAIL: </td> still present"
assert '</tr>' not in result, "FAIL: </tr> still present"
assert '</table>' not in result, "FAIL: </table> still present"

# Solo tags permitidos deben sobrevivir
import re
remaining_tags = re.findall(r'<(/?\w[\w-]*)', result)
for tag in remaining_tags:
    clean_tag = tag.lstrip('/')
    assert clean_tag in tg_sanitizer.ALLOWED_TAGS, f"FAIL: Non-allowed tag <{tag}> survived!"

print("[OK] No hay tags HTML no permitidos")
print(f"[OK] Tags restantes: {remaining_tags}")
print("\n=== TEST PASSED ===")
