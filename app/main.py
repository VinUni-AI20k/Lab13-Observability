from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from structlog.contextvars import bind_contextvars

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None

from .agent import LabAgent
from .dashboard import build_dashboard_series
from .incidents import disable, enable, status
from .logging_config import configure_logging, get_logger
from .metrics import record_error, snapshot
from .middleware import CorrelationIdMiddleware
from .pii import hash_user_id, summarize_text
from .schemas import ChatRequest, ChatResponse
from .tracing import get_tracing_status, safe_flush, safe_update_current_observation

if load_dotenv is not None:
    load_dotenv()

configure_logging()
log = get_logger()
app = FastAPI(title="Day 13 Observability Lab")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.add_middleware(CorrelationIdMiddleware)
agent = LabAgent()


@app.on_event("startup")
async def startup() -> None:
    tracing = get_tracing_status()
    log.info(
        "app_started",
        service=os.getenv("APP_NAME", "day13-observability-lab"),
        env=os.getenv("APP_ENV", "dev"),
        correlation_id="startup",
        user_id_hash=None,
        session_id=None,
        feature=None,
        model=None,
        payload={"tracing": tracing},
    )


@app.get("/health")
async def health() -> dict:
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    return {
        "ok": True,
        "tracing": get_tracing_status(),
        "langfuse_base_url": os.getenv("LANGFUSE_BASE_URL"),
        "langfuse_public_key_prefix": public_key[:12] if public_key else None,
        "incidents": status(),
    }


@app.on_event("shutdown")
async def shutdown() -> None:
    safe_flush()


@app.get("/metrics")
async def metrics() -> dict:
    return snapshot()


@app.get("/dashboard/series")
async def dashboard_series(window_minutes: int = 60, bucket_seconds: int = 60) -> dict:
    log_path = os.getenv("LOG_PATH", "data/logs.jsonl")
    return build_dashboard_series(log_path=log_path, window_minutes=window_minutes, bucket_seconds=bucket_seconds)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    # Enrich logs with request context (user_id_hash, session_id, feature, model, env)
    bind_contextvars(
        user_id_hash=hash_user_id(body.user_id),
        session_id=body.session_id,
        feature=body.feature,
        model=getattr(agent, "model", None),
        env=os.getenv("APP_ENV", "dev"),
    )
    
    log.info(
        "request_received",
        service="api",
        correlation_id=request.state.correlation_id,
        user_id_hash=hash_user_id(body.user_id),
        session_id=body.session_id,
        feature=body.feature,
        model=getattr(agent, "model", None),
        env=os.getenv("APP_ENV", "dev"),
        payload={"message_preview": summarize_text(body.message)},
    )

    try:
        result = agent.run(
            user_id=body.user_id,
            feature=body.feature,
            session_id=body.session_id,
            message=body.message,
            correlation_id=request.state.correlation_id,
        )
        log.info(
            "response_sent",
            service="api",
            correlation_id=request.state.correlation_id,
            user_id_hash=hash_user_id(body.user_id),
            session_id=body.session_id,
            feature=body.feature,
            model=getattr(agent, "model", None),
            env=os.getenv("APP_ENV", "dev"),
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            payload={"answer_preview": summarize_text(result.answer)},
        )
        return ChatResponse(
            answer=result.answer,
            correlation_id=request.state.correlation_id,
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
        )
    except Exception as exc:  # pragma: no cover
        error_type = type(exc).__name__
        record_error(error_type)
        incidents = status()
        log.error(
            "request_failed",
            service="api",
            correlation_id=request.state.correlation_id,
            user_id_hash=hash_user_id(body.user_id),
            session_id=body.session_id,
            feature=body.feature,
            model=getattr(agent, "model", None),
            env=os.getenv("APP_ENV", "dev"),
            error_type=error_type,
            payload={"detail": str(exc), "message_preview": summarize_text(body.message)},
        )
        raise HTTPException(status_code=500, detail=error_type) from exc
    finally:
        safe_flush()


@app.post("/incidents/{name}/enable")
async def enable_incident(name: str) -> JSONResponse:
    try:
        enable(name)
        log.warning(
            "incident_enabled",
            service="control",
            correlation_id=f"incident-{name}",
            user_id_hash=None,
            session_id=None,
            feature=None,
            model=None,
            env=os.getenv("APP_ENV", "dev"),
            payload={"name": name},
        )
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/incidents/{name}/disable")
async def disable_incident(name: str) -> JSONResponse:
    try:
        disable(name)
        log.warning(
            "incident_disabled",
            service="control",
            correlation_id=f"incident-{name}",
            user_id_hash=None,
            session_id=None,
            feature=None,
            model=None,
            env=os.getenv("APP_ENV", "dev"),
            payload={"name": name},
        )
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
