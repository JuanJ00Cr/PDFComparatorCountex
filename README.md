# Sistema de Comparación de Documentos PDF con IA

Sistema que compara documentos PDF y genera explicaciones inteligentes sobre las diferencias entre ellos, especialmente útil para identificar cambios en reglamentaciones y normas.

## 📋 Requisitos Previos

1. **Python 3.8 o superior** - Si no lo tienes instalado:
   - Descarga desde: https://www.python.org/downloads/
   - O instala desde Microsoft Store (Windows)
   - **IMPORTANTE**: Al instalar, marca la opción "Add Python to PATH"

2. **API Key de OpenAI** (opcional, para explicaciones con IA):
   - Obtén tu API key en: https://platform.openai.com/api-keys
   - Crea un archivo `.env` en este directorio con:
     ```
     OPENAI_API_KEY=tu_api_key_aqui
     ```

## 🚀 Instalación

1. Abre una terminal en este directorio (`pdf-comparator`)

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
   
   O si tienes Python 3 específicamente:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

## ▶️ Uso

1. Inicia el servidor:
   ```bash
   python main.py
   ```
   
   O:
   ```bash
   python3 main.py
   ```

2. Abre tu navegador en: **http://localhost:8000**

3. Sube dos documentos PDF y haz clic en "Comparar Documentos"

## 📁 Estructura del Proyecto

```
pdf-comparator/
├── main.py                 # Servidor FastAPI principal
├── pdf_processor.py        # Extracción de texto de PDFs
├── document_comparator.py  # Lógica de comparación
├── ai_explainer.py         # Integración con OpenAI
├── requirements.txt        # Dependencias
├── README.md              # Este archivo
├── .env                   # Variables de entorno (crear manualmente)
├── static/                # Archivos estáticos
└── uploads/               # PDFs temporales (se crea automáticamente)
```

## ⚠️ Solución de Problemas

### Error: "No se puede acceder a este sitio web" o "ERR_CONNECTION_REFUSED"

**Causa**: El servidor no está corriendo.

**Solución**:
1. Asegúrate de estar en el directorio `pdf-comparator`
2. Ejecuta: `python main.py`
3. Espera a ver el mensaje: "Uvicorn running on http://127.0.0.1:8000"
4. Luego abre http://localhost:8000 en tu navegador

### Error: "Python no se encontró"

**Solución**:
1. Instala Python desde https://www.python.org/downloads/
2. Durante la instalación, marca "Add Python to PATH"
3. Reinicia la terminal
4. Verifica con: `python --version`

### Error al instalar dependencias

**Solución**:
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### La explicación con IA no funciona

**Solución**:
1. Crea un archivo `.env` en este directorio
2. Agrega: `OPENAI_API_KEY=tu_api_key_aqui`
3. Reinicia el servidor

## 🔧 Características

- ✅ Comparación línea por línea de documentos PDF
- ✅ Detección de cambios (agregados, eliminados, modificados)
- ✅ Estadísticas de similitud
- ✅ Explicaciones inteligentes con IA (requiere API key)
- ✅ Interfaz web moderna y fácil de usar
- ✅ Identificación de secciones (artículos, capítulos, etc.)

## 📝 Notas

- El sistema funciona sin API key de OpenAI, pero sin las explicaciones de IA
- Los PDFs subidos se procesan temporalmente y se eliminan después
- El servidor corre en `localhost:8000` por defecto

