import os
import time
import re
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# Carrega o arquivo .env para inicializar a chave da API
load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")

# Configuração do modelo de linguagem com o Together API
llm = ChatOpenAI(
    base_url="https://api.together.xyz/v1",
    api_key=api_key,
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
)

# Templates para prompts
prompt_biblia_template = """
Por favor, forneça a passagem bíblica correspondente a: "{assunto}" na tradução: "{traducoes}". 
Apenas a passagem, sem comentários ou explicações adicionais, e limite-se ao trecho especificado.
"""

prompt_resumo_template = """
Por favor, encontre o trecho da Bíblia que corresponde a: "{assunto}" na tradução: "{traducoes}".

Em seguida, forneça um resumo interpretativo e descritivo que inclua:
1. O contexto histórico ou teológico do trecho.
2. Os principais eventos ou ensinamentos abordados nos versículos.
3. A relevância do trecho para a compreensão da mensagem bíblica.

Certifique-se de que a interpretação esteja clara e que todos os pontos solicitados sejam abordados. Se não houver interpretação disponível, informe isso de maneira clara.
"""

# Função para processar a pergunta sobre a passagem bíblica
def responder_pergunta_biblia(assunto, traducoes):
    """
    Gera uma resposta para uma pergunta sobre uma passagem bíblica específica.

    Args:
        assunto (str): O assunto da passagem bíblica.
        traducoes (str): A tradução da Bíblia a ser utilizada.

    Returns:
        str: A resposta formatada da passagem bíblica.
    """
    prompt = PromptTemplate(template=prompt_biblia_template, input_variables=["assunto", "traducoes"])
    biblia_chain = prompt | llm
    return obter_resposta(biblia_chain, assunto, traducoes)

# Função para processar a pergunta sobre o resumo da passagem
def responder_pergunta_resumo(assunto, traducoes):
    """
    Gera um resumo para uma passagem bíblica específica.

    Args:
        assunto (str): O assunto da passagem bíblica.
        traducoes (str): A tradução da Bíblia a ser utilizada.

    Returns:
        str: A interpretação do resumo da passagem bíblica.
    """
    prompt = PromptTemplate(template=prompt_resumo_template, input_variables=["assunto", "traducoes"])
    resumo_chain = prompt | llm
    return obter_resumo_interpretacao(resumo_chain, assunto, traducoes)

# Função para obter a resposta do LangChain
def obter_resposta(chain, assunto, traducoes):
    """
    Invoca o modelo para obter uma resposta, tentando até 3 vezes em caso de falha.

    Args:
        chain: A cadeia do LangChain configurada.
        assunto (str): O assunto da pergunta.
        traducoes (str): A tradução da Bíblia a ser utilizada.

    Returns:
        str: A resposta formatada ou uma mensagem de erro.
    """
    for attempt in range(3):  # Tentar até 3 vezes
        try:
            resposta = chain.invoke({"assunto": assunto, "traducoes": traducoes})
            resposta_texto = resposta.content if hasattr(resposta, 'content') else str(resposta)
            return formatar_resposta(resposta_texto)
        except Exception as e:
            print(f"Erro: {e}. Tentando novamente em 60 segundos... (Tentativa {attempt + 1})")
            time.sleep(60)
    return "Erro ao obter resposta após múltiplas tentativas."

# Função para extrair apenas a interpretação do resumo
def obter_resumo_interpretacao(chain, assunto, traducoes):
    """
    Extrai a interpretação de um resumo baseado na resposta completa.

    Args:
        chain: A cadeia do LangChain configurada.
        assunto (str): O assunto da pergunta.
        traducoes (str): A tradução da Bíblia a ser utilizada.

    Returns:
        str: A interpretação extraída ou uma mensagem de erro.
    """
    resposta_completa = obter_resposta(chain, assunto, traducoes)
    partes = resposta_completa.split("Interpretação:")
    
    # Se houver uma interpretação, retornamos, senão, informamos que não foi encontrada
    return partes[1].strip() if len(partes) > 1 else "Interpretação não encontrada."

# Função para formatar a resposta
def formatar_resposta(resposta):
    """
    Formata a resposta para um formato legível.

    Args:
        resposta (str): A resposta a ser formatada.

    Returns:
        str: A resposta formatada.
    """
    if resposta is None:
        return "Resposta não disponível."  # Trata caso de resposta None

    resposta = resposta.replace("<br>", "\n")
    resposta = re.sub(r'\n+', '\n', resposta)  # Remove quebras de linha duplicadas
    resposta = '\n'.join(line.strip() for line in resposta.splitlines())  # Remove espaços em branco
    return resposta.strip()
