# Sindicato Chatbot - Versión Visual Profesional

Proyecto: Asesor Sindical Virtual (SUTET-SIMATOL)

Estructura:
- app.py : servidor Flask (visual + RAG + Ollama)
- rag_helper.py : utilidades RAG (FAISS + sentence-transformers)
- ingest.py : script para leer PDFs/TXT y construir índice
- templates/index.html : interfaz visual con logo y chat
- static/css/styles.css, static/js/chat.js : assets
- static/logo-simatol.png : logo institucional (si lo proveíste)
- data/docs/ : coloca aquí tus PDFs/TXT para indexar
- data/index/ : índice FAISS resultante
- requirements.txt : dependencias

Instrucciones rápidas:
1. Crear venv: python3 -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt
4. Instalar Ollama y descargar modelo (phi3). Iniciar: ollama serve &
5. (Opcional) Poner PDFs/TXT en data/docs/ y ejecutar: python3 ingest.py
6. Iniciar app: python3 app.py
7. Abrir http://127.0.0.1:5000

