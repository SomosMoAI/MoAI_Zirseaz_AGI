# Pipeline de Investigación y Despliegue Automatizado

**Generado:** 2026-05-11T11:33:40.841741
**Estado:** ACTIVO

## Estructura

- `investigador.py` - Motor de investigación con búsqueda web y análisis
- `despliegue.py` - Gestor de despliegue automatizado
- `orquestador.py` - Orquestador que coordina investigación + despliegue
- `resultados/` - Resultados de investigaciones
- `despliegues/` - Configuraciones y estados de despliegues
- `logs/` - Logs del pipeline completo

## Uso

```bash
# Pipeline completo
python orquestador.py "tema de investigación"

# Solo investigación
python investigador.py "tema"

# Solo despliegue
python despliegue.py deploy
```

## Características

- ✅ Investigación web automatizada
- ✅ Despliegue local con verificación de estado
- ✅ Pipeline completo orquestado
- ✅ Logging y persistencia de resultados
- ✅ Modular y extensible
