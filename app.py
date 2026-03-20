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

def gerar_sql(pergunta, schema):
    prompt = f"""Você é um especialista em SQL para SQLite. Sua única tarefa é converter perguntas em queries SQL corretas e executáveis.

Schema do banco:
{schema}

Regras obrigatórias:
1. Retorne APENAS o SQL puro, sem explicações, sem markdown, sem crases, sem comentários
2. Use apenas tabelas e colunas que existem no schema acima
3. Nunca use ORDER BY dentro de subqueries ou CTEs com UNION / UNION ALL
4. Quando usar UNION ALL com ORDER BY, sempre envolva em uma subquery externa:
   SELECT * FROM (SELECT ... UNION ALL SELECT ...) ORDER BY ...
5. Nunca use funções que não existem no SQLite (ex: MONTH(), YEAR() não existem — use strftime('%m', coluna) e strftime('%Y', coluna))
6. Para datas, sempre use strftime() do SQLite
7. Quando a pergunta pedir "top N e bottom N" ao mesmo tempo, use CTE ou subquery, nunca ORDER BY dentro do UNION
8. Sempre use aliases claros nas colunas calculadas
9. Prefira JOINs explícitos (INNER JOIN, LEFT JOIN) em vez de subqueries quando possível
10. Nunca retorne mais de 1000 linhas — use LIMIT quando necessário
11. Nunca use funções de janela (LAG, LEAD, RANK, ROW_NUMBER) dentro de HAVING ou WHERE — calcule em CTE ou subquery primeiro
12. Para calcular crescimento mês a mês, use uma subquery com self-join em vez de LAG()
13. Funções de janela só podem aparecer no SELECT, nunca em HAVING, WHERE ou GROUP BY

Pergunta: {pergunta}

SQL:"""
    resposta = cliente.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    sql = resposta.choices[0].message.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

def gerar_sql_com_erro(pergunta, schema, sql_anterior, erro):
    prompt = f"""Você é um especialista em SQL para SQLite. O SQL abaixo gerou um erro ao ser executado.
Corrija o SQL para resolver o erro, mantendo o objetivo original da pergunta.
Retorne APENAS o SQL corrigido, sem explicações, sem markdown, sem crases.

Schema:
{schema}

Pergunta original: {pergunta}

SQL com erro:
{sql_anterior}

Erro retornado:
{erro}

SQL corrigido:"""
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

def validar_sql(sql):
    palavras_proibidas = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE", "CREATE"]
    sql_upper = sql.upper()
    for palavra in palavras_proibidas:
        if palavra in sql_upper:
            return False, f"Query bloqueada: contém comando '{palavra}' não permitido."
    if not sql_upper.strip().startswith("SELECT"):
        return False, "Apenas queries SELECT são permitidas."
    return True, ""

def tentar_grafico(df):
    if df is None or df.empty or len(df.columns) < 2:
        return
    col1 = df.columns[0]
    col2 = df.columns[1]
    if pd.api.types.is_numeric_dtype(df[col2]):
        fig = px.bar(df, x=col1, y=col2, title="Visualização dos dados")
        st.plotly_chart(fig, use_container_width=True)

with st.sidebar:
    st.subheader("💡 Perguntas de exemplo")
    for pergunta_ex in PERGUNTAS_EXEMPLO:
        if st.button(pergunta_ex, use_container_width=True):
            st.session_state.pergunta_input = pergunta_ex

    st.divider()
    st.subheader("🕘 Histórico")
    if "historico" not in st.session_state:
        st.session_state.historico = []
    for item in reversed(st.session_state.historico[-5:]):
        if st.button(item, key=f"hist_{item}", use_container_width=True):
            st.session_state.pergunta_input = item
            
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

    MAX_TENTATIVAS = 3
    tentativa = 0
    df = None
    erro_anterior = None

    while tentativa < MAX_TENTATIVAS:
        try:
            if erro_anterior:
                with st.spinner(f"Corrigindo SQL (tentativa {tentativa + 1})..."):
                    sql = gerar_sql_com_erro(pergunta, schema, sql, erro_anterior)
            conn = sqlite3.connect("ecommerce.db")
            df = pd.read_sql(sql, conn)
            conn.close()
            erro_anterior = None
            break
        except Exception as e:
            erro_anterior = str(e)
            tentativa += 1

    if erro_anterior:
        st.error(f"Não foi possível gerar um SQL válido após {MAX_TENTATIVAS} tentativas.")
        st.code(sql, language="sql")
    else:
        with st.spinner("Interpretando resultado..."):
            resposta = interpretar_resultado(pergunta, sql, df.to_string())

        st.success(resposta)
        tentar_grafico(df)

        aba1, aba2 = st.tabs(["📊 Dados", "🔧 SQL gerado"])
        with aba1:
            st.dataframe(df, use_container_width=True)
        with aba2:
            st.code(sql, language="sql")

        if "historico" not in st.session_state:
            st.session_state.historico = []
        st.session_state.historico.append(pergunta)
        st.session_state.pergunta_input = ""