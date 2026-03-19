import sqlite3
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import plotly.express as px
import streamlit as st
import os

load_dotenv()
cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(
    page_title="Agente de Dados IA",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Agente de Análise de Dados com IA")
st.caption("Faça perguntas em português sobre o e-commerce brasileiro da Olist")

PERGUNTAS_EXEMPLO = [
    "Quais os 5 estados com mais pedidos?",
    "Qual o ticket médio dos pedidos por estado?",
    "Quais os 10 produtos mais vendidos?",
    "Qual o total de receita por mês em 2018?",
    "Quais vendedores têm mais pedidos?",
]

def get_schema():
    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = cursor.fetchall()
    schema = ""
    for (tabela,) in tabelas:
        cursor.execute(f"PRAGMA table_info({tabela})")
        colunas = cursor.fetchall()
        cols = ", ".join([f"{col[1]} ({col[2]})" for col in colunas])
        schema += f"Tabela {tabela}: {cols}\n"
    conn.close()
    return schema

def validar_sql(sql):
    palavras_proibidas = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE", "CREATE"]
    sql_upper = sql.upper()
    for palavra in palavras_proibidas:
        if palavra in sql_upper:
            return False, f"Query bloqueada: contém comando '{palavra}' não permitido."
    if not sql_upper.strip().startswith("SELECT"):
        return False, "Apenas queries SELECT são permitidas."
    return True, ""
def gerar_sql(pergunta, schema):
    prompt = f"""Você é um analista de dados especialista em SQL.
Dado o schema abaixo, converta a pergunta em uma query SQL válida para SQLite.
Retorne APENAS o SQL, sem explicações, sem markdown, sem crases.

Schema:
{schema}

Pergunta: {pergunta}

SQL:"""
    resposta = cliente.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    sql = resposta.choices[0].message.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

def interpretar_resultado(pergunta, sql, resultado):
    prompt = f"""Você é um analista de dados. Responda a pergunta abaixo em português 
de forma clara e objetiva, baseado nos dados retornados pela query SQL.
Seja direto, como se estivesse explicando para um executivo.

Pergunta: {pergunta}
SQL executado: {sql}
Resultado: {resultado}

Resposta:"""
    resposta = cliente.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return resposta.choices[0].message.content.strip()

def tentar_grafico(df):
    if df is None or df.empty or len(df.columns) < 2:
        return
    col1 = df.columns[0]
    col2 = df.columns[1]
    if pd.api.types.is_numeric_dtype(df[col2]):
        fig = px.bar(df, x=col1, y=col2, title="Visualização dos dados")
        st.plotly_chart(fig, use_container_width=True)

# Sidebar com perguntas de exemplo e histórico
with st.sidebar:
    st.subheader("💡 Perguntas de exemplo")
    for pergunta in PERGUNTAS_EXEMPLO:
        if st.button(pergunta, use_container_width=True):
            st.session_state.pergunta_input = pergunta

    st.divider()
    st.subheader("🕘 Histórico")
    if "historico" not in st.session_state:
        st.session_state.historico = []
    for item in reversed(st.session_state.historico[-5:]):
        st.caption(f"• {item}")

# Input principal
if "pergunta_input" not in st.session_state:
    st.session_state.pergunta_input = ""

pergunta = st.text_input(
    "Digite sua pergunta:",
    value=st.session_state.pergunta_input,
    placeholder="Ex: Quais os 5 estados com mais pedidos?"
)

if st.button("🔍 Perguntar", type="primary") and pergunta:
    schema = get_schema()

    with st.spinner("Gerando SQL..."):
        sql = gerar_sql(pergunta, schema)

    valido, mensagem_erro = validar_sql(sql)
    if not valido:
        st.error(mensagem_erro)
        st.stop()

    valido, mensagem_erro = validar_sql(sql)
    if not valido:
        st.error(mensagem_erro)
        st.stop()

    try:
        conn = sqlite3.connect("ecommerce.db")
        df = pd.read_sql(sql, conn)
        conn.close()

        with st.spinner("Interpretando resultado..."):
            resposta = interpretar_resultado(pergunta, sql, df.to_string())

        # Resposta principal
        st.success(resposta)

        # Gráfico automático
        tentar_grafico(df)

        # Dados e SQL em abas
        aba1, aba2 = st.tabs(["📊 Dados", "🔧 SQL gerado"])
        with aba1:
            st.dataframe(df, use_container_width=True)
        with aba2:
            st.code(sql, language="sql")

        # Salva no histórico
        if "historico" not in st.session_state:
            st.session_state.historico = []
        st.session_state.historico.append(pergunta)
        st.session_state.pergunta_input = ""

    except Exception as e:
        st.error(f"Erro ao executar a query: {e}")
        st.code(sql, language="sql")