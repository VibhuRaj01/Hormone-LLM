from flask import Flask, request, jsonify, render_template_string
from GPT import get_out

app = Flask(__name__)


# -------------------- Web pages --------------------
@app.route("/")
def index():
    # Serve a tiny single-page UI
    return render_template_string(HTML)


@app.route("/chat", methods=["POST"])
def chat():
    """AJAX endpoint that the JS front-end calls."""
    user_query = request.json.get("message", "").strip()
    if not user_query:
        return jsonify(error="Empty message"), 400

    try:
        answer = get_out(user_query)
        return jsonify(reply=answer)
    except Exception as e:
        return jsonify(error=str(e)), 500


# -------------------- Ultra-simple single-file template --------------------
HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Hormone-GPT Chat</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Helvetica, Arial, sans-serif; margin: 0; padding: 0; display: flex; height: 100vh; background:#f0f0f0; }
    #chat { flex: 1; display: flex; flex-direction: column; }
    #messages { flex: 1; overflow-y: auto; padding: 10px; background:#fff; border:1px solid #ccc; margin:10px; border-radius:4px;}
    .user { color:#3498db; font-weight:bold; }
    .bot  { color:#2c3e50; }
    .error{ color:#e74c3c; }
    #form { display: flex; padding: 0 10px 10px 10px; }
    #form input { flex:1; padding:8px; font-size:14px; border:1px solid #ccc; border-radius:4px 0 0 4px; }
    #form button { padding:8px 14px; font-size:14px; border:1px solid #ccc; border-left:none; border-radius:0 4px 4px 0; cursor:pointer; }
  </style>
</head>
<body>
  <div id="chat">
    <div id="messages"></div>
    <form id="form" onsubmit="sendMsg(); return false;">
      <input id="msg" autocomplete="off" placeholder="Type your message…">
      <button>Send</button>
    </form>
  </div>

<script>
async function sendMsg() {
  const input = document.getElementById('msg');
  const text = input.value.trim();
  if (!text) return;
  addMsg('user', text);
  input.value = '';

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({message: text})
    });
    const data = await res.json();
    if (res.ok) {
      addMsg('bot', data.reply);
    } else {
      addMsg('error', data.error || 'Unknown error');
    }
  } catch (err) {
    addMsg('error', err);
  }
}

function addMsg(cls, txt) {
  const box = document.getElementById('messages');
  const div = document.createElement('div');
  div.className = cls;
  div.textContent = (cls === 'user' ? 'You: ' : 'Bot: ') + txt;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}
</script>
</body>
</html>
"""

# -------------------- Entry point --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
