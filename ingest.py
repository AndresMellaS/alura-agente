"""
Etapa 1: Procesamiento del documento.

Este script:
1. Lee un PDF ubicado en docs/
2. Lo divide en fragmentos (chunks) manejables
3. Genera embeddings con Gemini
4. Guarda un índice vectorial FAISS en vectorstore/ para reutilizarlo después

Uso:
    python ingest.py docs/mi_documento.pdf
"""

import sys
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

VECTORSTORE_PATH = "vectorstore/faiss_index"


def procesar_pdf(ruta_pdf: str) -> None:
    if not os.path.exists(ruta_pdf):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_pdf}")

    print(f"Leyendo documento: {ruta_pdf}")
    loader = PyPDFLoader(ruta_pdf)
    paginas = loader.load()
    print(f"  -> {len(paginas)} páginas cargadas")

    print("Dividiendo el documento en fragmentos...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(paginas)
    print(f"  -> {len(chunks)} fragmentos generados")

    print("Generando embeddings con Gemini y creando el índice FAISS...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"Índice guardado en: {VECTORSTORE_PATH}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ingest.py docs/mi_documento.pdf")
        sys.exit(1)

    procesar_pdf(sys.argv[1])
