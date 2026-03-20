import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Admin", page_icon="📊", layout="wide")

st.title("📊 Dashboard de Uso")
st.caption("Monitoramento de perguntas e feedbacks do agente")

def carregar_feedbacks():
    try:
        conn = sqlite3.connect("ecommerce.db")
        df = pd.read_sql("""
            SELECT pergunta, sql_gerado, avaliacao, timestamp
            FROM feedbacks
            ORDER BY timestamp DESC
        """, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

df = carregar_feedbacks()

if df.empty:
    st.info("Nenhum feedback registrado ainda.")
    st.stop()

# ─── MÉTRICAS ──────────────────────────────────────────────────────────────────
total = len(df)
positivos = len(df[df["avaliacao"] == "positivo"])
negativos = len(df[df["avaliacao"] == "negativo"])
taxa = round((positivos / total) * 100) if total > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de feedbacks", total)
col2.metric("👍 Positivos", positivos)
col3.metric("👎 Negativos", negativos)
col4.metric("Taxa de satisfação", f"{taxa}%")

st.divider()

# ─── GRÁFICO POR DIA ───────────────────────────────────────────────────────────
st.subheader("Feedbacks por dia")
df["data"] = pd.to_datetime(df["timestamp"]).dt.date
por_dia = df.groupby(["data", "avaliacao"]).size().reset_index(name="quantidade")
fig = px.bar(por_dia, x="data", y="quantidade", color="avaliacao",
             color_discrete_map={"positivo": "#2ecc71", "negativo": "#e74c3c"},
             barmode="group")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ─── PERGUNTAS COM FEEDBACK NEGATIVO ──────────────────────────────────────────
st.subheader("❌ Perguntas com feedback negativo")
negativos_df = df[df["avaliacao"] == "negativo"][["pergunta", "sql_gerado", "timestamp"]]
if negativos_df.empty:
    st.success("Nenhum feedback negativo ainda!")
else:
    st.dataframe(negativos_df, use_container_width=True)

st.divider()

# ─── HISTÓRICO COMPLETO ────────────────────────────────────────────────────────
st.subheader("📋 Histórico completo")
st.dataframe(df[["pergunta", "avaliacao", "timestamp"]], use_container_width=True)