import os
import shutil
from zipfile import ZipFile

from src.config import COMPARE_FORMATS
from src.converter import convert_docx_to_txt, convert_pdf_to_txt
import time


def color_scale(val, extra=True):
    if val and extra:
        color = f"rgb({int(val * 255)}, {int(255 - val * 255)},0)"
        return f"background-color: {color};"
    elif val:
        color = f"rgb({int(255 - val * 255)},{int(val * 255)},0)"
        return f"background-color: {color};"

    return f"background-color: while;"


def format_link(value, indices, name):
    cl = ""
    color = ""
    if indices.split("/")[:-1] == name.split("/")[:-1]:
        # Proprietario
        cl += "owner "
        value = ""
    elif value:
        value = round(float(value), 2)
        # Due proprietari
        if (
            indices.split(".")[-1].upper() == "HTML"
            or name.split(".")[-1].upper() == "HTML"
        ):
            pass
            # color = color_scale(value,False)
        else:
            color = color_scale(value, True)

    indices = indices.replace("/", "+!+")
    name = name.replace("/", "+!+")
    url = f"/compare/{indices}/{name}?sim={value}"
    return f'<a href="{url}" style="{color}" class="{cl}" target="_blank">{value}</a>'


def format_cell(value, base_path, propr, filer, propc, filec):
    cl = ""
    color = ""
    link = ""
    if propr == propc:
        # Proprietario
        cl += "same-owner "
        value = ""
    elif value:
        value = round(float(value), 2)
        # Due proprietari
        if (
            filer.split(".")[-1].upper() == "HTML"
            or filec.split(".")[-1].upper() == "HTML"
        ):
            pass
            # color = color_scale(value,False)
        else:
            color = color_scale(value, True)
        indices = (base_path + "/" + propr + "/" + filer).replace("/", "+!+")
        name = (base_path + "/" + propc + "/" + filec).replace("/", "+!+")
        # indices = (base_path + "/" + propr + "/" + filer).replace("/", "+!+")
        # name = (base_path + "/" + propc + "/" + filec).replace("/", "+!+")
        url = f"/compare/{indices}/{name}?sim={value}"
        link = (
            f'<a href="{url}" style="{color}" class="{cl}" target="_blank">{value}</a>'
        )

    return f'<td class="{cl}">{link}</td>'


# Funzione per ottenere tutti i percorsi dei file nelle sottocartelle
def get_file_paths(folder_path):
    file_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            # print(file_path)
            if (
                file.split(".")[-1].upper() in COMPARE_FORMATS
                and file.split(".")[0] != ""
            ):
                file_paths.append(file_path)
    return file_paths


def read_file_content(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        return f"File {file_path} non trovato"


def prop_file_extract(file):
    file = file.split("/")
    prop = file[0]
    file = "/".join(file[1:])
    return prop, file


def extract_zip(zip_file, extract_path):
    with ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(extract_path)


def flatten_directory(directory):
    contents = os.listdir(directory)

    if len(contents) == 1 and os.path.isdir(os.path.join(directory, contents[0])):
        subdirectory = os.path.join(directory, contents[0])
        subcontents = os.listdir(subdirectory)

        if len(subcontents) == 1:
            subitem_path = os.path.join(subdirectory, subcontents[0])
            item_path = os.path.join(directory, subcontents[0])

            # Sposta il file nella cartella padre più vicina
            shutil.move(subitem_path, item_path)

        # Elimina la sottocartella
        os.rmdir(subdirectory)


def extract_nested_zips(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".zip"):
                zip_path = os.path.join(root, file)

                try:
                    # Ottieni il nome dell'archivio ZIP senza estensione
                    zip_name = os.path.splitext(file)[0]

                    # Crea la cartella con il nome dell'archivio ZIP
                    extracted_path = os.path.join(root, zip_name)
                    os.makedirs(extracted_path, exist_ok=True)

                    # Estrai lo zip nella cartella appena creata
                    extract_zip(zip_path, extracted_path)

                    # Appiattisci la directory
                    flatten_directory(extracted_path)

                    # Elimina l'archivio dopo averlo estratto
                    os.remove(zip_path)
                except Exception as e:
                    print(
                        f"Problema nell'estrazione di un file: {zip_path}. Errore: {e}"
                    )


def convert_formats(root_directory):
    converters = {
        ".docx": convert_docx_to_txt,
        ".pdf": convert_pdf_to_txt,
        # Aggiungi altri formati e le relative funzioni di conversione qui
    }

    for foldername, subfolders, filenames in os.walk(root_directory):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            base_name, file_extension = os.path.splitext(filename)
            converter = converters.get(file_extension.lower())

            if converter:
                txt_file_path = os.path.join(foldername, f"{base_name}.txt")
                converter(file_path, txt_file_path)
                print(
                    f"Il file {file_extension.upper()} è stato convertito in TXT: {txt_file_path}"
                )

                # Elimina il vecchio file dopo la conversione
                os.remove(file_path)
                print(
                    f"Il vecchio file {file_extension.upper()} è stato eliminato: {file_path}"
                )


def delete_temp_folder(temp_folder, delay):
    time.sleep(delay)
    shutil.rmtree(temp_folder)
    print(f"Temp folder {temp_folder} deleted")
