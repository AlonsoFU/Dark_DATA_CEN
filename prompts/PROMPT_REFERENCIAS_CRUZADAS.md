# PROMPT REFERENCIAS CRUZADAS

## 📋 INSTRUCCIONES PARA IA

```
Analiza este documento JSON y genera referencias cruzadas automáticas.

DOCUMENTO A ANALIZAR:
[PEGAR AQUÍ EL DOCUMENTO JSON UNIVERSAL]

## ✅ GENERA REFERENCIAS SIGUIENDO ESTAS REGLAS:

### Reglas temporales:
- Misma fecha → documentos operativos relacionados

### Reglas por entidades:
- Centrales compartidas → vínculos operacionales
- Empresas compartidas → vínculos corporativos

### Reglas de dominio:
- Solar/Eólica → impacta precios mercado
- ERNC → debe cumplir normativa legal
- Incidentes → afecta mercado y requiere reportes

## 📄 FORMATO DE SALIDA:

Devuelve SOLO este array JSON:

```json
[
  {
    "documento_objetivo": "doc:mercados:precios_spot:2025-01-15",
    "dominio_objetivo": "mercados",
    "tipo_relacion": "IMPACTA_PRECIO",
    "confianza": 0.85,
    "contexto": "Generación solar afecta precios mediodía",
    "automatico": true
  },
  {
    "documento_objetivo": "doc:legal:normativa_ernc:2025-01-15",
    "dominio_objetivo": "legal",
    "tipo_relacion": "DEBE_CUMPLIR_NORMATIVA",
    "confianza": 0.90,
    "contexto": "Centrales ERNC deben cumplir cuotas",
    "automatico": true
  }
]
```

## 🎯 TIPOS DE RELACIÓN VÁLIDOS:

- `IMPACTA_PRECIO` - Afecta precios de mercado
- `REFERENCIA_ENTIDAD` - Comparte entidades
- `DEBE_CUMPLIR_NORMATIVA` - Requiere cumplimiento legal
- `MISMA_FECHA_OPERATIVA` - Documentos del mismo día
- `CAUSA_ALTERACION` - Genera cambios en sistema

NO generes explicaciones, SOLO el array JSON de referencias.
```

## 🎯 USO

1. Copia este prompt
2. Pega tu documento JSON universal
3. La IA devuelve array de referencias_cruzadas
4. Integra el array en tu documento principal