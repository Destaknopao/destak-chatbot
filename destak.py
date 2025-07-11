from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3
from datetime import datetime
import json

app = Flask(__name__)

# Função para registrar mensagens recebidas
def registrar_atendimento(numero, mensagem):
    conn = sqlite3.connect('destak.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT,
            mensagem TEXT,
            horario TEXT
        )
    ''')
    c.execute('INSERT INTO atendimentos (numero, mensagem, horario) VALUES (?, ?, ?)',
              (numero, mensagem, datetime.now()))
    conn.commit()
    conn.close()

# Rota padrão (opcional)
@app.route("/", methods=["GET"])
def home():
    return "Destak no Pão - Webhook ativo!"

# Rota para verificação do webhook (Meta)
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = "destaktoken"
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == verify_token:
            return challenge, 200
        else:
            return "Erro na verificação", 403

    elif request.method == "POST":
        payload = request.get_json()
        print("📩 Mensagem recebida do Meta:")
        print(json.dumps(payload, indent=2))

        # Aqui você pode implementar o tratamento da mensagem se quiser
        return "Evento recebido", 200

# Rota para responder mensagens do Twilio (caso ainda esteja usando)
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    msg_usuario = request.values.get('Body', '').strip().lower()
    numero_usuario = request.values.get('From', '')
    resposta = MessagingResponse()
    msg = resposta.message()

    registrar_atendimento(numero_usuario, msg_usuario)

    if msg_usuario in ['oi', 'olá', 'bom dia', 'boa tarde']:
        msg.body(
            "🍞 Olá! Eu sou o *Destakinho*, assistente da Destak no Pão!\n\n"
            "Escolha uma opção:\n"
            "1️⃣ Quero anunciar\n"
            "2️⃣ Como funciona\n"
            "3️⃣ Ver exemplos\n"
            "4️⃣ Falar com um atendente"
        )
    elif msg_usuario == '1':
        msg.body("📢 Ótimo! Para anunciar, envie agora o nome do seu comércio e a região que deseja alcançar.")
    elif msg_usuario == '2':
        msg.body("📦 Funciona assim: colocamos sua propaganda em sacos de pão distribuídos em padarias parceiras. Simples, barato e direto ao consumidor!")
    elif msg_usuario == '3':
        msg.body("🖼️ Veja exemplos reais de anúncios: https://instagram.com/destaknopao")
    elif msg_usuario == '4':
        msg.body("💬 Um atendente entrará em contato com você em breve. Obrigado!")
    else:
        msg.body("❓ Não entendi. Envie *1*, *2*, *3* ou *4* para escolher uma opção.")

    return str(resposta)

# 🔧 Configuração para Render funcionar
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

