from docx import Document
import fitz


def convert_docx_to_txt(docx_file_path, txt_file_path):
    doc = Document(docx_file_path)

    with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
        for paragraph in doc.paragraphs:
            txt_file.write(paragraph.text + '\n')


def convert_pdf_to_txt(pdf_file_path, txt_file_path):
    pdf_document = fitz.open(pdf_file_path)

    with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            txt_file.write(page.get_text())
