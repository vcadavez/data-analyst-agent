import os
import shutil
import logging
import asyncio

from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.agent import run_agent
from backend.tools.tool_list import TOOLS
from backend.indexer import load_index, build_index, query_index
from backend.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AGENTE")

tool_dict = {tool.name: tool for tool in TOOLS}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variável global para o índice e o lock assíncrono
index_cache = None
index_lock = asyncio.Lock()

async def get_index():
    global index_cache
    async with index_lock:
        if index_cache is None:
            logger.info("🔄 Carregando índice pela primeira vez...")
            index_cache = load_index()
    return index_cache

@app.get("/ping")
async def ping():
    return {"ok": True}


@app.post("/analyse")
async def analyse(request: Request):
    data = await request.json()
    prompt = data.get("question")
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing 'question' in request.")

    try:
        # Get index and query
        idx = await get_index()
        query_response = query_index(idx, prompt)

        # Run agent
        agent_response = run_agent(prompt)

        return {
            "query_answer": str(query_response),
            "agent_answer": agent_response,
        }
    except Exception as e:
        logger.error(f"Erro na análise: {e}")
        return JSONResponse(status_code=500, content={"error": f"Erro na análise: {str(e)}"})


@app.post("/query", deprecated=True)
async def query(request: Request):
    data = await request.json()
    prompt = data.get("question")
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing 'question' in request.")

    try:
        idx = await get_index()
        response = query_index(idx, prompt)
        return {"answer": str(response)}
    except Exception as e:
        logger.error(f"Erro na consulta ao índice: {e}")
        return JSONResponse(status_code=500, content={"error": f"Erro na consulta ao índice: {str(e)}"})


@app.post("/agent", deprecated=True)
async def agent_endpoint(request: Request):
    data = await request.json()
    prompt = data.get("question")
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing 'question' in request.")

    try:
        response = run_agent(prompt)
        return {"answer": response}
    except Exception as e:
        logger.error(f"Erro no agente: {e}")
        return JSONResponse(status_code=500, content={"error": f"Erro no agente: {str(e)}"})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        upload_path = settings.csv_path
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # ------------ Auto-reindex aqui ------------
        from backend.indexer import build_index
        build_index(csv_path=upload_path)
        # -------------------------------------------

        file_size = os.path.getsize(upload_path)
        logger.info(f"✅ Ficheiro '{file.filename}' carregado ({file_size} bytes).")
        return {"status": "success", "message": f"Ficheiro '{file.filename}' carregado e indexado com sucesso."}
    except Exception as e:
        logger.error(f"❌ Erro ao carregar/indexar ficheiro: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/reindex")
async def reindex_endpoint():
    global index_cache
    async with index_lock:
        try:
            index_cache = build_index(csv_path=settings.csv_path)
            logger.info("🔁 Índice reindexado manualmente.")
            return {"status": "success", "message": "Índice reindexado com sucesso."}
        except Exception as e:
            logger.error(f"❌ Erro ao reindexar: {e}")
            return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/tool")
async def tool_endpoint(request: Request):
    data = await request.json()
    tool_name = data.get("tool")
    tool_args = data.get("args", {})

    if tool_name not in tool_dict:
        return JSONResponse(
            status_code=400,
            content={
                "error": f"❌ Ferramenta '{tool_name}' não encontrada. Ferramentas disponíveis: {list(tool_dict)}"
            },
        )

    try:
        tool = tool_dict[tool_name]
        
        # Envolve a execução síncrona da ferramenta em `run_in_executor`
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,  # Usa o executor padrão (ThreadPoolExecutor)
            lambda: tool.invoke(tool_args) if hasattr(tool, "invoke") else tool(tool_args)
        )

        return {"result": result}
    except Exception as e:
        logger.error(f"Erro ao executar '{tool_name}': {e}")
        return JSONResponse(status_code=500, content={"error": f"Erro ao executar '{tool_name}': {str(e)}"})

@app.get("/history/{thread_id}")
async def get_history(thread_id: str):
    import sqlite3
    from langgraph.checkpoint.sqlite import SqliteSaver
    conn = sqlite3.connect("agent_memory.db", check_same_thread=False)
    memory = SqliteSaver(conn)
    return memory.get_thread(thread_id)
