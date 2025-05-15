from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import tempfile
import os
from pdf2docx import Converter

app = FastAPI()

class PDFInput(BaseModel):
    fileName: str
    base64File: str

@app.post("/convert")
async def convert_pdf_to_docx(data: PDFInput):
    try:
        # Decode and save PDF
        pdf_bytes = base64.b64decode(data.base64File)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf_path = temp_pdf.name

        # Convert PDF to DOCX
        docx_path = temp_pdf_path.replace(".pdf", ".docx")
        converter = Converter(temp_pdf_path)
        converter.convert(docx_path)
        converter.close()

        # Read and encode DOCX
        with open(docx_path, "rb") as docx_file:
            docx_bytes = docx_file.read()
            base64_docx = base64.b64encode(docx_bytes).decode()

        # Clean up
        os.remove(temp_pdf_path)
        os.remove(docx_path)

        return {
            "fileName": data.fileName.replace(".pdf", ".docx"),
            "base64File": base64_docx
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
