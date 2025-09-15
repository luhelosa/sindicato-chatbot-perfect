from flask import Flask, request, jsonify, render_template
import requests
import ollama
from rag_helper import RAGRetriever, build_context
import os
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__, template_folder='templates', static_folder='static')
retriever = RAGRetriever()  # carga índice si existe

@app.route("/", methods=["GET"])
def home():
    estado = "✅ activo" if retriever.ready else "⚠️ sin índice (usa conocimiento general)"
    return render_template("index.html", estado_rag=estado)

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json(force=True)
        question = data.get("question", "").strip()
        if not question:
            return jsonify({"error": "No se recibió ninguna pregunta"}), 400

        # Verificar servidor Ollama
        try:
            requests.get("http://127.0.0.1:11434", timeout=2)
        except requests.exceptions.RequestException:
            return jsonify({
                "error": "❌ Ollama no está corriendo. Ejecuta: 'ollama serve &' en otra terminal."
            }), 500

        # Recuperar contexto desde tus documentos (si hay índice)
        context_block, sources = "", []
        if retriever.ready:
            snippets = retriever.search(question, k=4)
            context_block, sources = build_context(snippets)

        system_prompt = (
            "Eres 'Simatolito', asesor virtual jurídico-sindical de SUTET-SIMATOL (Tolima, Colombia). "
            "Respondes de forma clara y respetuosa, citando la documentación interna cuando exista.\n"
            "Si la respuesta NO está en la documentación, dilo con transparencia y ofrece orientar con normas generales.\n"
            "Cuando uses info interna, incluye al final: 'Fuentes: archivo#chunk,...'."
        )

        user_prompt = question
        if context_block:
            user_prompt = (
                f"Usa EXCLUSIVAMENTE la siguiente documentación interna para responder a la pregunta.\n\n"
                f"=== DOCUMENTACIÓN INTERNA ===\n{context_block}\n\n"
                f"=== PREGUNTA ===\n{question}\n\n"
                f"Si la info no está en los fragmentos, dilo explícitamente."
            )

        # Llamada al modelo local (usa phi3 por memoria)
        resp = ollama.chat(
            model="phi3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            options={"temperature": 0.2}
        )
        answer = resp["message"]["content"]

        return jsonify({"answer": answer, "sources": sources if sources else []})
    except Exception as e:
        logging.exception("Error en /ask")
        return jsonify({"error": str(e)}), 500

@app.route("/reindex", methods=["POST"])
def reindex():
    # Endpoint simple para reindexar los documentos en data/docs
    try:
        from ingest import build_index_from_docs
        count = build_index_from_docs()
        # recargar retriever
        global retriever
        retriever = RAGRetriever()
        return jsonify({"ok": True, "indexed_chunks": count})
    except Exception as e:
        logging.exception("Error en reindex")
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port, debug=True)
