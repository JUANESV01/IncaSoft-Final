import pypdf
import sys

def read_pdf(path):
    text = ""
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

full_text = read_pdf("Documentos/Proyecto_Incapacidades.pdf")
print("--- START PDF ---")
print(full_text)
print("--- END PDF ---")
