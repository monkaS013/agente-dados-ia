import sqlite3
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

def perguntar(pergunta):
    print(f"\nPergunta: {pergunta}")
    print("-" * 50)
    
    schema = get_schema()
    sql = gerar_sql(pergunta, schema)
    print(f"SQL gerado:\n{sql}\n")
    
    try:
        conn = sqlite3.connect("ecommerce.db")
        df = pd.read_sql(sql, conn)
        conn.close()
        
        resposta = interpretar_resultado(pergunta, sql, df.to_string())
        print(f"Resposta: {resposta}")
        return resposta, sql, df
    
    except Exception as e:
        print(f"Erro ao executar SQL: {e}")
        return None, sql, None

if __name__ == "__main__":
    perguntar("Quais os 5 estados com mais pedidos?")