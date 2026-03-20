# 🤖 Agente de Análise de Dados com IA

Aplicação que responde perguntas em **linguagem natural** sobre dados reais de e-commerce brasileiro, gerando SQL automaticamente com LLM e interpretando os resultados como um analista de dados.

👉 **[Acesse o app ao vivo](https://agente-dados-ia-fpx5aylbicabcnyuwtc4hw.streamlit.app)**

---

## Como funciona

1. Você digita uma pergunta em português
2. Um LLM (Llama 3.3 70B via Groq) converte a pergunta em SQL
3. O SQL é validado e executado no banco SQLite com dados reais da Olist
4. Se o SQL gerar erro, o agente corrige automaticamente e tenta novamente
5. O LLM interpreta o resultado e responde como um analista de dados

---

## Funcionalidades

- Perguntas em linguagem natural em português
- Geração automática de SQL com LLM
- Retry automático com autocorreção de erros de SQL
- Validação de segurança contra SQL injection e comandos destrutivos
- Proteção contra prompt injection
- Rate limiting por sessão com feedback visual em tempo real
- Conexão somente leitura com o banco de dados
- Gráfico automático quando o resultado permite visualização
- Histórico persistente por usuário via cookies
- Cache do schema do banco para melhor performance
- Logging de erros para monitoramento em produção

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

## Dataset

Dados públicos do [Brazilian E-Commerce (Olist)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) com +100k pedidos reais de e-commerce brasileiro.

Tabelas: `orders`, `order_items`, `products`, `customers`, `sellers`

---

## Como rodar localmente

Clone o repositório e instale as dependências:

    git clone https://github.com/monkaS013/agente-dados-ia.git
    cd agente-dados-ia
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

Crie um arquivo `.env` com sua chave:

    GROQ_API_KEY=sua_chave_aqui

Baixe o dataset da Olist no Kaggle, coloque os CSVs na pasta `data/` e rode:

    python setup_db.py
    streamlit run app.py

---

## Exemplos de perguntas

- *Quais os 5 estados com mais pedidos?*
- *Qual o ticket médio por estado?*
- *Qual o total de receita por mês em 2018 e qual mês teve maior crescimento?*
- *Quais os 5 vendedores com maior ticket médio?*
- *Qual a média de dias entre o pedido e a entrega por estado?*

---

## Autor

**Vinicius Soares de Morais**
[LinkedIn](https://www.linkedin.com/in/seu-perfil) · [GitHub](https://github.com/monkaS013)