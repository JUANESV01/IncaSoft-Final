import pypdf
import sys

def search_pdf(path):
    text = ""
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    
    import re
    # Extract sections related to 'tipo' or 'incapacidad'
    paragraphs = text.split("\n\n")
    for i, p in enumerate(paragraphs):
        if "Enfermedad General" in p or "tipos" in p.lower() or "días" in p.lower() or "pago" in p.lower():
            print(f"--- PARAGRAPH {i} ---")
            print(p)

search_pdf("Documentos/Proyecto_Incapacidades.pdf")
