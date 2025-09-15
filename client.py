import requests
print('===================================')
print('🤖 Bienvenido/a al Asesor Sindical Virtual Simatolito')
print('Escribe "salir" para terminar la conversación.')
print('===================================')
while True:
    q = input('👤 Tú: ')
    if q.lower() in ('salir','exit','quit'):
        break
    try:
        res = requests.post('http://127.0.0.1:5000/ask', json={'question':q})
        data = res.json()
        if 'answer' in data:
            print('\n🤖 Simatolito:', data['answer'], '\n')
        else:
            print('\n❌ Error:', data.get('error','respuesta inválida'), '\n')
    except Exception as e:
        print('\n❌ Error de conexión:', e, '\n')
