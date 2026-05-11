
import json
import os
import sys
from datetime import datetime

class PipelineInvestigacionDespliegue:
    """Pipeline automatizado de investigacion y despliegue"""
    
    def __init__(self, ruta_config="pipelines/pipeline_investigacion_despliegue.json"):
        with open(ruta_config, "r") as f:
            self.config = json.load(f)
        self.estado = {"fase_actual": 0, "log": [], "iniciado": datetime.now().isoformat()}
    
    def ejecutar(self):
        """Ejecutar todas las fases del pipeline secuencialmente"""
        resultados = []
        for fase in self.config["fases"]:
            print(f"\n=== EJECUTANDO FASE {fase['id']}: {fase['nombre']} ===")
            resultado = self._ejecutar_fase(fase)
            resultados.append(resultado)
            self.estado["log"].append({
                "fase": fase["nombre"],
                "resultado": resultado["estado"],
                "timestamp": datetime.now().isoformat()
            })
            
            if resultado["estado"] == "fallo":
                print(f"FASE {fase['nombre']} FALLIDA. Deteniendo pipeline.")
                break
        return resultados
    
    def _ejecutar_fase(self, fase):
        """Ejecutar una fase individual"""
        return {"fase": fase["nombre"], "estado": "pendiente", "accion": fase["accion_base"]}
    
    def obtener_resumen(self):
        """Obtener resumen del estado del pipeline"""
        return {
            "config": self.config["nombre"],
            "fases_completadas": len([l for l in self.estado["log"]]),
            "ultima_fase": self.estado["log"][-1] if self.estado["log"] else None,
            "iniciado": self.estado["iniciado"]
        }

if __name__ == "__main__":
    pipeline = PipelineInvestigacionDespliegue()
    pipeline.ejecutar()
    print(json.dumps(pipeline.obtener_resumen(), indent=2))
