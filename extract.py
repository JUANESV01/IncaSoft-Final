import pypdf
import docx
import sys

def read_pdf(path):
    text = ""
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def read_docx(path):
    doc = docx.Document(path)
    return "\n".join([p.text for p in doc.paragraphs])

print("--- Proyecto_Incapacidades.pdf ---")
print(read_pdf("Documentos/Proyecto_Incapacidades.pdf")[:2000])

print("\n--- IncaSoft_Vision_Alcance.docx ---")
print(read_docx("Documentos/IncaSoft_Vision_Alcance.docx")[:2000])

