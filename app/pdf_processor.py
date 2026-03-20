from io import BytesIO
import PyPDF2

def extract_text_from_pdf(contents):
    pdf = PyPDF2.PdfReader(BytesIO(contents))
    text = ""

    for page in pdf.pages:
        text += page.extract_text() or ""

    return text