import pandas as pd
import sqlite3
import os

conn = sqlite3.connect("ecommerce.db")

arquivos = {
    "orders":      "data/olist_orders_dataset.csv",
    "order_items": "data/olist_order_items_dataset.csv",
    "products":    "data/olist_products_dataset.csv",
    "customers":   "data/olist_customers_dataset.csv",
    "sellers":     "data/olist_sellers_dataset.csv",
}

for tabela, caminho in arquivos.items():
    if os.path.exists(caminho):
        df = pd.read_csv(caminho)
        df.to_sql(tabela, conn, if_exists="replace", index=False)
        print(f"✓ Tabela '{tabela}' criada com {len(df)} linhas")
    else:
        print(f"✗ Arquivo não encontrado: {caminho}")

conn.close()
print("\nBanco de dados 'ecommerce.db' criado com sucesso!")
