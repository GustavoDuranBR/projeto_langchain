import sys
import os
from flask import Flask, render_template, request
from dotenv import load_dotenv

# Adiciona o diretório raiz do projeto ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa as funções do chatbot
from chatbot.chatbot import responder_pergunta_biblia, responder_pergunta_resumo

# Inicializa o Flask e carrega o arquivo .env
app = Flask(__name__)
load_dotenv()

# Rota para a página principal
@app.route('/', methods=['GET', 'POST'])
def index():
    resposta = ""
    if request.method == 'POST':
        assunto = request.form.get('assunto')
        traducoes = request.form.get('traducoes')
        
        if assunto and traducoes:
            try:
                resposta = responder_pergunta_biblia(assunto, traducoes)
            except Exception as e:
                resposta = f"Erro ao processar a pergunta: {str(e)}"
        else:
            resposta = "Por favor, preencha todos os campos."
    return render_template('index.html', resposta=resposta)

# Rota para a página de resumo
@app.route('/resumo', methods=['GET', 'POST'])
def resumo():
    resposta = ""
    if request.method == 'POST':
        assunto = request.form.get('assunto')
        traducoes = request.form.get('traducoes')
        
        if assunto and traducoes:
            try:
                resposta = responder_pergunta_resumo(assunto, traducoes)
            except Exception as e:
                resposta = f"Erro ao processar o resumo: {str(e)}"
        else:
            resposta = "Por favor, preencha todos os campos."
    return render_template('resumo.html', resposta=resposta)

# Rota para a página "Sobre"
@app.route('/sobre', methods=['GET'])
def sobre():
    return render_template('sobre.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
