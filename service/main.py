#!/usr/bin/env python3

import os

import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import llm
from pathlib import Path
from dotenv import load_dotenv
import logging
from pythonjsonlogger.json import JsonFormatter
import time
from context import request_id

load_dotenv()


class LlmRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User query to the model",
        examples=["Why is the sky blue?"],
    )


class LlmResponse(BaseModel):
    message: str = Field(
        ...,
        description="Response from the model",
        examples=[
            "The sky appears blue due to the scattering of sunlight by the atmosphere."
        ],
    )

class LogRequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id.get()
        return True
    
def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter(
        "%(asctime)s %(levelname)s %(message)s",
        rename_fields={"levelname": "level", "asctime": "timestamp"},
    ))
    handler.addFilter(LogRequestIdFilter())      
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), handlers=[handler])
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    app.state.system_prompt = Path(os.getenv("SYSTEM_PROMPT_PATH")).read_text(
        encoding="utf-8"
    )
    yield


app = FastAPI(
    lifespan=lifespan,
    title="RAG Platform — Inference Service",
    description="Self-hosted LLM-inference service",
    version="0.1.0",
)
log = logging.getLogger(__name__)



@app.middleware("http")
async def log_requests(request, call_next):
    start = time.perf_counter()
    rid = str(uuid.uuid4())
    request_id.set(rid)
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    log.info(
        "request_handled",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 1),
        },
    )
    response.headers["X-Request-ID"] = rid   
    return response

@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint to verify that the service is running. Returns a simple status message.
    """
    return JSONResponse(content={"status": "ok"})


@app.get("/ready", tags=["Health"])
def ready_check():
    """
    Readiness check endpoint to verify that the service is ready to accept requests. Returns a simple status message.
    """
    if not llm.check_model_ready():
        return JSONResponse(content={"status": "not ready"}, status_code=503)
    return JSONResponse(content={"status": "ready"})


@app.post(
    "/ask",
    response_model=LlmResponse,
    summary="LLM Query Endpoint",
    description="Endpoint to query the language model with a user prompt.",
)
def ask(request: LlmRequest):
    """
    Handle incoming LLM query and return the response.
    """
    try:
        response = llm.query(request.query, system_prompt=app.state.system_prompt)
    except llm.InferenceTimeoutError:
        raise HTTPException(status_code=504, detail="Inference request timed out")
    except llm.InferenceError:
        raise HTTPException(status_code=503, detail="Inference service unavailable")
    return {"message": response}
