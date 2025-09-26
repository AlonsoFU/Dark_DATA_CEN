# PROMPT TEMPLATE PARA IA - Sistema Eléctrico Chileno

## 📋 COPIA Y PEGA ESTE PROMPT

```
INSTRUCCIONES CRÍTICAS PARA GENERACIÓN DE CÓDIGO:

Estás ayudando con el sistema eléctrico chileno. Cuando generes código de extracción de documentos, DEBES seguir estas reglas EXACTAS:

## ✅ ESTRUCTURA JSON OBLIGATORIA

TODO código que generes DEBE producir esta estructura JSON EXACTA:

```json
{
  "@context": "https://coordinador.cl/context/v1",
  "@id": "cen:{dominio}:{tipo_documento}:{fecha}",
  "@type": "DocumentoSistemaElectricoChile",

  "metadatos_universales": {
    "titulo": "TÍTULO_EXTRAÍDO",
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
        "nombre": "NOMBRE_EXACTO_EXTRAÍDO",
        "confianza": 0.95
      }
    ],
    "empresas": [
      {
        "@id": "cen:empresa:{nombre_normalizado}",
        "@type": "EmpresaElectricaChile",
        "nombre": "NOMBRE_EMPRESA_EXTRAÍDO",
        "confianza": 0.85
      }
    ],
    "ubicaciones": [],
    "regulaciones": [],
    "equipos": []
  },

  "referencias_cruzadas": [
    {
      "documento_objetivo": "cen:mercados:precios_spot:YYYY-MM-DD",
      "dominio_objetivo": "mercados",
      "tipo_relacion": "IMPACTA_PRECIO_MEDIODIA",
      "confianza": 0.85,
      "contexto": "Generación solar afecta precios mediodía",
      "sistema": "chileno",
      "automatico": true
    }
  ],

  "etiquetas_semanticas": [
    "chile",
    "sistema_electrico_nacional",
    "sen",
    "{dominio}",
    "etiquetas_específicas"
  ],

  "datos_especificos_dominio": {
    "{dominio}": {
      // AQUÍ van los datos de extracción originales
      // PRESERVAR la estructura que ya existe
    }
  },

  "metadatos_calidad": {
    "confianza_extraccion": 0.85,
    "estado_validacion": "aprobado",
    "metodo_procesamiento": "extraccion_automatizada_chilena",
    "sistema_electrico": "chileno"
  }
}
```

## 🇨🇱 CONTEXTO SISTEMA CHILENO

- **País**: Chile (NO España)
- **Sistema**: SEN (Sistema Eléctrico Nacional)
- **Regulador**: Coordinador Eléctrico Nacional (NO CNMC)
- **Empresas**: Enel Chile, Colbún, AES Gener, ENGIE, Statkraft
- **Tecnologías**: Solar, Eólica, Hidroeléctrica, Térmica, Biomasa, Geotermia

## 🚫 NUNCA HAGAS:
- Estructura JSON diferente
- Omitir campos obligatorios
- Usar país diferente a Chile
- Poner datos fuera de "datos_especificos_dominio"

## ✅ SIEMPRE INCLUYE:
- Las funciones helper para Chile
- Extracción automática de entidades
- IDs con formato "cen:tipo:nombre_normalizado"
- Contexto del sistema eléctrico chileno

## 🛠️ FUNCIONES HELPER OBLIGATORIAS:

```python
def determinar_tipo_central_chile(nombre: str) -> str:
    nombre_lower = nombre.lower()
    if "solar" in nombre_lower: return "CentralSolarChile"
    elif "eólica" in nombre_lower: return "CentralEolicaChile"
    elif "hidro" in nombre_lower: return "CentralHidroelectricaChile"
    elif "térmica" in nombre_lower: return "CentralTermicaChile"
    return "CentralElectricaChile"

def normalizar_nombre_chile(nombre: str) -> str:
    import re
    normalizado = re.sub(r'[^a-zA-ZáéíóúñÁÉÍÓÚÑ0-9\s]', '', nombre.lower())
    normalizado = normalizado.replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n')
    return re.sub(r'\s+', '_', normalizado.strip())

def extraer_entidades_chile(datos: dict) -> dict:
    entidades = {"centrales_electricas": [], "empresas": [], "ubicaciones": [], "regulaciones": [], "equipos": []}

    for tabla in ["upper_table", "lower_table"]:
        if tabla in datos and "rows" in datos[tabla]:
            for fila in datos[tabla]["rows"]:
                for campo in ["central", "planta", "generador", "nombre"]:
                    if campo in fila and fila[campo]:
                        nombre = fila[campo].strip()
                        if len(nombre) > 3:
                            entidades["centrales_electricas"].append({
                                "@id": f"cen:central:{normalizar_nombre_chile(nombre)}",
                                "@type": determinar_tipo_central_chile(nombre),
                                "nombre": nombre,
                                "confianza": 0.9
                            })

                for campo in ["empresa", "compañia", "operador"]:
                    if campo in fila and fila[campo]:
                        empresa = fila[campo].strip()
                        if len(empresa) > 3:
                            entidades["empresas"].append({
                                "@id": f"cen:empresa:{normalizar_nombre_chile(empresa)}",
                                "@type": "EmpresaElectricaChile",
                                "nombre": empresa,
                                "confianza": 0.85
                            })

    return entidades
```

AHORA genera el código siguiendo estas reglas EXACTAS.
```

## 🎯 CÓMO USAR ESTE PROMPT

### Para Cualquier IA (ChatGPT, Claude, etc.):

1. **Copia el prompt de arriba**
2. **Pégalo al inicio de tu conversación**
3. **Luego pide**: "Genera código para extraer datos del ANEXO 2 de generación real"

### Ejemplo de Uso:
```
[PEGAR TODO EL PROMPT DE ARRIBA]

Ahora ayúdame a crear código para extraer datos de un PDF del ANEXO 2 - Generación Real del sistema eléctrico chileno. El código debe leer tablas con información de centrales eléctricas y generar la estructura JSON que especifiqué arriba.
```

### La IA Automáticamente Generará:
- ✅ Código que produce estructura JSON exacta
- ✅ Funciones helper incluidas
- ✅ Extracción automática de entidades chilenas
- ✅ IDs con formato correcto
- ✅ Contexto del sistema chileno

## 📁 DÓNDE GUARDAR ESTE PROMPT

1. **En tu repositorio**: Para que siempre esté disponible
2. **En tus notas**: Para copiar/pegar rápidamente
3. **Como archivo de referencia**: Para entrenar nuevas IAs

## 🚀 RESULTADO

Cada vez que uses este prompt, la IA generará código que produce JSONs compatibles con:
- Tu sistema de esquema universal
- Referencias cruzadas automáticas
- Consultas de IA complejas
- Grafo de conocimiento del sistema eléctrico chileno

¡La IA sabrá **exactamente** qué estructura generar!