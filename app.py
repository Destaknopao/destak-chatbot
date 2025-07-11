# -*- coding: utf-8 -*-
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return '🚀 Servidor do Destakinho está rodando!'

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

@app.route("/webhook", methods=["GET", "POST"])
def whatsapp():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == "destaktoken":
            return request.args.get("hub.challenge")
        return "Token inválido!", 403

    if request.method == "POST":
        print("📩 Mensagem recebida do Meta:")
        print(request.json)
        return "ok", 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)

