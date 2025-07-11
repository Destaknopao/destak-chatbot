# -*- coding: utf-8 -*-
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return '🚀 Servidor do Destakinho está rodando!'

# ✅ VERIFICAÇÃO DO WEBHOOK (GET) E RECEBIMENTO DE MENSAGENS (POST)
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if verify_token == "destaktoken":
            return challenge, 200
        return "Token inválido", 403

    # POST: Recebendo mensagens do Meta (apenas imprime no console)
    data = request.get_json()
    print("📩 Mensagem recebida do Meta:")
    print(data)
    return "ok", 200

# 🔁 Função para registrar mensagens no banco de dados
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

# ✅ ROTA PARA MENSAGENS DO WHATSAPP (caso esteja usando Twilio)
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
        msg.body(
            "Ótimo! Aqui está nossa proposta em PDF:\n"
            "📄 Acesse: https://destaknopao.com.br/proposta/Proposta_Destak_no_Pao.pdf\n\n"
            "Depois de ler, envie:\n- Nome da empresa\n- Bairro/cidade\n- Telefone\n\n"
            "Nosso time vai te chamar! 🚀"
        )

    elif msg_usuario == '2':
        msg.body("📢 A publicidade em sacos de pão funciona assim:\n"
                 "- Sua marca é impressa nos sacos\n"
                 "- Os sacos são entregues gratuitamente em padarias\n"
                 "- Sua marca chega até a mesa do consumidor!")

    elif msg_usuario == '3':
        msg.media("https://exemplo.com/imagem_publicidade_destak.jpg")  # Substituir pelo link real
        msg.body("Aqui está um exemplo real do nosso trabalho!")

    elif msg_usuario == '4':
        msg.body("Um atendente da Destak no Pão vai te chamar em instantes. Por favor, envie sua dúvida.")

    else:
        msg.body("❓ Não entendi... Digite:\n1, 2, 3 ou 4 para continuar.")

    return str(resposta)

if __name__ == "__main__":
    app.run(debug=True, port=5000)

