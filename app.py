# app/views.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from src.list import similarity_html
from src.support import (
    extract_zip,
    extract_nested_zips,
    convert_formats,
    read_file_content)
from src.config import UPLOAD_FOLDER

from src.history import add_project_to_json, remove_project_from_json, get_projects
import shutil
import tempfile
import os

app = Flask(__name__)


app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = os.environ.get("PASSWORD", "psw")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = os.environ.get("PASSWORD", "psw")
        if request.form["password"] == password:
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Password Errata, ritenta")
    session["next"] = request.args.get("next")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))


@app.before_request
def require_login():
    if not session.get("logged_in") and request.endpoint not in ["login", "static"]:
        return redirect(url_for("login"))


@app.route("/delete_project/<string:project_id>", methods=["POST"])
def delete_project_route(project_id):
    project_folder = os.path.join(tempfile.gettempdir(), project_id)
    if os.path.exists(project_folder):
        shutil.rmtree(project_folder)
    remove_project_from_json(project_id)
    return redirect(url_for("home"))


@app.route("/")
def home():
    progetti = get_projects()
    return render_template("index.html", projects=progetti)


@app.route("/send", methods=["POST"])
def action_table():
    # Controlla se è stato inviato un file
    if "file" not in request.files:
        return render_template("index.html", error="No file part")

    file = request.files["file"]
    nome = request.form["nome"]

    # Controlla se è stato selezionato un file
    if file.filename == "":
        return render_template("index.html", error="No selected file")

    # Salva il file nella cartella temporanea
    project_folder = tempfile.mkdtemp()
    file_path = os.path.join(project_folder, file.filename + "-cartella")
    file.save(file_path)

    # Estrai il file zip principale
    extract_zip(file_path, project_folder + "/estratti")

    subdirectories = [
        d
        for d in os.listdir(project_folder)
        if os.path.isdir(os.path.join(project_folder, d))
    ]

    while len(subdirectories) == 1:
        new_project_folder = os.path.join(project_folder, subdirectories[0])
        for item in os.listdir(new_project_folder):
            shutil.move(os.path.join(new_project_folder, item), project_folder)
        os.rmdir(new_project_folder)
        subdirectories = [
            d
            for d in os.listdir(project_folder)
            if os.path.isdir(os.path.join(project_folder, d))
        ]

    # Estrai gli archivi zip nidificati
    extract_nested_zips(project_folder)

    # Converti i formati strani (docx) to txt
    convert_formats(project_folder)
    # Fai qualcosa con i file estratti (es. stampa il loro elenco)
    print("Files estratti:", os.listdir(project_folder))

    # Ottengo l'algoritmo
    algorithm = request.form["algorithm"]

    # trovo il nome della cartella temporanea
    project_id = os.path.basename(project_folder)
    add_project_to_json(project_id, nome)

    # Creo la pagina
    return similarity_html(project_folder, algorithm, project_id)


@app.route("/tabella/<string:algorithm>/<string:project_id>", methods=["GET"])
def tabella(project_id, algorithm):
    project_folder = os.path.join(tempfile.gettempdir(), project_id)

    if not os.path.exists(project_folder):
        return render_template("index.html", error="Progetto non trovato")

    return similarity_html(project_folder, algorithm, project_id)


@app.route("/compare/<string:a>/<string:b>")
def compare(a, b):
    a = a.replace("+!+", "/")
    b = b.replace("+!+", "/")
    a = os.path.join(tempfile.gettempdir(), a)
    b = os.path.join(tempfile.gettempdir(), b)
    contenta = read_file_content(a)
    contentb = read_file_content(b)

    return render_template(
        "compare.html", file1=a, file2=b, content_file1=contenta, content_file2=contentb
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
