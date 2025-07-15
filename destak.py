# -*- coding: utf-8 -*-
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3
from datetime import datetime
import json
import os

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
              (numero, mensagem, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# Rota padrão
@app.route("/", methods=["GET"])
def home():
    return "✅ Destak no Pão - Webhook ativo!"

# Rota para verificação e recepção de mensagens do WhatsApp Cloud API (Meta)
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    verify_token = os.environ.get("VERIFY_TOKEN", "destaktoken")

    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == verify_token:
            print("🔐 Webhook verificado com sucesso!")
            return challenge, 200
        else:
            print("❌ Falha na verificação do webhook.")
            return "Erro na verificação", 403

    elif request.method == "POST":
        payload = request.get_json()
        print("📩 Mensagem recebida do Meta:")
        print(json.dumps(payload, indent=2))

        try:
            entry = payload['entry'][0]
            changes = entry['changes'][0]['value']
            mensagens = changes.get('messages')

            if mensagens:
                numero = mensagens[0]['from']
                texto = mensagens[0]['text']['body']
                registrar_atendimento(numero, texto)

        except Exception as e:
            print(f"❌ Erro ao registrar atendimento: {e}")

        return "Evento recebido", 200

# Rota para responder mensagens do Twilio
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

# 🔧 Executa o app no Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

