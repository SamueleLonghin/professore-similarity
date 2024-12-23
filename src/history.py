import json

TEMP_FILES_JSON = "temp_files.json"


def add_project_to_json(temp_folder_id, nome):
    try:
        with open(TEMP_FILES_JSON, "r") as f:
            temp_files = json.load(f)
    except FileNotFoundError:
        temp_files = []

    temp_files.append((temp_folder_id, nome))

    with open(TEMP_FILES_JSON, "w") as f:
        json.dump(temp_files, f)


def remove_project_from_json(temp_folder_id):
    try:
        with open(TEMP_FILES_JSON, "r") as f:
            temp_files = json.load(f)
    except FileNotFoundError:
        print("File JSON non trovato")

    temp_files = [
        (folder, nome) for (folder, nome) in temp_files if folder != temp_folder_id
    ]

    with open(TEMP_FILES_JSON, "w") as f:
        json.dump(temp_files, f)


def get_projects():
    try:
        with open(TEMP_FILES_JSON, "r") as f:
            temp_files = json.load(f)
    except FileNotFoundError:
        temp_files = []
    return temp_files
