"""FastAPI app creation, logger configuration and main API routes."""
import logging

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from injector import Injector


from server.routes.health.health_router import health_router
from server.routes.completion.completion_router import completions_router
from server.routes.token.token_router import token_router
from server.routes.summarize.summarize_router import summarize_router 
from server.routes.scrap.scrap_router import scrap_router
from server.routes.load_document.load_document_router import load_document_router 
from settings.settings import Settings

logger = logging.getLogger(__name__)


def create_app(root_injector: Injector) -> FastAPI:

    # Start the API
    async def bind_injector_to_request(request: Request) -> None:
        request.state.injector = root_injector

    app = FastAPI(dependencies=[Depends(bind_injector_to_request)])

    app.include_router(health_router)
    app.include_router(completions_router)
    app.include_router(token_router)
    app.include_router(summarize_router)
    app.include_router(scrap_router)
    app.include_router(load_document_router)

    settings = root_injector.get(Settings)
    if settings.server.cors.enabled:
        logger.debug("Setting up CORS middleware")
        app.add_middleware(
            CORSMiddleware,
            allow_credentials=settings.server.cors.allow_credentials,
            allow_origins=settings.server.cors.allow_origins,
            allow_origin_regex=settings.server.cors.allow_origin_regex,
            allow_methods=settings.server.cors.allow_methods,
            allow_headers=settings.server.cors.allow_headers,
        )

    return app
