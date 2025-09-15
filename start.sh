#!/bin/bash
echo "🚀 Iniciando Asesor Sindical Virtual SIMATOL..."

# Activar entorno virtual
source venv/bin/activate

# Preguntar si el usuario quiere regenerar la base de conocimiento
read -p "🔄 ¿Quieres reindexar los documentos (s/n)? " respuesta

if [[ "$respuesta" == "s" || "$respuesta" == "S" ]]; then
    echo "🗑️  Borrando índice anterior..."
    rm -rf data/index
    mkdir -p data/index

    echo "📚 Iniciando reingesta de documentos..."
    python3 ingest.py
    echo "✅ Reingesta completada."
else
    echo "⏩ Saltando reingesta. Usando índice existente."
fi

# Verificar si Ollama ya está corriendo
if pgrep -x "ollama" > /dev/null
then
    echo "✅ Ollama ya está corriendo."
else
    echo "▶️  Iniciando Ollama..."
    ollama serve &
    sleep 5
fi

# Arrancar servidor Flask
echo "🌐 Arrancando servidor Flask en http://127.0.0.1:5000 ..."
python3 app.py

