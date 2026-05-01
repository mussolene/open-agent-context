from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from oacs import __version__
from oacs.api.routes_audit import router as audit_router
from oacs.api.routes_benchmark import router as benchmark_router
from oacs.api.routes_context import router as context_router
from oacs.api.routes_memory import router as memory_router
from oacs.core.errors import AccessDenied, NotFound, OacsError


def create_app() -> FastAPI:
    app = FastAPI(title="OACS API", version=__version__)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.exception_handler(AccessDenied)
    def access_denied_handler(request, exc: AccessDenied) -> JSONResponse:  # noqa: ANN001
        return JSONResponse(status_code=403, content={"error": str(exc)})

    @app.exception_handler(NotFound)
    def not_found_handler(request, exc: NotFound) -> JSONResponse:  # noqa: ANN001
        return JSONResponse(status_code=404, content={"error": str(exc)})

    @app.exception_handler(OacsError)
    def oacs_error_handler(request, exc: OacsError) -> JSONResponse:  # noqa: ANN001
        return JSONResponse(status_code=400, content={"error": str(exc)})

    app.include_router(memory_router)
    app.include_router(context_router)
    app.include_router(audit_router)
    app.include_router(benchmark_router)
    return app


app = create_app()
