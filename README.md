# Alura Agente – Agente de IA para documentos internos

Agente de inteligencia artificial que responde preguntas en lenguaje natural
sobre documentos internos de una empresa (PDF), usando RAG (Retrieval-Augmented
Generation) con LangChain y Gemini.

## Arquitectura

```
┌─────────────┐     ┌──────────────┐     ┌───────────────────┐
│  docs/*.pdf │ ──▶ │  ingest.py   │ ──▶ │ vectorstore/       │
│ (documento) │     │ (split +     │     │ (índice FAISS)     │
└─────────────┘     │  embeddings) │     └──────────┬─────────┘
                     └──────────────┘                │
                                                      ▼
┌─────────────┐     ┌──────────────┐     ┌───────────────────┐
│  Usuario    │ ──▶ │  app.py      │ ──▶ │  agente.py         │
│ (pregunta)  │     │ (API REST)   │     │ (RetrievalQA +      │
│             │ ◀── │              │ ◀── │  Gemini)            │
└─────────────┘     └──────────────┘     └───────────────────┘
```

**Flujo:**
1. `ingest.py` lee el PDF, lo divide en fragmentos y genera embeddings con
   Gemini (`gemini-embedding-001`), guardando todo en un índice FAISS local.
2. `agente.py` carga ese índice y arma una cadena `RetrievalQA`: ante cada
   pregunta, busca los fragmentos más relevantes y se los pasa al modelo
   `gemini-flash-latest` junto con un prompt que le indica responder solo con
   base en el contexto recuperado.
3. `app.py` expone el agente como una API REST con FastAPI, lista para
   desplegarse en una instancia de OCI Compute. Además sirve una interfaz web
   simple (`static/`) con un chat y un personaje genérico como agente, para
   probar el asistente desde el navegador sin necesidad de `curl`.

## Tecnologías

- Python 3.10+
- LangChain + langchain-google-genai
- Gemini (embeddings + LLM), vía Google AI Studio
- FAISS (vector store local)
- FastAPI + Uvicorn
- OCI Compute (deploy)

## Instrucciones para ejecutar el proyecto

### 1. Clonar el repositorio e instalar dependencias

```bash
git clone <URL_DEL_REPO>
cd alura-agente
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar la API key de Gemini

Obtené una API key gratuita en https://aistudio.google.com/app/apikey

```bash
cp .env.example .env
# Editar .env y pegar tu GOOGLE_API_KEY
```

### 3. Procesar el documento (Etapa 1)

Colocá tu PDF dentro de `docs/` y corré:

```bash
python ingest.py docs/tu_documento.pdf
```

### 4. Probar el agente por consola (Etapa 2)

```bash
python agente.py
```

### 5. Levantar la API localmente

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Probar con:

```bash
curl -X POST http://localhost:8000/preguntar \
     -H "Content-Type: application/json" \
     -d '{"pregunta": "¿Cuál es la política de vacaciones?"}'
```

## Ejemplos de preguntas y respuestas

Documento usado: *Reglamento Interno de Trabajo* de Microfinanza Calificadora
de Riesgos S.A. (Microriesg), Ecuador.

| Pregunta | Respuesta del agente |
|---|---|
| ¿Cuántos días de vacaciones tienen los trabajadores al año? | 15 días ininterrumpidos, incluidos los días no laborables (Art. 20). |
| ¿Cuál es la jornada de trabajo? | 8 horas efectivas diarias, 5 días a la semana (Art. 14). |
| ¿Está permitido fumar dentro de la empresa? | No, está expresamente prohibido (Art. 36, literal t). |
| ¿Qué pasa si un trabajador falta más de 3 días sin justificación? | La Empresa puede terminar la relación laboral mediante visto bueno (Art. 14). |
| ¿Cuál es el tope de las multas que puede aplicar la empresa? | No puede exceder el 10% de la remuneración (Art. 24 y Art. 42). |

## Deploy en OCI

*(Completar con el link público o captura de pantalla de la aplicación
corriendo en la instancia de OCI Compute)*

Pasos generales seguidos para el deploy:
1. Crear una instancia gratuita (Always Free) en OCI Compute con Ubuntu.
2. Abrir el puerto 8000 en la lista de seguridad de la VCN.
3. Conectarse por SSH, clonar el repo, instalar dependencias y configurar `.env`.
4. Ejecutar la API con Uvicorn (idealmente detrás de `systemd` o `tmux`
   para que siga corriendo tras cerrar la sesión SSH).
5. Acceder desde `http://<IP_PUBLICA_INSTANCIA>:8000`.

## Estructura del repositorio

```
alura-agente/
├── docs/                # PDFs a procesar
├── vectorstore/          # Índice FAISS generado (no versionado)
├── static/                # Interfaz web (HTML/CSS/JS) servida por app.py
├── ingest.py             # Etapa 1: procesamiento del documento
├── agente.py              # Etapa 2: agente RAG
├── app.py                 # Etapa 3: API REST + interfaz web para el deploy
├── requirements.txt
├── .env.example
└── README.md
```
