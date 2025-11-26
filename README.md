# Sistema de Comparación de Documentos PDF con IA

Sistema web que compara documentos PDF y genera explicaciones inteligentes sobre las diferencias entre ellos, especialmente útil para identificar cambios en reglamentaciones y normas. Incluye un chatbot interactivo para hacer preguntas sobre la comparación realizada.

## 🚀 Características

- 📄 **Comparación de documentos PDF** - Analiza diferencias línea por línea
- 🤖 **Explicaciones generadas por IA** - Resúmenes inteligentes de los cambios
- 💬 **Chatbot interactivo** - Haz preguntas sobre la comparación realizada
- 🔍 **Identificación de cambios** - Detecta agregados, eliminados y modificaciones
- 📊 **Estadísticas detalladas** - Métricas de similitud y diferencias
- 🌐 **Interfaz web moderna** - Diseño responsive y fácil de usar

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.14+** - Lenguaje de programación principal
- **FastAPI 0.104.1** - Framework web moderno y rápido para APIs
- **Uvicorn 0.24.0** - Servidor ASGI de alto rendimiento
- **OpenAI API (1.3.5)** - Integración con GPT-4o-mini para explicaciones y chatbot
- **pdfplumber 0.10.3** - Extracción de texto de documentos PDF
- **PyPDF2 3.0.1** - Procesamiento adicional de PDFs
- **python-dotenv 1.0.0** - Manejo de variables de entorno
- **python-multipart 0.0.6** - Manejo de archivos multipart/form-data
- **httpx 0.27.2** - Cliente HTTP asíncrono (compatible con OpenAI)

### Frontend
- **HTML5** - Estructura de la interfaz
- **CSS3** - Estilos modernos con gradientes y animaciones
- **JavaScript (Vanilla)** - Interactividad y comunicación con la API
- **Fetch API** - Peticiones HTTP asíncronas

### Librerías de Procesamiento
- **difflib** - Comparación de secuencias de texto (incluida en Python)
- **pdfminer.six** - Motor de extracción de texto de PDFs

## 📋 Requisitos Previos

- Python 3.14 o superior
- pip (gestor de paquetes de Python)
- Clave API de OpenAI (obtener en https://platform.openai.com/api-keys)
- Navegador web moderno (Chrome, Firefox, Edge, etc.)

## 📦 Instalación

### Paso 1: Clonar o descargar el proyecto

Si tienes el proyecto en una carpeta, navega a ella:
```bash
cd C:\pdf-comparator
```

### Paso 2: Crear entorno virtual (recomendado)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar la clave API de OpenAI

Tienes dos opciones:

**Opción A: Usar el archivo start.bat (Windows)**
El archivo `start.bat` ya está configurado con la clave API. Solo ejecútalo.

**Opción B: Crear archivo .env**
Crea un archivo `.env` en la raíz del proyecto:
```
OPENAI_API_KEY=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
```

**Opción C: Variable de entorno del sistema**
Configura la variable de entorno `OPENAI_API_KEY` en tu sistema operativo.

## 🚀 Ejecución del Proyecto

### Método 1: Usando start.bat (Windows - Más fácil)

1. Abre una terminal (CMD o PowerShell)
2. Navega a la carpeta del proyecto:
   ```cmd
   cd C:\pdf-comparator
   ```
3. Ejecuta el archivo batch:
   ```cmd
   start.bat
   ```
4. El servidor se iniciará automáticamente en `http://localhost:8000`

### Método 2: Ejecución manual (Windows)

**PowerShell:**
```powershell
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Configurar variable de entorno
$env:OPENAI_API_KEY='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'

# Iniciar servidor
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**CMD:**
```cmd
# Activar entorno virtual
venv\Scripts\activate.bat

# Configurar variable de entorno e iniciar servidor
set OPENAI_API_KEY=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 && python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Linux/Mac:**
```bash
# Activar entorno virtual
source venv/bin/activate

# Configurar variable de entorno
export OPENAI_API_KEY='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'

# Iniciar servidor
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Método 3: Ejecutar main.py directamente

```bash
python main.py
```

## 💻 Ejecución en Visual Studio Code

### Paso 1: Abrir el proyecto en VS Code

1. Abre Visual Studio Code
2. Ve a `File > Open Folder...`
3. Selecciona la carpeta `C:\pdf-comparator`
4. Espera a que VS Code cargue el proyecto

### Paso 2: Configurar el entorno virtual

1. Presiona `Ctrl + Shift + P` (o `Cmd + Shift + P` en Mac)
2. Escribe "Python: Select Interpreter"
3. Selecciona el intérprete del entorno virtual:
   - `.\venv\Scripts\python.exe` (Windows)
   - `./venv/bin/python` (Linux/Mac)

### Paso 3: Configurar variables de entorno

**Opción A: Crear archivo .env**
1. Crea un archivo `.env` en la raíz del proyecto
2. Agrega:
   ```
   OPENAI_API_KEY=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
   ```

**Opción B: Configurar en launch.json**
1. Ve a la pestaña "Run and Debug" (Ctrl + Shift + D)
2. Clic en "create a launch.json file"
3. Selecciona "Python"
4. Modifica el archivo `.vscode/launch.json`:
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: FastAPI",
               "type": "python",
               "request": "launch",
               "program": "${workspaceFolder}/main.py",
               "console": "integratedTerminal",
               "env": {
                   "OPENAI_API_KEY": "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"
               }
           }
       ]
   }
   ```

### Paso 4: Ejecutar el proyecto

**Método A: Usando la terminal integrada**
1. Abre la terminal integrada (`Ctrl + ` ` o `View > Terminal`)
2. Activa el entorno virtual:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
3. Ejecuta:
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

**Método B: Usando el botón de ejecutar**
1. Presiona `F5` o ve a `Run > Start Debugging`
2. El servidor se iniciará automáticamente

**Método C: Usando la extensión de Python**
1. Instala la extensión "Python" de Microsoft si no la tienes
2. Abre `main.py`
3. Clic en el botón "Run Python File" en la esquina superior derecha

### Paso 5: Abrir en el navegador

1. Una vez iniciado el servidor, verás en la terminal:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```
2. Abre tu navegador y ve a: `http://localhost:8000`

## 📁 Estructura del Proyecto

```
pdf-comparator/
│
├── main.py                      # Servidor FastAPI principal
├── pdf_processor.py             # Módulo para procesar PDFs
├── document_comparator.py       # Lógica de comparación de documentos
├── ai_explainer.py              # Integración con OpenAI para explicaciones y chatbot
├── requirements.txt             # Dependencias del proyecto
├── start.bat                    # Script de inicio para Windows
├── start.sh                     # Script de inicio para Linux/Mac
├── README.md                    # Este archivo
│
├── static/                      # Archivos estáticos
│   └── index.html              # Interfaz web principal
│
├── uploads/                     # Carpeta temporal para archivos subidos
│
└── venv/                        # Entorno virtual (no incluir en git)
```

## 🔧 Endpoints de la API

### GET `/`
Página principal con la interfaz web.

### POST `/api/compare`
Compara dos documentos PDF.

**Parámetros:**
- `file1`: Archivo PDF (multipart/form-data)
- `file2`: Archivo PDF (multipart/form-data)
- `generate_explanation`: Boolean (opcional, default: true)

**Respuesta:**
```json
{
    "success": true,
    "comparison": {
        "document1": {...},
        "document2": {...},
        "differences": [...],
        "statistics": {...},
        "similarity_ratio": 0.95
    },
    "explanation": "Explicación generada por IA..."
}
```

### POST `/api/chat`
Chatbot para hacer preguntas sobre la última comparación.

**Body (JSON):**
```json
{
    "message": "¿Qué documento es más actualizado?"
}
```

**Respuesta:**
```json
{
    "success": true,
    "response": "Respuesta del chatbot..."
}
```

### GET `/api/health`
Verifica el estado del servidor.

**Respuesta:**
```json
{
    "status": "ok",
    "ai_available": true,
    "comparison_available": false
}
```

## 🐛 Solución de Problemas

### Error: "OPENAI_API_KEY no está configurada"
**Solución:** Asegúrate de configurar la variable de entorno o crear el archivo `.env` con tu clave API.

### Error: "Connection error" al usar la IA
**Solución:** 
1. Verifica tu conexión a internet
2. Confirma que la clave API sea válida
3. Verifica que tengas créditos en tu cuenta de OpenAI

### Error: "No se puede acceder a este sitio web"
**Solución:**
1. Verifica que el servidor esté ejecutándose
2. Confirma que el puerto 8000 no esté en uso
3. Intenta acceder a `http://127.0.0.1:8000` en lugar de `localhost`

### Error al instalar dependencias
**Solución:**
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### El servidor no inicia
**Solución:**
1. Verifica que Python 3.14+ esté instalado: `python --version`
2. Asegúrate de estar en el entorno virtual
3. Revisa los logs de error en la terminal

## 🛑 Detener el Servidor

**Windows (PowerShell/CMD):**
```powershell
Get-Process python | Stop-Process
```

**Linux/Mac:**
```bash
# En la terminal donde está corriendo, presiona Ctrl + C
# O encuentra el proceso:
ps aux | grep uvicorn
kill <PID>
```

## 📝 Notas Importantes

- Los archivos PDF subidos se eliminan automáticamente después de la comparación
- La última comparación se mantiene en memoria para el chatbot
- El servidor debe reiniciarse si cambias la clave API
- Para producción, considera usar variables de entorno del sistema en lugar de archivos `.env`

## 📄 Licencia

Este proyecto es de uso libre para fines educativos y comerciales.

## 👥 Soporte

Para problemas o preguntas, revisa la sección de "Solución de Problemas" o consulta la documentación de las tecnologías utilizadas.

---

**Desarrollado con ❤️ usando FastAPI, OpenAI y Python**
