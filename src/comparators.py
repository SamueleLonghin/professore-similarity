import difflib
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from src.support import read_file_content


def compare_files(file1, file2):
    # Apertura dei file
    try:
        with open(file1, "r") as f1, open(file2, "r") as f2:
            # Lettura delle righe dei file
            lines1 = f1.readlines()
            lines2 = f2.readlines()

    except Exception:
        return -1
    # Identificazione delle regex nei file
    regex1 = [re.findall(r"\.+\S+", line) for line in lines1]
    regex2 = [re.findall(r"\.+\S+", line) for line in lines2]

    # Flatizzazione delle liste di regex
    regex1 = [item for sublist in regex1 for item in sublist]
    regex2 = [item for sublist in regex2 for item in sublist]

    # Confronto delle regex utilizzando difflib
    differ = difflib.Differ()
    diff = differ.compare(regex1, regex2)

    diff = [d for d in diff]

    # Calcolo del punteggio di somiglianza
    if len(diff) == 0:
        return 1
    similarity = len([line for line in diff if line.startswith(" ")]) / len(diff)

    return similarity


def preprocess_text(text):
    try:
        l = stopwords.words("english")
    except Exception:
        nltk.download('stopwords')
        nltk.download('punkt')
    stop_words = set(stopwords.words("english") + stopwords.words("italian"))
    words = word_tokenize(text)
    words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]
    return " ".join(words)


def cosine_compare_files(file1, file2):
    text1 = read_file_content(file1)
    text2 = read_file_content(file2)
    # with open(file1, 'r', encoding='utf-8') as f:
    #     text1 = f.read()

    # with open(file2, 'r', encoding='utf-8') as f:
    #     text2 = f.read()

    text1 = preprocess_text(text1)
    text2 = preprocess_text(text2)

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([text1, text2])

    similarity = cosine_similarity(vectors)
    return similarity[0, 1]


def spacy_compare_file(file1, file2):
    import spacy
    # Nome del modello
    # model_name = "en_core_web_sm"
    model_name = "it_core_news_sm"

    # Controlla se il modello è già installato
    try:
        npl = spacy.load(model_name)
    except Exception:
        # Scarica il modello solo se non è presente

        print("SCARICOOOO")
        spacy.cli.download(model_name)
    nlp = spacy.load(model_name)

    with open(file1, 'r', encoding='utf-8') as f:
        text1 = f.read()

    with open(file2, 'r', encoding='utf-8') as f:
        text2 = f.read()

    doc1 = nlp(text1)
    doc2 = nlp(text2)

    similarity_score = doc1.similarity(doc2)
    return similarity_score


comparators = {
    'classic': compare_files,
    'cosine': cosine_compare_files,
    'spacy': spacy_compare_file
}
