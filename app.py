"""
Etapa 3: Implementación (Deploy).

Expone el agente como una API web con FastAPI, lista para correr en
una instancia de OCI Compute.

Uso local:
    uvicorn app:app --host 0.0.0.0 --port 8000

Luego probar con:
    curl -X POST http://localhost:8000/preguntar \
         -H "Content-Type: application/json" \
         -d '{"pregunta": "¿Cuál es la política de vacaciones?"}'
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agente import cargar_agente, preguntar

app = FastAPI(
    title="Alura Agente - Agente de IA para documentos internos",
    description="API que responde preguntas en lenguaje natural sobre documentos internos.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

qa_chain = None


class PreguntaRequest(BaseModel):
    pregunta: str


@app.on_event("startup")
def iniciar_agente():
    global qa_chain
    qa_chain = cargar_agente()


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/status")
def estado():
    return {"status": "ok", "mensaje": "El agente está corriendo. Usá POST /preguntar"}


@app.post("/preguntar")
def endpoint_preguntar(request: PreguntaRequest):
    if qa_chain is None:
        raise HTTPException(status_code=503, detail="El agente todavía no está listo.")
    if not request.pregunta.strip():
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")

    resultado = preguntar(qa_chain, request.pregunta)
    return resultado
