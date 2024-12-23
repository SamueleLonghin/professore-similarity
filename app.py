# app/views.py
from flask import Flask, render_template, request
from src.list import similarity_html
from src.support import (
    extract_zip,
    extract_nested_zips,
    convert_formats,
    read_file_content,
    delete_temp_folder,
)
from src.config import UPLOAD_FOLDER

import shutil
import tempfile
import os
import threading

app = Flask(__name__)


app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/send", methods=["POST"])
def action_table():
    password = os.environ.get("PASSWORD", "psw")

    if request.form["password"] != password:
        return render_template("index.html", error="Password Errata, ritenta")

    if "file" not in request.files:
        return render_template("index.html", error="No file part")

    file = request.files["file"]

    # Controlla se è stato selezionato un file
    if file.filename == "":
        return render_template("index.html", error="No selected file")

    # Salva il file nella cartella temporanea
    temp_folder = tempfile.mkdtemp()
    file_path = os.path.join(temp_folder, file.filename + "-cartella")
    file.save(file_path)

    # Estrai il file zip principale
    extract_zip(file_path, temp_folder + "/estratti")

    subdirectories = [
        d
        for d in os.listdir(temp_folder)
        if os.path.isdir(os.path.join(temp_folder, d))
    ]

    while len(subdirectories) == 1:
        new_temp_folder = os.path.join(temp_folder, subdirectories[0])
        for item in os.listdir(new_temp_folder):
            shutil.move(os.path.join(new_temp_folder, item), temp_folder)
        os.rmdir(new_temp_folder)
        subdirectories = [
            d
            for d in os.listdir(temp_folder)
            if os.path.isdir(os.path.join(temp_folder, d))
        ]

    # Estrai gli archivi zip nidificati
    extract_nested_zips(temp_folder)

    # Converti i formati strani (docx) to txt
    convert_formats(temp_folder)
    # Fai qualcosa con i file estratti (es. stampa il loro elenco)
    print("Files estratti:", os.listdir(temp_folder))

    # Ottengo l'algoritmo
    algorithm = request.form["algorithm"]

    # trovo il nome della cartella temporanea 
    temp_folder_id = os.path.basename(temp_folder)

    # Creo la pagina
    html = similarity_html(temp_folder, algorithm, temp_folder_id)

    # Elimina i file temporanei dopo un giorno (86400 secondi)
    delay = 86400  # tempo in secondi
    threading.Thread(target=delete_temp_folder, args=(temp_folder, delay)).start()

    return html


@app.route("/tabella/<string:algorithm>/<string:temp_folder_id>", methods=["GET"])
def tabella(temp_folder_id, algorithm):
    temp_folder = os.path.join(tempfile.gettempdir(), temp_folder_id)

    if not os.path.exists(temp_folder):
        return render_template("index.html", error="Cartella temporanea non trovata")

    return similarity_html(temp_folder, algorithm, temp_folder_id)


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
