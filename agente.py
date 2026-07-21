"""
Etapa 2: Construcción del agente de IA.

Carga el índice vectorial generado por ingest.py y arma una cadena
RetrievalQA con Gemini para responder preguntas sobre el documento.
"""

import os
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

VECTORSTORE_PATH = "vectorstore/faiss_index"

PROMPT_TEMPLATE = """Sos un asistente que responde preguntas basándote ÚNICAMENTE
en el siguiente contexto extraído de documentos internos de la empresa.
Si la respuesta no está en el contexto, decí claramente que no tenés
esa información en los documentos disponibles. No inventes datos.

Contexto:
{context}

Pregunta: {question}

Respuesta clara y concisa:"""


def cargar_agente():
    if not os.path.exists(VECTORSTORE_PATH):
        raise FileNotFoundError(
            "No se encontró el índice vectorial. Corré primero: "
            "python ingest.py docs/tu_documento.pdf"
        )

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = FAISS.load_local(
        VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True
    )

    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.2)

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE, input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )
    return qa_chain


def preguntar(qa_chain, pregunta: str) -> dict:
    resultado = qa_chain.invoke({"query": pregunta})
    return {
        "respuesta": resultado["result"],
        "fuentes": [
            f"Página {doc.metadata.get('page', '?')}"
            for doc in resultado.get("source_documents", [])
        ],
    }


if __name__ == "__main__":
    print("Cargando agente... (puede tardar unos segundos)")
    agente = cargar_agente()
    print("Agente listo. Escribí 'salir' para terminar.\n")

    while True:
        pregunta = input("Pregunta: ").strip()
        if pregunta.lower() in ("salir", "exit", "quit"):
            break
        if not pregunta:
            continue

        resultado = preguntar(agente, pregunta)
        print(f"\nRespuesta: {resultado['respuesta']}")
        print(f"Fuentes: {', '.join(resultado['fuentes'])}\n")
