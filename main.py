"""
Servidor principal FastAPI para el sistema de comparación de PDFs
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import shutil
from pathlib import Path
from typing import Optional
import uvicorn

from document_comparator import DocumentComparator
from ai_explainer import AIExplainer
from document_chatbot import DocumentChatbot


class ChatRequest(BaseModel):
    question: str

app = FastAPI(title="Sistema de Comparación de PDFs con IA")

# Crear directorios necesarios
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
STATIC_DIR = Path("static")
STATIC_DIR.mkdir(exist_ok=True)

# Montar directorio estático
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inicializar componentes
comparator = DocumentComparator()
explainer = None
chatbot = None

# Almacenar documentos comparados en memoria (por sesión)
current_comparison = None
current_document_texts = {}

try:
    explainer = AIExplainer()
except Exception as e:
    print(f"Advertencia: No se pudo inicializar AIExplainer: {e}")
    print("El sistema funcionará pero sin explicaciones de IA")

try:
    chatbot = DocumentChatbot()
except Exception as e:
    print(f"Advertencia: No se pudo inicializar DocumentChatbot: {e}")
    print("El sistema funcionará pero sin chatbot")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Página principal"""
    html_file = STATIC_DIR / "index.html"
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return get_default_html()


@app.post("/api/compare")
async def compare_documents(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    generate_explanation: bool = Form(True)
):
    """
    Endpoint para comparar dos documentos PDF
    """
    # Validar que sean PDFs
    if not file1.filename.endswith('.pdf') or not file2.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Ambos archivos deben ser PDFs")
    
    # Guardar archivos temporalmente
    file1_path = UPLOAD_DIR / f"temp_{file1.filename}"
    file2_path = UPLOAD_DIR / f"temp_{file2.filename}"
    
    try:
        # Guardar archivo 1
        with open(file1_path, "wb") as buffer:
            shutil.copyfileobj(file1.file, buffer)
        
        # Guardar archivo 2
        with open(file2_path, "wb") as buffer:
            shutil.copyfileobj(file2.file, buffer)
        
        # Comparar documentos
        comparison_result = comparator.compare_documents(
            str(file1_path),
            str(file2_path)
        )
        
        # Extraer textos completos para el chatbot
        from pdf_processor import PDFProcessor
        processor = PDFProcessor()
        doc1_text = processor.extract_text(str(file1_path))['full_text']
        doc2_text = processor.extract_text(str(file2_path))['full_text']
        
        # Guardar en memoria para el chatbot
        global current_comparison, current_document_texts
        current_comparison = comparison_result
        current_document_texts = {
            'document1': doc1_text,
            'document2': doc2_text
        }
        
        # Limpiar historial del chatbot para nueva comparación
        if chatbot:
            chatbot.clear_history()
        
        # Generar explicación con IA si está disponible
        explanation = None
        if generate_explanation and explainer:
            try:
                explanation = explainer.explain_differences(comparison_result)
            except Exception as e:
                explanation = f"Error al generar explicación: {str(e)}"
        
        # Preparar respuesta
        response = {
            "success": True,
            "comparison": comparison_result,
            "explanation": explanation
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al comparar documentos: {str(e)}")
    
    finally:
        # Limpiar archivos temporales
        if file1_path.exists():
            file1_path.unlink()
        if file2_path.exists():
            file2_path.unlink()


@app.get("/api/health")
async def health_check():
    """Endpoint de salud del sistema"""
    return {
        "status": "ok",
        "ai_available": explainer is not None,
        "chatbot_available": chatbot is not None
    }


@app.post("/api/chat")
async def chat_with_documents(request: ChatRequest):
    """
    Endpoint para hacer preguntas al chatbot sobre los documentos
    """
    if not chatbot:
        raise HTTPException(
            status_code=503, 
            detail="Chatbot no está disponible. Verifica que OPENAI_API_KEY esté configurada."
        )
    
    if not current_comparison:
        raise HTTPException(
            status_code=400,
            detail="No hay documentos comparados. Por favor compara documentos primero."
        )
    
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía")
    
    try:
        answer = chatbot.ask_question(
            question=question,
            comparison_result=current_comparison,
            document_texts=current_document_texts
        )
        
        return JSONResponse(content={
            "success": True,
            "answer": answer,
            "question": question
        })
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la pregunta: {str(e)}"
        )


def get_default_html():
    """HTML por defecto si no existe el archivo estático"""
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comparador de PDFs con IA</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .upload-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .upload-box {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            transition: all 0.3s;
            background: #f8f9ff;
        }
        
        .upload-box:hover {
            border-color: #764ba2;
            background: #f0f2ff;
        }
        
        .upload-box.dragover {
            border-color: #764ba2;
            background: #e8ebff;
        }
        
        .upload-box h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .file-input {
            display: none;
        }
        
        .file-label {
            display: inline-block;
            padding: 12px 30px;
            background: #667eea;
            color: white;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }
        
        .file-label:hover {
            background: #764ba2;
            transform: translateY(-2px);
        }
        
        .file-name {
            margin-top: 15px;
            color: #666;
            font-size: 0.9em;
        }
        
        .compare-button {
            width: 100%;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.3em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 20px;
        }
        
        .compare-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .compare-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .results {
            margin-top: 40px;
            display: none;
        }
        
        .results.show {
            display: block;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: #f8f9ff;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
        
        .stat-card h4 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .stat-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #764ba2;
        }
        
        .explanation {
            background: #f8f9ff;
            padding: 30px;
            border-radius: 12px;
            margin-top: 30px;
            border-left: 5px solid #667eea;
        }
        
        .explanation h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .explanation-content {
            line-height: 1.8;
            color: #333;
            white-space: pre-wrap;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            border-left: 5px solid #c33;
        }
        
        .chatbot-container {
            margin-top: 40px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
            display: none;
        }
        
        .chatbot-container.show {
            display: block;
        }
        
        .chatbot-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .chatbot-header h3 {
            margin: 0;
            font-size: 1.3em;
        }
        
        .chatbot-answer-box {
            padding: 25px;
            background: #f8f9ff;
            border-bottom: 2px solid #e0e0e0;
            min-height: 100px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .chatbot-answer-box.empty {
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-style: italic;
        }
        
        .chatbot-answer-content {
            line-height: 1.8;
            color: #333;
            white-space: pre-wrap;
        }
        
        .chatbot-input-area {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .chatbot-input-wrapper {
            display: flex;
            gap: 10px;
            align-items: flex-end;
        }
        
        .chatbot-input {
            flex: 1;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1em;
            font-family: inherit;
            resize: none;
            min-height: 50px;
            max-height: 150px;
        }
        
        .chatbot-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .chatbot-send-btn {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            white-space: nowrap;
        }
        
        .chatbot-send-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .chatbot-send-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .chatbot-loading {
            text-align: center;
            padding: 20px;
            color: #667eea;
            display: none;
        }
        
        .chatbot-loading.show {
            display: block;
        }
        
        .chatbot-message {
            margin-bottom: 15px;
            padding: 12px 15px;
            border-radius: 10px;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .chatbot-message.user {
            background: #e3f2fd;
            margin-left: 20%;
            text-align: right;
        }
        
        .chatbot-message.assistant {
            background: #f5f5f5;
            margin-right: 20%;
        }
        
        .chatbot-message-label {
            font-size: 0.8em;
            font-weight: bold;
            margin-bottom: 5px;
            opacity: 0.7;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 Comparador de PDFs con IA</h1>
            <p>Identifica cambios en reglamentaciones y normas con explicaciones inteligentes</p>
        </div>
        
        <div class="content">
            <form id="compareForm">
                <div class="upload-section">
                    <div class="upload-box" id="uploadBox1">
                        <h3>📄 Documento 1</h3>
                        <input type="file" id="file1" class="file-input" accept=".pdf" required>
                        <label for="file1" class="file-label">Seleccionar PDF</label>
                        <div class="file-name" id="fileName1"></div>
                    </div>
                    
                    <div class="upload-box" id="uploadBox2">
                        <h3>📄 Documento 2</h3>
                        <input type="file" id="file2" class="file-input" accept=".pdf" required>
                        <label for="file2" class="file-label">Seleccionar PDF</label>
                        <div class="file-name" id="fileName2"></div>
                    </div>
                </div>
                
                <button type="submit" class="compare-button" id="compareBtn">
                    🔍 Comparar Documentos
                </button>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Procesando documentos y generando explicación...</p>
            </div>
            
            <div class="error" id="error" style="display: none;"></div>
            
            <div class="chatbot-container" id="chatbotContainer">
                <div class="chatbot-header">
                    <span>🤖</span>
                    <h3>Asistente de Documentos - Haz preguntas sobre la comparación</h3>
                </div>
                <div class="chatbot-answer-box" id="chatbotAnswerBox">
                    <div class="chatbot-answer-content" id="chatbotAnswerContent">
                        <div class="chatbot-message assistant">
                            <div class="chatbot-message-label">Asistente</div>
                            <div>Hola! Puedo ayudarte a entender las diferencias entre los documentos comparados. ¿Qué te gustaría saber?</div>
                        </div>
                    </div>
                </div>
                <div class="chatbot-loading" id="chatbotLoading">
                    <div class="spinner" style="width: 30px; height: 30px; border-width: 3px;"></div>
                    <p>Pensando...</p>
                </div>
                <div class="chatbot-input-area">
                    <div class="chatbot-input-wrapper">
                        <textarea 
                            id="chatbotInput" 
                            class="chatbot-input" 
                            placeholder="Escribe tu pregunta sobre los documentos comparados..."
                            rows="2"
                        ></textarea>
                        <button id="chatbotSendBtn" class="chatbot-send-btn">Enviar</button>
                    </div>
                </div>
            </div>
            
            <div class="results" id="results">
                <div class="stats" id="stats"></div>
                <div class="explanation" id="explanation"></div>
            </div>
        </div>
    </div>
    
    <script>
        const form = document.getElementById('compareForm');
        const file1Input = document.getElementById('file1');
        const file2Input = document.getElementById('file2');
        const fileName1 = document.getElementById('fileName1');
        const fileName2 = document.getElementById('fileName2');
        const compareBtn = document.getElementById('compareBtn');
        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        const errorDiv = document.getElementById('error');
        const statsDiv = document.getElementById('stats');
        const explanationDiv = document.getElementById('explanation');
        
        // Mostrar nombre de archivo seleccionado
        file1Input.addEventListener('change', (e) => {
            fileName1.textContent = e.target.files[0]?.name || '';
        });
        
        file2Input.addEventListener('change', (e) => {
            fileName2.textContent = e.target.files[0]?.name || '';
        });
        
        // Manejar envío del formulario
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const file1 = file1Input.files[0];
            const file2 = file2Input.files[0];
            
            if (!file1 || !file2) {
                showError('Por favor selecciona ambos archivos PDF');
                return;
            }
            
            // Mostrar loading
            loading.classList.add('show');
            results.classList.remove('show');
            errorDiv.style.display = 'none';
            compareBtn.disabled = true;
            
            // Preparar FormData
            const formData = new FormData();
            formData.append('file1', file1);
            formData.append('file2', file2);
            formData.append('generate_explanation', 'true');
            
            try {
                const response = await fetch('/api/compare', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.detail || 'Error al comparar documentos');
                }
                
                // Mostrar resultados
                displayResults(data);
                
                // Mostrar chatbot después de comparar
                document.getElementById('chatbotContainer').classList.add('show');
                
            } catch (error) {
                showError('Error: ' + error.message);
            } finally {
                loading.classList.remove('show');
                compareBtn.disabled = false;
            }
        });
        
        function displayResults(data) {
            const comparison = data.comparison;
            const stats = comparison.statistics;
            
            // Mostrar estadísticas
            statsDiv.innerHTML = `
                <div class="stat-card">
                    <h4>Similitud</h4>
                    <div class="value">${(comparison.similarity_ratio * 100).toFixed(1)}%</div>
                </div>
                <div class="stat-card">
                    <h4>Total Diferencias</h4>
                    <div class="value">${stats.total_differences}</div>
                </div>
                <div class="stat-card">
                    <h4>Agregadas</h4>
                    <div class="value">${stats.added_sections}</div>
                </div>
                <div class="stat-card">
                    <h4>Eliminadas</h4>
                    <div class="value">${stats.deleted_sections}</div>
                </div>
                <div class="stat-card">
                    <h4>Modificadas</h4>
                    <div class="value">${stats.modified_sections}</div>
                </div>
            `;
            
            // Mostrar explicación
            if (data.explanation) {
                explanationDiv.innerHTML = `
                    <h3>🤖 Explicación de las Diferencias (IA)</h3>
                    <div class="explanation-content">${data.explanation}</div>
                `;
            } else {
                explanationDiv.innerHTML = `
                    <h3>⚠️ Explicación no disponible</h3>
                    <p>La explicación con IA no está disponible. Verifica que OPENAI_API_KEY esté configurada.</p>
                `;
            }
            
            results.classList.add('show');
        }
        
        function showError(message) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
        
        // ========== CHATBOT FUNCTIONALITY ==========
        const chatbotContainer = document.getElementById('chatbotContainer');
        const chatbotInput = document.getElementById('chatbotInput');
        const chatbotSendBtn = document.getElementById('chatbotSendBtn');
        const chatbotAnswerContent = document.getElementById('chatbotAnswerContent');
        const chatbotLoading = document.getElementById('chatbotLoading');
        
        // Enviar pregunta al presionar Enter (Shift+Enter para nueva línea)
        chatbotInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatbotQuestion();
            }
        });
        
        // Enviar pregunta al hacer clic en el botón
        chatbotSendBtn.addEventListener('click', sendChatbotQuestion);
        
        // Auto-resize del textarea
        chatbotInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        async function sendChatbotQuestion() {
            const question = chatbotInput.value.trim();
            
            if (!question) {
                return;
            }
            
            // Deshabilitar input y botón
            chatbotInput.disabled = true;
            chatbotSendBtn.disabled = true;
            
            // Mostrar pregunta del usuario
            addChatbotMessage('user', question);
            
            // Limpiar input
            chatbotInput.value = '';
            chatbotInput.style.height = 'auto';
            
            // Mostrar loading
            chatbotLoading.classList.add('show');
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ question: question })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.detail || 'Error al procesar la pregunta');
                }
                
                // Mostrar respuesta
                addChatbotMessage('assistant', data.answer);
                
            } catch (error) {
                addChatbotMessage('assistant', 'Error: ' + error.message);
            } finally {
                // Habilitar input y botón
                chatbotInput.disabled = false;
                chatbotSendBtn.disabled = false;
                chatbotLoading.classList.remove('show');
                chatbotInput.focus();
            }
        }
        
        function addChatbotMessage(role, content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `chatbot-message ${role}`;
            
            const label = document.createElement('div');
            label.className = 'chatbot-message-label';
            label.textContent = role === 'user' ? 'Tú' : 'Asistente';
            
            const contentDiv = document.createElement('div');
            contentDiv.textContent = content;
            
            messageDiv.appendChild(label);
            messageDiv.appendChild(contentDiv);
            
            chatbotAnswerContent.appendChild(messageDiv);
            
            // Scroll al final
            chatbotAnswerContent.scrollTop = chatbotAnswerContent.scrollHeight;
        }
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

