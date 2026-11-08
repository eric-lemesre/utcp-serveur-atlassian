"""Manuel UTCP : rendu au démarrage depuis ``utcp/manual.json``, servi sur ``GET /utcp``.

Le service rend ``${ATLASSIAN_SITE}`` (site Atlassian Cloud) et ``${BASE_URL}``
(sa propre URL publique, si le manuel la cite). Les identifiants Atlassian
restent des variables, ``${ATLASSIAN_USERNAME}`` et ``${ATLASSIAN_API_TOKEN}``,
que le client UTCP fournit de son côté : ils ne transitent jamais par ici.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from fastapi import APIRouter, Response

CHEMIN_SOURCE = Path(__file__).resolve().parents[1] / "utcp" / "manual.json"
MARQUEUR_SITE = "${ATLASSIAN_SITE}"
MARQUEUR_BASE_URL = "${BASE_URL}"
# Seules variables laissées au client après rendu.
VARIABLES_CLIENT = frozenset({"ATLASSIAN_USERNAME", "ATLASSIAN_API_TOKEN"})
_MARQUEUR = re.compile(r"\$\{([^}]*)\}")
_MARQUEUR_SEUL = re.compile(r"^\$\{[A-Za-z0-9_]+\}$")
# Champs d'``auth`` qui portent un secret ou un identifiant : jamais en clair dans le manuel.
_CHAMPS_SECRETS = ("username", "password", "api_key", "client_id", "client_secret", "token")
_HOTES_LOOPBACK = {"localhost", "127.0.0.1", "::1"}


class ErreurManuel(ValueError):
    """Le manuel source ou les URL configurées sont inexploitables ; arrête le service au démarrage."""


def url_outil_admise(url: str) -> bool:
    """HTTPS, ou http vers loopback (tests) ; jamais d'identifiant dans l'URL."""
    m = urlsplit(url)
    hote = (m.hostname or "").lower()
    if m.username or m.password or not hote:
        return False
    return m.scheme == "https" or (
        m.scheme == "http" and (hote in _HOTES_LOOPBACK or hote.startswith("127."))
    )


def _verifier(manuel: Any) -> None:
    if not isinstance(manuel, dict):
        raise ErreurManuel("manuel source : un objet JSON est attendu")
    if not isinstance(manuel.get("utcp_version"), str):
        raise ErreurManuel("manuel source : champ `utcp_version` absent")
    outils = manuel.get("tools")
    if not isinstance(outils, list) or not outils:
        raise ErreurManuel("manuel source : champ `tools` absent ou vide")
    for outil in outils:
        nom = outil.get("name", "?") if isinstance(outil, dict) else "?"
        modele = outil.get("tool_call_template") if isinstance(outil, dict) else None
        if not isinstance(modele, dict):
            raise ErreurManuel(f"outil {nom} : `tool_call_template` absent")
        url = modele.get("url")
        if not isinstance(url, str) or not url_outil_admise(url):
            raise ErreurManuel(f"outil {nom} : URL refusée (https ou loopback obligatoire) : {url}")
        auth = modele.get("auth") or {}
        for champ in _CHAMPS_SECRETS:
            valeur = auth.get(champ)
            if valeur is not None and not (
                isinstance(valeur, str) and _MARQUEUR_SEUL.match(valeur)
            ):
                # La valeur n'est pas citée : c'est peut-être un secret.
                raise ErreurManuel(f"outil {nom} : `auth.{champ}` doit être une variable ${{…}}")


def rendre(site: str, url_publique: str | None = None, source: Path = CHEMIN_SOURCE) -> bytes:
    """Rend ``${ATLASSIAN_SITE}`` et ``${BASE_URL}``, vérifie le manuel, le sérialise une fois.

    ``site`` et ``url_publique`` arrivent validés par ``Reglages`` (HTTPS ou
    loopback, sans slash final). Toute anomalie lève ``ErreurManuel``.
    """
    try:
        texte = source.read_text(encoding="utf-8")
    except OSError as e:
        raise ErreurManuel(f"manuel source illisible : {source} ({e.strerror})") from e
    texte = texte.replace(MARQUEUR_SITE, site.rstrip("/"))
    if MARQUEUR_BASE_URL in texte:
        if not url_publique:
            raise ErreurManuel("le manuel cite ${BASE_URL} : définir ATLASSIAN_URL_PUBLIQUE")
        texte = texte.replace(MARQUEUR_BASE_URL, url_publique.rstrip("/"))
    restants = sorted(set(_MARQUEUR.findall(texte)) - VARIABLES_CLIENT)
    if restants:
        raise ErreurManuel(
            "marqueur(s) non rendu(s) dans le manuel : " + ", ".join(f"${{{v}}}" for v in restants)
        )
    try:
        manuel = json.loads(texte)
    except json.JSONDecodeError as e:
        raise ErreurManuel(f"manuel source invalide : {e}") from e
    _verifier(manuel)
    return json.dumps(manuel, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def routeur(manuel: bytes) -> APIRouter:
    """Routeur autonome pour ``GET /utcp`` (public : le manuel ne contient aucun secret)."""
    r = APIRouter()

    @r.get("/utcp", include_in_schema=False)
    def servir() -> Response:
        return Response(
            content=manuel,
            media_type="application/json",
            # Le manuel change avec le déploiement, pas avec les données : cache court.
            headers={"Cache-Control": "public, max-age=300"},
        )

    return r
