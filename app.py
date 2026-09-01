from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "chave-secreta-troque-depois"


def conectar_banco():
    return sqlite3.connect("cursos.db")


def criar_tabela_progresso():
    banco = conectar_banco()

    banco.execute("""
        CREATE TABLE IF NOT EXISTS progresso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            aula INTEGER NOT NULL,
            concluida INTEGER DEFAULT 0,
            UNIQUE(aluno_id, aula)
        )
    """)

    banco.commit()
    banco.close()


criar_tabela_progresso()


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/curso")
def curso():
    return render_template("curso.html")


@app.route("/checkout")
def checkout():
    return render_template("checkout.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        senha_hash = generate_password_hash(senha)

        banco = conectar_banco()

        try:
            banco.execute(
                "INSERT INTO alunos (nome, email, senha) VALUES (?, ?, ?)",
                (nome, email, senha_hash)
            )
            banco.commit()
        except sqlite3.IntegrityError:
            banco.close()
            return "Este e-mail já está cadastrado."

        banco.close()

        return redirect("/login")

    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        banco = conectar_banco()

        aluno = banco.execute(
            "SELECT * FROM alunos WHERE email = ?",
            (email,)
        ).fetchone()

        banco.close()

        if aluno and check_password_hash(aluno[3], senha):
            session["aluno_id"] = aluno[0]
            session["aluno_nome"] = aluno[1]

            return redirect("/aluno")

        return "E-mail ou senha incorretos."

    return render_template("login.html")


@app.route("/aluno")
def aluno():
    if "aluno_id" not in session:
        return redirect("/login")

    banco = conectar_banco()

    progresso = banco.execute(
        "SELECT aula FROM progresso WHERE aluno_id = ? AND concluida = 1",
        (session["aluno_id"],)
    ).fetchall()

    banco.close()

    aulas_concluidas = [item[0] for item in progresso]

    return render_template(
        "aluno.html",
        nome=session["aluno_nome"],
        aula_concluida=1 in aulas_concluidas,
        aulas_concluidas=aulas_concluidas
    )


@app.route("/concluir-aula", methods=["POST"])
def concluir_aula():
    if "aluno_id" not in session:
        return redirect("/login")

    aula = int(request.form["aula"])
    aluno_id = session["aluno_id"]

    banco = conectar_banco()

    banco.execute("""
        INSERT INTO progresso (aluno_id, aula, concluida)
        VALUES (?, ?, 1)
        ON CONFLICT(aluno_id, aula)
        DO UPDATE SET concluida = 1
    """, (aluno_id, aula))

    banco.commit()
    banco.close()

    return redirect("/aluno")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)



