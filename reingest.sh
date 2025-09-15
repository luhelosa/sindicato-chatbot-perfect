#!/bin/bash
echo "🔄 Reiniciando ingesta de documentos para el Chatbot Sindical..."

# Activar entorno virtual
source venv/bin/activate

# Borrar el índice anterior
rm -rf data/index
mkdir -p data/index

# Ejecutar el ingest
python3 ingest.py

echo "✅ Reingesta completada. Ahora el chatbot tiene el nuevo conocimiento."
