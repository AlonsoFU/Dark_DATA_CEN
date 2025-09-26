#!/usr/bin/env python3
"""
Esquema Universal Español - Sistema Eléctrico
Wrapper functions para convertir extracciones a esquema universal en español
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

def crear_documento_universal(datos_extraccion: dict,
                            titulo_documento: str,
                            fecha_documento: str,
                            tipo_documento: str,
                            dominio: str = "operaciones",
                            puntuacion_confianza: float = 0.85) -> dict:
    """
    Convierte resultados de extracción al formato de esquema universal español

    Args:
        datos_extraccion: Tus resultados de extracción existentes
        titulo_documento: Título del documento
        fecha_documento: Fecha en formato YYYY-MM-DD
        tipo_documento: Tipo de documento (anexo_01, anexo_02, etc.)
        dominio: Dominio del sistema (operaciones, mercados, legal, planificacion)
        puntuacion_confianza: Confianza general de la extracción

    Returns:
        Documento en formato de esquema universal español
    """

    # Generar ID único del documento
    id_documento = f"cen:{dominio}:{tipo_documento}:{fecha_documento}"

    # Extraer entidades de tus datos existentes
    entidades = extraer_entidades_de_datos(datos_extraccion)

    # Generar etiquetas semánticas
    etiquetas_semanticas = generar_etiquetas_semanticas(datos_extraccion, dominio)

    documento_universal = {
        "@context": "https://coordinador.cl/context/v1",
        "@id": id_documento,
        "@type": obtener_tipo_documento(dominio),

        "metadatos_universales": {
            "titulo": titulo_documento,
            "dominio": dominio,
            "tipo_documento": tipo_documento,
            "fecha_creacion": fecha_documento,
            "fecha_procesamiento": datetime.now().isoformat(),
            "idioma": "es",
            "version": "1.0",
            "estado": "final",
            "pais": "España",
            "regulador": "CNMC"
        },

        "entidades": entidades,
        "referencias_cruzadas": [],  # Se completará por motor de referencias cruzadas
        "etiquetas_semanticas": etiquetas_semanticas,

        "datos_especificos_dominio": {
            dominio: datos_extraccion  # TUS DATOS ORIGINALES SE PRESERVAN AQUÍ
        },

        "metadatos_calidad": {
            "confianza_extraccion": puntuacion_confianza,
            "estado_validacion": "aprobado",
            "metodo_procesamiento": "extraccion_automatizada",
            "puntuacion_calidad": puntuacion_confianza,
            "validado_humano": False,
            "sistema_electrico": "español",
            "normativa_aplicable": "Ley 24/2013 del Sector Eléctrico"
        }
    }

    return documento_universal

def extraer_entidades_de_datos(datos: dict) -> dict:
    """Extraer entidades de la estructura de datos de extracción existente"""

    entidades = {
        "centrales_electricas": [],
        "empresas": [],
        "ubicaciones": [],
        "regulaciones": [],
        "equipos": []
    }

    # Extraer de upper_table (estructura anexo)
    if "upper_table" in datos and "rows" in datos["upper_table"]:
        for fila in datos["upper_table"]["rows"]:
            # Buscar nombres de centrales en diferentes campos posibles
            nombre_central = None
            for campo in ["central", "planta", "generador", "unidad", "nombre"]:
                if campo in fila and fila[campo]:
                    nombre_candidato = fila[campo].strip()
                    if es_probable_nombre_central(nombre_candidato):
                        nombre_central = nombre_candidato
                        break

            if nombre_central:
                entidades["centrales_electricas"].append({
                    "@id": f"cen:central:{normalizar_nombre(nombre_central)}",
                    "@type": determinar_tipo_central(nombre_central),
                    "nombre": nombre_central,
                    "confianza": 0.9,
                    "metadatos": {
                        "fuente_anexo": "tabla_superior",
                        "sistema_electrico": "español"
                    }
                })

            # Buscar nombres de empresas
            nombre_empresa = None
            for campo in ["empresa", "compañia", "operador", "propietario"]:
                if campo in fila and fila[campo]:
                    nombre_candidato = fila[campo].strip()
                    if es_probable_nombre_empresa(nombre_candidato):
                        nombre_empresa = nombre_candidato
                        break

            if nombre_empresa and not any(e["nombre"] == nombre_empresa for e in entidades["empresas"]):
                entidades["empresas"].append({
                    "@id": f"cen:empresa:{normalizar_nombre(nombre_empresa)}",
                    "@type": "EmpresaElectrica",
                    "nombre": nombre_empresa,
                    "confianza": 0.85,
                    "metadatos": {
                        "pais": "España",
                        "sector": "electrico"
                    }
                })

    # Extraer de lower_table si existe
    if "lower_table" in datos and "rows" in datos["lower_table"]:
        for fila in datos["lower_table"]["rows"]:
            for campo, valor in fila.items():
                if isinstance(valor, str) and len(valor) > 3:
                    if es_probable_nombre_central(valor):
                        if not any(c["nombre"] == valor for c in entidades["centrales_electricas"]):
                            entidades["centrales_electricas"].append({
                                "@id": f"cen:central:{normalizar_nombre(valor)}",
                                "@type": determinar_tipo_central(valor),
                                "nombre": valor,
                                "confianza": 0.85,
                                "metadatos": {
                                    "fuente_anexo": "tabla_inferior",
                                    "sistema_electrico": "español"
                                }
                            })

    # Remover duplicados
    for tipo_entidad in entidades:
        entidades[tipo_entidad] = remover_entidades_duplicadas(entidades[tipo_entidad])

    return entidades

def determinar_tipo_central(nombre_central: str) -> str:
    """Determinar tipo de central desde el nombre (adaptado para España)"""
    nombre_lower = nombre_central.lower()

    # Tecnologías renovables en España
    if any(palabra in nombre_lower for palabra in ["solar", "fotovoltaica", "fv", "pv"]):
        return "CentralSolar"
    elif any(palabra in nombre_lower for palabra in ["eólica", "eolica", "viento", "wind"]):
        return "CentralEolica"
    elif any(palabra in nombre_lower for palabra in ["hidro", "agua", "embalse", "salto"]):
        return "CentralHidroelectrica"
    elif any(palabra in nombre_lower for palabra in ["nuclear"]):
        return "CentralNuclear"
    elif any(palabra in nombre_lower for palabra in ["térmica", "termica", "carbón", "carbon", "gas", "ciclo combinado", "cogeneracion"]):
        return "CentralTermica"
    elif any(palabra in nombre_lower for palabra in ["biomasa", "biogas"]):
        return "CentralBiomasa"
    elif any(palabra in nombre_lower for palabra in ["mareomotriz", "undimotriz"]):
        return "CentralMarina"
    else:
        return "CentralElectrica"

def es_probable_nombre_central(texto: str) -> bool:
    """Verificar si el texto es probablemente nombre de central (adaptado para España)"""
    if not isinstance(texto, str) or len(texto) < 3:
        return False

    # Saltar valores numéricos, fechas, unidades
    if re.match(r'^[\d\.\,\s]+$', texto.strip()):
        return False
    if re.match(r'^\d{2}/\d{2}/\d{4}$', texto.strip()):
        return False
    if texto.strip().upper() in ["MW", "GWH", "KV", "N/A", "SI", "NO", "OK"]:
        return False

    # Buscar indicadores de centrales españolas
    indicadores_central = ["central", "planta", "parque", "complejo", "instalacion", "ct", "cc"]
    palabras_energia = ["solar", "eólica", "eolica", "hidro", "térmica", "termica", "nuclear", "biomasa"]

    texto_lower = texto.lower()
    tiene_indicador = any(palabra in texto_lower for palabra in indicadores_central)
    tiene_energia = any(palabra in texto_lower for palabra in palabras_energia)

    # Si tiene ambos indicadores, probablemente es una central
    if tiene_indicador and tiene_energia:
        return True

    # Si tiene palabras de energía y longitud razonable, probablemente es una central
    if tiene_energia and 5 <= len(texto) <= 60:
        return True

    # Patrones comunes de nombres de centrales españolas
    if re.match(r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s\-]+\d*$', texto) and len(texto) > 5:
        return True

    return False

def es_probable_nombre_empresa(texto: str) -> bool:
    """Verificar si el texto es probablemente nombre de empresa española"""
    if not isinstance(texto, str) or len(texto) < 3:
        return False

    # Indicadores de empresas españolas
    indicadores_empresa = ["s.a.", "s.l.", "s.l.u.", "s.a.u.", "iberdrola", "endesa", "naturgy", "repsol", "acciona", "renovables"]

    texto_lower = texto.lower()
    if any(indicador in texto_lower for indicador in indicadores_empresa):
        return True

    # Patrones de nombres empresariales
    if any(palabra in texto_lower for palabra in ["energia", "energía", "eléctrica", "electrica", "power", "renovables"]):
        return True

    return False

def normalizar_nombre(nombre: str) -> str:
    """Normalizar nombre para ID de entidad"""
    import re
    # Remover caracteres especiales y normalizar
    normalizado = re.sub(r'[^a-zA-ZáéíóúñÁÉÍÓÚÑ0-9\s]', '', nombre.lower())
    # Reemplazar acentos para IDs
    normalizado = (normalizado.replace('á', 'a').replace('é', 'e').replace('í', 'i')
                              .replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n'))
    normalizado = re.sub(r'\s+', '_', normalizado.strip())
    return normalizado

def remover_entidades_duplicadas(lista_entidades: list) -> list:
    """Remover entidades duplicadas por nombre"""
    nombres_vistos = set()
    entidades_unicas = []

    for entidad in lista_entidades:
        nombre = entidad.get("nombre", "")
        if nombre not in nombres_vistos:
            nombres_vistos.add(nombre)
            entidades_unicas.append(entidad)

    return entidades_unicas

def generar_etiquetas_semanticas(datos: dict, dominio: str) -> list:
    """Generar etiquetas semánticas en español"""
    etiquetas = {dominio}

    # Añadir etiqueta de dominio
    etiquetas.add(dominio)

    # Añadir etiquetas de tipo de datos
    texto_datos = json.dumps(datos).lower()
    if any(palabra in texto_datos for palabra in ["tiempo real", "actual", "ahora"]):
        etiquetas.add("tiempo_real")
    elif any(palabra in texto_datos for palabra in ["histórico", "pasado", "anterior"]):
        etiquetas.add("historico")
    elif any(palabra in texto_datos for palabra in ["pronóstico", "proyección", "estimación"]):
        etiquetas.add("pronostico")

    # Añadir etiquetas específicas del dominio español
    if dominio == "operaciones":
        etiquetas.update(["datos_operacionales", "gestion_sistema", "red_electrica_española"])

        # Verificar energías renovables
        if "solar" in texto_datos:
            etiquetas.add("energia_renovable")
        if "eólica" in texto_datos or "eolica" in texto_datos:
            etiquetas.add("energia_renovable")
        if "hidro" in texto_datos:
            etiquetas.add("energia_renovable")

    elif dominio == "mercados":
        etiquetas.update(["datos_mercado", "analisis_economico", "omie", "precio_electricidad"])
    elif dominio == "legal":
        etiquetas.update(["cumplimiento_regulatorio", "marco_legal", "cnmc", "ley_sector_electrico"])
    elif dominio == "planificacion":
        etiquetas.update(["planificacion_infraestructura", "analisis_capacidad", "pniec"])

    return sorted(list(etiquetas))

def obtener_tipo_documento(dominio: str) -> str:
    """Obtener @type del documento basado en dominio español"""
    mapeo_tipos = {
        "operaciones": "DocumentoSistemaElectrico",
        "mercados": "InformeMercado",
        "legal": "RegulacionLegal",
        "planificacion": "EstudioPlanificacion"
    }
    return mapeo_tipos.get(dominio, "Documento")

def guardar_json_esquema_universal(documento: dict, ruta_salida: Path):
    """Guardar documento en formato esquema universal"""

    # Asegurar que el directorio existe
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    # Añadir metadatos de guardado
    documento["metadatos_calidad"]["guardado_en"] = datetime.now().isoformat()
    documento["metadatos_calidad"]["ruta_archivo"] = str(ruta_salida)

    # Guardar con formato apropiado
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        json.dump(documento, f, indent=2, ensure_ascii=False)

    print(f"✅ Documento de esquema universal guardado: {ruta_salida}")
    return ruta_salida

# Ejemplo de uso con tu extracción existente
def ejemplo_modificacion_funcion_extraccion():
    """Ejemplo de cómo modificar tu función de extracción existente"""

    def tu_funcion_extraccion_modificada(ruta_pdf: Path):
        """Tu función de extracción DESPUÉS de añadir esquema universal"""

        # Tu lógica de extracción existente (¡SIN CAMBIOS!)
        resultados = {
            "document_metadata": {
                "document_file": "Anexos-EAF-089-2025.pdf",
                "page_number": 75
            },
            "upper_table": {
                "rows": [
                    {"central": "Central Solar Manzanares", "potencia": "245.5"},
                    {"central": "Parque Eólico Burgos", "potencia": "180.0"}
                ]
            },
            "system_metrics": {
                "generacion_total": 840.5
            }
        }

        # NUEVO: Envolver en esquema universal
        documento_universal = crear_documento_universal(
            datos_extraccion=resultados,
            titulo_documento="ANEXO 2 - Generación Real",
            fecha_documento="2025-02-25",
            tipo_documento="anexo_02_generacion_real",
            dominio="operaciones",
            puntuacion_confianza=0.92
        )

        # NUEVO: Guardar versión de esquema universal
        ruta_salida = Path(f"output/{documento_universal['@id'].replace(':', '_')}.json")
        guardar_json_esquema_universal(documento_universal, ruta_salida)

        return documento_universal  # Ahora retorna datos compatibles con esquema!

    return tu_funcion_extraccion_modificada

if __name__ == "__main__":
    import re

    print("🇪🇸 Sistema de Esquema Universal Español")
    print("=" * 50)

    # Datos de ejemplo
    datos_ejemplo = {
        "upper_table": {
            "rows": [
                {"central": "Central Solar Manzanares", "empresa": "Iberdrola Renovables S.A.", "potencia": "245.5"},
                {"central": "Parque Eólico Burgos", "empresa": "Acciona Energía S.A.", "potencia": "180.0"}
            ]
        }
    }

    # Crear documento universal
    doc_universal = crear_documento_universal(
        datos_extraccion=datos_ejemplo,
        titulo_documento="ANEXO 2 - Generación Real",
        fecha_documento="2025-02-25",
        tipo_documento="anexo_02_generacion_real"
    )

    print(f"📄 Documento ID: {doc_universal['@id']}")
    print(f"🏭 Centrales extraídas: {len(doc_universal['entidades']['centrales_electricas'])}")
    print(f"🏢 Empresas extraídas: {len(doc_universal['entidades']['empresas'])}")
    print("✅ Esquema universal español creado correctamente")