from PyPDF2 import PdfReader

def extract_text_from_file(file_like, filename: str):
    fname = filename.lower()
    if fname.endswith(".pdf"):
        reader = PdfReader(file_like)
        pages = []
        for p in reader.pages:
            t = p.extract_text()
            if t:
                pages.append(t)
        return "\n\n".join(pages)
    else:
        # assume text file
        file_like.seek(0)
        try:
            return file_like.read().decode("utf-8")
        except Exception:
            return ""
