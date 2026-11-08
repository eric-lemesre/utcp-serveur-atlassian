"""Assemblage de l'application FastAPI."""

from __future__ import annotations

import logging
import uuid
from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import FastAPI, Request, Response

from serveur_utcp_atlassian import routes, utcp
from serveur_utcp_atlassian.config import Reglages

journal = logging.getLogger("serveur_utcp_atlassian")


def creer_application(reglages: Reglages, source: Path = utcp.CHEMIN_SOURCE) -> FastAPI:
    """``/utcp`` et ``/health`` publics, ``X-Request-Id`` lu ou généré et renvoyé.

    ``source`` désigne le manuel à rendre ; les tests y injectent un autre fichier.
    """
    # Échoue au démarrage, pas à la requête.
    manuel = utcp.rendre(reglages.site, reglages.url_publique, source)
    app = FastAPI(title="Fournisseur UTCP atlassian", docs_url=None, redoc_url=None)
    app.state.reglages = reglages
    app.include_router(routes.public)
    app.include_router(utcp.routeur(manuel))

    @app.middleware("http")
    async def correlation(
        request: Request, suite: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        id_requete = request.headers.get("x-request-id") or uuid.uuid4().hex
        request.state.id_requete = id_requete
        reponse = await suite(request)
        reponse.headers["X-Request-Id"] = id_requete
        # Route générique, jamais le chemin brut.
        route = getattr(request.scope.get("route"), "path", "-")
        journal.info(
            "requête servie",
            extra={
                "id_requete": id_requete,
                "methode": request.method,
                "route": route,
                "statut": reponse.status_code,
            },
        )
        return reponse

    return app
