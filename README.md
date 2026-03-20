# 🤖 Agente de Análise de Dados com IA

Aplicação que permite fazer perguntas em **linguagem natural** sobre dados de e-commerce brasileiro e receber respostas inteligentes, geradas por LLM com SQL automático.

👉 **[Acesse o app ao vivo](https://agente-dados-ia-fpx5aylbicabcnyuwtc4hw.streamlit.app)**

---

## Como funciona

1. Você digita uma pergunta em português
2. Um LLM (Llama 3.3 70B via Groq) converte a pergunta em SQL
3. O SQL é executado no banco de dados SQLite com dados reais da Olist
4. O LLM interpreta o resultado e responde como um analista de dados
5. Se o SQL gerar erro, o agente corrige automaticamente e tenta novamente

---

## Funcionalidades

- Perguntas em linguagem natural em português
- Geração automática de SQL com LLM
- Retry automático com autocorreção de erros de SQL
- Validação de segurança (bloqueia DELETE, DROP, INSERT)
- Gráfico automático quando o resultado permite visualização
- Histórico das últimas perguntas
- Perguntas de exemplo para explorar o dataset

---

## Dataset

Dados públicos do [Brazilian E-Commerce (Olist)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) com +100k pedidos reais de e-commerce brasileiro.

Tabelas disponíveis: `orders`, `order_items`, `products`, `customers`, `sellers`

---

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Interface | Streamlit |
| LLM | Llama 3.3 70B (Groq API) |
| Banco de dados | SQLite |
| Visualização | Plotly |
| Deploy | Streamlit Cloud |
| Linguagem | Python 3.14 |

---

## Como rodar localmente
```bash