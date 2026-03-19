import sqlite3
import pandas as pd

conn = sqlite3.connect("ecommerce.db")

tabelas = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
print("Tabelas disponíveis:")
print(tabelas)

print("\nTop 5 estados com mais clientes:")
query = """
    SELECT customer_state, COUNT(*) as total
    FROM customers
    GROUP BY customer_state
    ORDER BY total DESC
    LIMIT 5
"""
print(pd.read_sql(query, conn))

conn.close()