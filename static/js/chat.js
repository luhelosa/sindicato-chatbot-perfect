const chatBox = document.getElementById('chat-box');
const input = document.getElementById('pregunta');
const send = document.getElementById('send');

function addMessage(text, role='bot'){
  const m = document.createElement('div');
  m.className = 'msg ' + (role==='user'?'user':'bot');
  const b = document.createElement('div');
  b.className = 'bubble ' + (role==='user'?'user':'bot');
  b.textContent = text;
  m.appendChild(b);
  chatBox.appendChild(m);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function enviarPregunta(){
  const q = input.value.trim();
  if(!q) return;
  addMessage('👤 ' + q, 'user');
  input.value = '';
  // show loader
  addMessage('🤖 Simatolito está escribiendo...', 'bot');
  try {
    const res = await fetch('/ask', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({question: q})
    });
    const data = await res.json();
    // remove loader (last bot message)
    const msgs = chatBox.querySelectorAll('.msg.bot');
    if(msgs.length) msgs[msgs.length-1].remove();
    if(data.answer){
      let text = data.answer;
      if(data.sources && data.sources.length) text += '\n\nFuentes: ' + data.sources.join(', ');
      addMessage('🤖 ' + text, 'bot');
    } else if(data.error){
      addMessage('❌ ' + data.error, 'bot');
    } else {
      addMessage('❌ Error desconocido', 'bot');
    }
  } catch(err){
    // remove loader
    const msgs = chatBox.querySelectorAll('.msg.bot');
    if(msgs.length) msgs[msgs.length-1].remove();
    addMessage('❌ Error de conexión: ' + err.message, 'bot');
  }
}

send.addEventListener('click', enviarPregunta);
input.addEventListener('keydown', function(e){
  if(e.key==='Enter') enviarPregunta();
});
