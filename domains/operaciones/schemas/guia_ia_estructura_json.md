# Guía para IA: Estructura JSON Obligatoria - Sistema Eléctrico Chileno

## 🎯 INSTRUCCIONES PARA IA

Cuando generes código de extracción para documentos del sistema eléctrico chileno, **SIEMPRE** debes generar código que produzca esta estructura JSON **EXACTA**:

## ✅ ESTRUCTURA JSON OBLIGATORIA

### Plantilla Base para Todos los Documentos
```json
{
  "@context": "https://coordinador.cl/context/v1",
  "@id": "cen:{dominio}:{tipo_documento}:{fecha}",
  "@type": "DocumentoSistemaElectricoChile",

  "metadatos_universales": {
    "titulo": "TITULO_EXTRAIDO_DEL_DOCUMENTO",
    "dominio": "operaciones|mercados|legal|planificacion",
    "tipo_documento": "anexo_01|anexo_02|informe_diario|etc",
    "fecha_creacion": "YYYY-MM-DD",
    "fecha_procesamiento": "TIMESTAMP_ISO",
    "idioma": "es",
    "version": "1.0",
    "estado": "final",
    "pais": "Chile",
    "regulador": "Coordinador Eléctrico Nacional",
    "sistema_electrico": "SEN"
  },

  "entidades": {
    "centrales_electricas": [
      {
        "@id": "cen:central:{nombre_normalizado}",
        "@type": "CentralSolarChile|CentralEolicaChile|CentralHidroelectricaChile|CentralTermicaChile",
        "nombre": "NOMBRE_EXTRAIDO_EXACTO",
        "confianza": 0.0-1.0
      }
    ],
    "empresas": [
      {
        "@id": "cen:empresa:{nombre_normalizado}",
        "@type": "EmpresaElectricaChile",
        "nombre": "NOMBRE_EMPRESA_EXTRAIDO",
        "confianza": 0.0-1.0
      }
    ],
    "ubicaciones": [],
    "regulaciones": [],
    "equipos": []
  },

  "referencias_cruzadas": [
    {
      "documento_objetivo": "cen:{dominio}:{tipo}:{fecha}",
      "dominio_objetivo": "operaciones|mercados|legal|planificacion",
      "tipo_relacion": "IMPACTA_PRECIO|REFERENCIA_CENTRAL|DEBE_CUMPLIR",
      "confianza": 0.0-1.0,
      "contexto": "Descripción de la relación",
      "sistema": "chileno",
      "automatico": true
    }
  ],

  "etiquetas_semanticas": [
    "chile",
    "sistema_electrico_nacional",
    "sen",
    "{dominio}",
    "etiquetas_especificas"
  ],

  "datos_especificos_dominio": {
    "{dominio}": {
      // AQUÍ van los datos de extracción originales del usuario
      // PRESERVAR estructura existente del usuario
    }
  },

  "metadatos_calidad": {
    "confianza_extraccion": 0.0-1.0,
    "estado_validacion": "aprobado",
    "metodo_procesamiento": "extraccion_automatizada_chilena",
    "sistema_electrico": "chileno"
  }
}
```

## 🚫 REGLAS ESTRICTAS PARA LA IA

### ❌ NUNCA HAGAS ESTO:
- Crear estructura JSON diferente
- Omitir campos obligatorios (@context, @id, @type, metadatos_universales, entidades, datos_especificos_dominio)
- Usar IDs que no sigan formato "cen:{tipo}:{nombre_normalizado}"
- Poner datos de extracción fuera de "datos_especificos_dominio"
- Usar países diferentes a "Chile"
- Usar reguladores diferentes a "Coordinador Eléctrico Nacional"

### ✅ SIEMPRE HAZ ESTO:
- Usar la plantilla exacta de arriba
- Preservar datos originales en "datos_especificos_dominio.{dominio}"
- Extraer entidades automáticamente a la sección "entidades"
- Generar IDs únicos con formato correcto
- Usar tipos de centrales chilenos (CentralSolarChile, etc.)
- Incluir contexto del sistema eléctrico chileno

## 🇨🇱 CONTEXTO SISTEMA ELÉCTRICO CHILENO

### Dominios Válidos:
- **operaciones**: Operación del SEN, generación, incidentes
- **mercados**: Precios spot, licitaciones, costos marginales
- **legal**: Regulaciones CNE, SEC, normativa eléctrica
- **planificacion**: Expansión transmisión, estudios, proyecciones

### Tipos de Centrales Chilenas:
- **CentralSolarChile**: Fotovoltaica, plantas solares
- **CentralEolicaChile**: Parques eólicos
- **CentralHidroelectricaChile**: Pasada, embalse, mini hidro
- **CentralTermicaChile**: Carbón, gas, petróleo, ciclo combinado
- **CentralBiomasaChile**: Biomasa, biogás
- **CentralGeotermicaChile**: Geotermia

### Empresas Principales:
- Enel (Enel Chile, Enel Green Power Chile)
- Colbún S.A.
- AES Gener
- ENGIE
- Statkraft
- Acciona Energía

### Regiones Principales:
- Antofagasta, Atacama, Coquimbo (Norte Grande/Chico)
- Valparaíso, Metropolitana, O'Higgins (Centro)
- Maule, Ñuble, Biobío, Araucanía (Centro-Sur)

## 📋 PLANTILLAS ESPECÍFICAS POR TIPO DE DOCUMENTO

### Para ANEXOS (anexo_01, anexo_02, etc):
```json
{
  "tipo_documento": "anexo_01_generacion_programada|anexo_02_generacion_real|anexo_03_etc",
  "etiquetas_semanticas": ["chile", "sen", "operaciones", "generacion_programada|generacion_real"],
  "datos_especificos_dominio": {
    "operaciones": {
      "upper_table": {/* tabla superior del anexo */},
      "lower_table": {/* tabla inferior del anexo */},
      "system_metrics": {/* métricas del sistema */}
    }
  }
}
```

### Para INFORMES DIARIOS:
```json
{
  "tipo_documento": "informe_diario_operacional",
  "etiquetas_semanticas": ["chile", "sen", "operaciones", "informe_diario", "tiempo_real"],
  "datos_especificos_dominio": {
    "operaciones": {
      "eventos_operacionales": [],
      "estado_sistema": {},
      "alertas": []
    }
  }
}
```

### Para DOCUMENTOS DE MERCADO:
```json
{
  "tipo_documento": "precios_spot_diarios|licitaciones|costos_marginales",
  "etiquetas_semanticas": ["chile", "sen", "mercados", "precios", "spot"],
  "datos_especificos_dominio": {
    "mercados": {
      "precios_por_hora": {},
      "costos_marginales": {},
      "demanda": {}
    }
  }
}
```

## 🤖 FUNCIONES DE AYUDA OBLIGATORIAS

Cuando generes código, **SIEMPRE** incluir estas funciones de ayuda:

```python
def determinar_tipo_central_chile(nombre_central: str) -> str:
    """Determinar tipo de central del sistema chileno"""
    nombre_lower = nombre_central.lower()
    if "solar" in nombre_lower or "fotovoltaica" in nombre_lower:
        return "CentralSolarChile"
    elif "eólica" in nombre_lower or "eolica" in nombre_lower:
        return "CentralEolicaChile"
    elif "hidro" in nombre_lower or "agua" in nombre_lower:
        return "CentralHidroelectricaChile"
    elif "térmica" in nombre_lower or "carbón" in nombre_lower or "gas" in nombre_lower:
        return "CentralTermicaChile"
    else:
        return "CentralElectricaChile"

def normalizar_nombre_chile(nombre: str) -> str:
    """Normalizar nombre para ID chileno"""
    import re
    normalizado = re.sub(r'[^a-zA-ZáéíóúñÁÉÍÓÚÑ0-9\s]', '', nombre.lower())
    normalizado = normalizado.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
    return re.sub(r'\s+', '_', normalizado.strip())

def generar_id_documento_chile(dominio: str, tipo_doc: str, fecha: str) -> str:
    """Generar ID único para documento chileno"""
    return f"cen:{dominio}:{tipo_doc}:{fecha}"

def extraer_entidades_automaticamente(datos_extraccion: dict) -> dict:
    """Extraer entidades de datos de extracción"""
    entidades = {"centrales_electricas": [], "empresas": [], "ubicaciones": [], "regulaciones": [], "equipos": []}

    # Buscar en tablas
    for tabla_key in ["upper_table", "lower_table"]:
        if tabla_key in datos_extraccion and "rows" in datos_extraccion[tabla_key]:
            for fila in datos_extraccion[tabla_key]["rows"]:
                for campo in ["central", "planta", "generador"]:
                    if campo in fila and fila[campo]:
                        nombre_central = fila[campo].strip()
                        if len(nombre_central) > 3:
                            entidades["centrales_electricas"].append({
                                "@id": f"cen:central:{normalizar_nombre_chile(nombre_central)}",
                                "@type": determinar_tipo_central_chile(nombre_central),
                                "nombre": nombre_central,
                                "confianza": 0.9
                            })

    return entidades
```

## 💡 EJEMPLO DE CÓDIGO GENERADO CORRECTO

```python
def extraer_anexo_con_estructura_universal(pdf_path: Path) -> dict:
    """Extraer anexo siguiendo estructura universal chilena"""

    # 1. Tu lógica de extracción existente
    datos_extraccion = {
        "upper_table": {"rows": [...]},
        "system_metrics": {...}
    }

    # 2. OBLIGATORIO: Convertir a estructura universal
    documento_universal = {
        "@context": "https://coordinador.cl/context/v1",
        "@id": generar_id_documento_chile("operaciones", "anexo_02_generacion_real", "2025-02-25"),
        "@type": "DocumentoSistemaElectricoChile",

        "metadatos_universales": {
            "titulo": "ANEXO 2 - Generación Real SEN",
            "dominio": "operaciones",
            "tipo_documento": "anexo_02_generacion_real",
            "fecha_creacion": "2025-02-25",
            "pais": "Chile",
            "regulador": "Coordinador Eléctrico Nacional",
            "sistema_electrico": "SEN"
        },

        "entidades": extraer_entidades_automaticamente(datos_extraccion),

        "etiquetas_semanticas": ["chile", "sen", "operaciones", "generacion_real"],

        "datos_especificos_dominio": {
            "operaciones": datos_extraccion  # PRESERVAR datos originales
        },

        "metadatos_calidad": {
            "confianza_extraccion": 0.85,
            "sistema_electrico": "chileno"
        }
    }

    return documento_universal
```

## 🎯 INSTRUCCIONES FINALES PARA LA IA

1. **SIEMPRE** usar la plantilla exacta de arriba
2. **NUNCA** inventar estructura diferente
3. **PRESERVAR** datos originales en "datos_especificos_dominio"
4. **EXTRAER** entidades automáticamente
5. **USAR** contexto del sistema eléctrico chileno
6. **INCLUIR** funciones de ayuda obligatorias
7. **GENERAR** código que produce esta estructura JSON exacta

¿Necesitas generar código de extracción? Usa esta guía como referencia obligatoria.