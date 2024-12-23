from src.comparators import comparators, compare_files
from src.support import get_file_paths, format_cell, prop_file_extract
from flask import render_template


def create_similarity_dict(file_paths, comparator):
    n = len(file_paths)
    D = dict()
    for i in range(n):
        for j in range(i + 1, n):
            file1 = file_paths[i]
            file2 = file_paths[j]
            if file1 != file2:
                similarity = comparator(file1, file2)
                k = frozenset({i, j})
                D[k] = similarity
    return D


def create_html_similarity_matrix(D, base_path, file_paths):
    headers_extract = [prop_file_extract(filer) for filer in file_paths]

    TABLE = "<table class='matrix'><thead>"
    TABLE += "<tr><th class='text-center'>Proprietario</th><th></th>"

    # Create header with rowspan for consecutive same names
    last_prop = None
    rowspan = 0
    for prop, _ in headers_extract:
        if prop == last_prop:
            rowspan += 1
        else:
            if last_prop is not None:
                TABLE += f"<th colspan='{rowspan}'> {last_prop.upper()} </th>"
            last_prop = prop
            rowspan = 1
    TABLE += (
        f"<th colspan='{rowspan}'> {last_prop.upper()} </th>"
    )
    TABLE += "</tr>"

    TABLE += "<tr><th></th><th class='text-center'>File</th>"
    for _, file in headers_extract:
        TABLE += f"<th> {file} </th>"
    TABLE += "</tr>"
    TABLE += "</thead> <tbody>"

    last_prop = None
    rowspan = 0
    accumulator = []
    for ir, (propr, filer) in enumerate(headers_extract):
        row = []
        for ic, (propc, filec) in enumerate(headers_extract):
            row.append(
                format_cell(
                    D.get(frozenset({ir, ic}), 0), base_path, propr, filer, propc, filec
                )
            )

        if propr != last_prop and last_prop != None:
            # scrivo la riga precedente
            title = f"<th rowspan='{rowspan}'> {last_prop.upper()} </th> "
            accumulator[0] = title + accumulator[0]
            TABLE += "<tr>" + "</tr><tr>".join(accumulator) + "</tr>"
            accumulator = []
        else:
            # sono uguale, conto
            rowspan += 1
        # aggiungo la riga attuale all'accumulatore del proprietario
        accumulator.append(f"<th> {filer} </th>" + "".join(row))
        if propr != last_prop:
            last_prop = propr
            rowspan = 1
    else:
        # ultimo giro
        title = f"<th rowspan='{rowspan}'> {last_prop.upper()} </th> "
        accumulator[0] = title + accumulator[0]
        TABLE += "<tr>" + "</tr><tr>".join(accumulator) + "</tr>"

    TABLE += "</tbody> </table>"
    return TABLE


def create_html_sorted_similarity_list(D, base_path, file_paths):
    # Ordino il dizionario in base al valore di somiglianza decrescente
    sorted_dict = sorted(D.items(), key=lambda item: item[1], reverse=True)

    LIST = ""
    for (a, b), value in sorted_dict:
        propr, filer = prop_file_extract(file_paths[a])
        propc, filec = prop_file_extract(file_paths[b])
        value = format_cell(value, base_path, propr, filer, propc, filec)
        LIST += f"""<tr> <td>{filer}</td> <td>{propr.upper()}</td> {value} <td>{propc.upper()}</td> <td>{filec}</td> </tr>"""
    return LIST


def similarity_html(base_path, algorithm, temp_folder_id):
    # trovo il comparatore o metto quello classico
    comparator = comparators.get(algorithm, compare_files)

    file_paths = get_file_paths(base_path)

    D = create_similarity_dict(file_paths, comparator)

    # pulisco i file paths rinuovando il base path
    file_paths = [fp.replace(base_path + "/", "") for fp in file_paths]

    # Creo la matrice di somiglianza
    TABLE = create_html_similarity_matrix(D, temp_folder_id, file_paths)

    LIST = create_html_sorted_similarity_list(D, temp_folder_id, file_paths)

    share_link = f"/tabella/{algorithm}/{temp_folder_id}"

    return render_template(
        "tabella.html", table_html=TABLE, list_html=LIST, share_link=share_link
    )
