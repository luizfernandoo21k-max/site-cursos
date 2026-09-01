import sqlite3

banco = sqlite3.connect("cursos.db")

banco.execute("""
CREATE TABLE IF NOT EXISTS alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL
)
""")

banco.commit()
banco.close()

print("Banco de dados criado com sucesso!")

