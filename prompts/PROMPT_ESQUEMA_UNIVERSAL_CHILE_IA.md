# PROMPT ESQUEMA UNIVERSAL

## 📋 INSTRUCCIONES PARA IA

```
Cuando generes código de extracción de documentos, DEBES producir esta estructura JSON universal:

## ✅ ESTRUCTURA JSON UNIVERSAL

```json
{
  "@context": "https://schema.org/context/v1",
  "@id": "doc:{dominio}:{tipo_documento}:{fecha}",
  "@type": "DocumentoEstructurado",

  "metadatos_universales": {
    "titulo": "TÍTULO_EXTRAÍDO",
    "dominio": "DOMINIO_DEL_DOCUMENTO",
    "tipo_documento": "TIPO_ESPECÍFICO",
    "fecha_creacion": "YYYY-MM-DD",
    "idioma": "es"
  },

  "entidades": {
    "entidades_principales": [
      {
        "@id": "ent:{tipo}:{nombre_normalizado}",
        "@type": "TipoEntidad",
        "nombre": "NOMBRE_EXTRAÍDO",
        "confianza": 0.9
      }
    ],
    "organizaciones": [],
    "ubicaciones": [],
    "conceptos": []
  },

  "datos_especificos_dominio": {
    "{dominio}": {
      // PRESERVAR EXACTAMENTE los datos de extracción originales aquí
      // NO modificar la estructura del usuario
    }
  },

  "metadatos_calidad": {
    "confianza_extraccion": 0.85,
    "metodo_procesamiento": "extraccion_automatizada"
  }
}
```

## 🎯 CONTEXTO

- Información del sector eléctrico chileno
- Preservar datos originales en "datos_especificos_dominio"
- Extraer entidades automáticamente del contenido

## 📋 EJEMPLO DE USO:

```python
def extraer_documento_universal(pdf_path):
    # 1. Tu extracción existente (NO cambiar)
    datos_originales = {
        "upper_table": {"rows": [...]},
        "lower_table": {"rows": [...]}
    }

    # 2. Envolver en estructura universal
    documento = {
        "@context": "https://schema.org/context/v1",
        "@id": f"doc:{dominio}:{tipo}:{fecha}",
        "@type": "DocumentoEstructurado",

        "metadatos_universales": {
            "titulo": "TÍTULO EXTRAÍDO",
            "dominio": "DOMINIO_CORRESPONDIENTE",
            "tipo_documento": "TIPO_DOCUMENTO",
            "fecha_creacion": "2025-01-15",
            "idioma": "es"
        },

        "entidades": {
            # Extraer entidades del contenido automáticamente
        },

        "datos_especificos_dominio": {
            "dominio": datos_originales  # PRESERVAR aquí
        },

        "metadatos_calidad": {
            "confianza_extraccion": 0.85,
            "metodo_procesamiento": "extraccion_automatizada"
        }
    }

    return documento
```
```

## 🎯 USO

1. Copia este prompt
2. Pide: "Genera código para extraer [documento]"
3. La IA produce estructura JSON universal