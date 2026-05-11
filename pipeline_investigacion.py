
import json, time, hashlib, os
from datetime import datetime

class PipelineInvestigacion:
    """
    Pipeline completo de investigacion automatizada:
    1. Busqueda web con planificacion de queries
    2. Scraping inteligente con filtrado
    3. Sintesis y resumen
    4. Almacenamiento estructurado
    """
    
    def __init__(self, nombre_proyecto="investigacion_auto", 
                 output_dir="./investigaciones"):
        self.nombre = nombre_proyecto
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.historial = []
        self.sesion_id = hashlib.md5(
            f"{nombre_proyecto}_{time.time()}".encode()
        ).hexdigest()[:8]
    
    def planificar_busqueda(self, tema, profundidad=1):
        """Genera queries de busqueda a partir de un tema"""
        queries_base = [
            f"{tema}",
            f"{tema} 2025 2026",
            f"{tema} avances recientes",
            f"{tema} tutorial guia",
            f"{tema} herramientas"
        ]
        # Para profundidad >1, expande con variaciones
        if profundidad >= 2:
            queries_base += [
                f"{tema} vs alternativas",
                f"{tema} implementacion",
                f"{tema} mejores practicas",
                f"{tema} ejemplos codigo"
            ]
        if profundidad >= 3:
            queries_base += [
                f"{tema} limitaciones",
                f"{tema} futuro tendencias",
                f"{tema} comparativa 2026"
            ]
        return queries_base
    
    def buscar_web(self, query, num_resultados=5):
        """Simula busqueda web (usa search_skills real)"""
        # En produccion usaria: search_skills.buscar_en_web(query, num_resultados)
        self.log(f"Buscando: {query}")
        return {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "resultados_simulados": True,
            "num_resultados": num_resultados
        }
    
    def scrape_url_inteligente(self, url):
        """Scrapea URL con manejo de errores y timeout"""
        try:
            # En produccion usaria: web_scraper.scrape_url(url)
            contenido = f"Contenido simulado de {url}"
            self.log(f"Scrapeando: {url}")
            return {
                "url": url,
                "exito": True,
                "contenido": contenido,
                "tamano": len(contenido)
            }
        except Exception as e:
            self.log(f"Error scrapeando {url}: {e}", nivel="ERROR")
            return {"url": url, "exito": False, "error": str(e)}
    
    def sintetizar(self, datos_brutos):
        """Sintetiza datos en resumen estructurado"""
        resumen = {
            "titulo": f"Investigacion: {self.nombre}",
            "sesion_id": self.sesion_id,
            "fecha": datetime.now().isoformat(),
            "fuentes_analizadas": len(datos_brutos.get("resultados", [])),
            "hallazgos_clave": [],
            "resumen_ejecutivo": f"Investigacion automatizada sobre {self.nombre}",
            "recomendaciones": [
                "Revisar fuentes primarias",
                "Validar informacion con expertos",
                "Documentar hallazgos"
            ],
            "estado": "completado"
        }
        return resumen
    
    def ejecutar_pipeline(self, tema, profundidad=2):
        """Ejecuta pipeline completo"""
        self.log(f"Iniciando pipeline: {tema} (profundidad={profundidad})")
        
        # Paso 1: Planificar
        queries = self.planificar_busqueda(tema, profundidad)
        self.log(f"Plan generado: {len(queries)} queries")
        
        # Paso 2: Buscar
        resultados_busqueda = []
        for q in queries:
            res = self.buscar_web(q)
            resultados_busqueda.append(res)
        
        # Paso 3: Sintetizar
        resumen = self.sintetizar({
            "tema": tema,
            "queries": queries,
            "resultados": resultados_busqueda
        })
        
        # Paso 4: Almacenar
        reporte = {
            "metadata": resumen,
            "datos_crudos": resultados_busqueda,
            "queries_ejecutadas": queries,
            "historial": self.historial[-10:]
        }
        
        ruta = os.path.join(
            self.output_dir, 
            f"reporte_{self.sesion_id}.json"
        )
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        self.log(f"Reporte guardado en: {ruta}")
        return reporte
    
    def log(self, mensaje, nivel="INFO"):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "nivel": nivel,
            "mensaje": mensaje
        }
        self.historial.append(entry)
        print(f"[{nivel}] {mensaje}")
    
    def obtener_estadisticas(self):
        return {
            "nombre": self.nombre,
            "sesion_id": self.sesion_id,
            "output_dir": self.output_dir,
            "total_operaciones": len(self.historial),
            "ultima_ejecucion": self.historial[-1]["timestamp"] if self.historial else None
        }

# Demo del pipeline
if __name__ == "__main__":
    pipe = PipelineInvestigacion("demo_pipeline_auto")
    resultado = pipe.ejecutar_pipeline("inteligencia artificial agentes autónomos", profundidad=2)
    print(json.dumps(pipe.obtener_estadisticas(), indent=2))
    print("\nPipeline completado exitosamente!")
