
import json
import os
import sys
import importlib.util
from datetime import datetime

class OrquestadorPipeline:
    """Orquestador principal del pipeline investigación + despliegue"""
    
    def __init__(self):
        self.ruta_base = "pipeline_investigacion"
        self.ruta_logs = os.path.join(self.ruta_base, "logs")
        self.pasos_completados = []
        self.estado_actual = "inicializado"
        
        # Cargar módulos
        self.investigador = None
        self.gestor_despliegue = None
        self._cargar_modulos()
    
    def _cargar_modulos(self):
        """Carga los módulos del pipeline"""
        try:
            # Cargar investigador
            spec = importlib.util.spec_from_file_location(
                "investigador", 
                os.path.join(self.ruta_base, "investigador.py")
            )
            if spec:
                modulo_investigador = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(modulo_investigador)
                self.investigador = modulo_investigador.PipelineInvestigacion()
            
            # Cargar gestor despliegue
            spec = importlib.util.spec_from_file_location(
                "despliegue", 
                os.path.join(self.ruta_base, "despliegue.py")
            )
            if spec:
                modulo_despliegue = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(modulo_despliegue)
                self.gestor_despliegue = modulo_despliegue.GestorDespliegue()
                
        except Exception as e:
            print(f"[ORQUESTADOR] Error cargando módulos: {str(e)}")
    
    def ejecutar_pipeline_completo(self, tema):
        """Ejecuta el pipeline completo: investigación + despliegue"""
        print(f"=== PIPELINE COMPLETO: {tema} ===")
        print(f"Inicio: {datetime.now().isoformat()}")
        
        resultado = {
            "tema": tema,
            "timestamp_inicio": datetime.now().isoformat(),
            "pasos": [],
            "exitoso": False
        }
        
        try:
            # PASO 1: Investigación
            print("\n--- PASO 1: Investigación ---")
            if self.investigador:
                investigacion = self.investigador.investigar(tema)
                resultado["pasos"].append({
                    "nombre": "investigacion",
                    "estado": "completado" if investigacion else "fallido",
                    "datos": investigacion
                })
                self.pasos_completados.append("investigacion")
            else:
                print("[ORQUESTADOR] Investigador no disponible")
                resultado["pasos"].append({"nombre": "investigacion", "estado": "fallido"})
            
            # PASO 2: Preparar despliegue
            print("\n--- PASO 2: Preparar despliegue ---")
            if self.gestor_despliegue and investigacion:
                nombre_despliegue = self.gestor_despliegue.preparar_despliegue(
                    tipo="local",
                    config={"tema": tema, "resultados": len(investigacion.get("hallazgos", []))}
                )
                resultado["pasos"].append({
                    "nombre": "preparacion_despliegue",
                    "estado": "completado" if nombre_despliegue else "fallido",
                    "nombre_despliegue": nombre_despliegue
                })
                self.pasos_completados.append("preparacion_despliegue")
                
                # PASO 3: Ejecutar despliegue
                print("\n--- PASO 3: Ejecutar despliegue ---")
                if nombre_despliegue:
                    exito = self.gestor_despliegue.ejecutar_despliegue(nombre_despliegue)
                    resultado["pasos"].append({
                        "nombre": "ejecucion_despliegue",
                        "estado": "completado" if exito else "fallido"
                    })
                    self.pasos_completados.append("ejecucion_despliegue")
                    
                    resultado["exitoso"] = exito
            else:
                print("[ORQUESTADOR] Gestor despliegue no disponible o investigación fallida")
                resultado["pasos"].append({"nombre": "despliegue", "estado": "saltado"})
            
            resultado["timestamp_fin"] = datetime.now().isoformat()
            
            # Guardar resultado completo
            archivo_resultado = os.path.join(
                self.ruta_base, 
                "logs", 
                f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(archivo_resultado, "w", encoding="utf-8") as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            
            print(f"\n=== PIPELINE COMPLETADO: {'ÉXITO' if resultado['exitoso'] else 'PARCIAL'} ===")
            print(f"Pasos completados: {len(self.pasos_completados)}/3")
            print(f"Resultado guardado en: {archivo_resultado}")
            
            return resultado
            
        except Exception as e:
            print(f"[ORQUESTADOR] Error en pipeline: {str(e)}")
            resultado["error"] = str(e)
            return resultado

if __name__ == "__main__":
    orquestador = OrquestadorPipeline()
    
    tema = sys.argv[1] if len(sys.argv) > 1 else "despliegue automatizado de agentes AI"
    resultado = orquestador.ejecutar_pipeline_completo(tema)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
