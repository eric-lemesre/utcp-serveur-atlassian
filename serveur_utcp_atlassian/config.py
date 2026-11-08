"""Réglages lus dans l'environnement, préfixe ``ATLASSIAN_``."""

from __future__ import annotations

from urllib.parse import urlsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_HOTES_LOOPBACK = {"localhost", "127.0.0.1", "::1"}


def valider_url_https(url: str, quoi: str) -> str:
    """URL HTTPS (ou http vers loopback), sans identifiants, requête ni fragment ; slash final retiré.

    Les deux URL finissent dans un manuel public : un identifiant glissé dans
    l'URL (``https://moi:jeton@…``) y serait publié, d'où le refus.
    """
    url = url.strip().rstrip("/")
    morceaux = urlsplit(url)
    hote = (morceaux.hostname or "").lower()
    loopback = hote in _HOTES_LOOPBACK or hote.startswith("127.")
    if morceaux.scheme == "https" or (morceaux.scheme == "http" and loopback):
        pass
    else:
        raise ValueError(f"{quoi} refusée : https obligatoire, http seulement vers loopback")
    if not hote:
        raise ValueError(f"{quoi} refusée : hôte absent")
    if morceaux.username or morceaux.password:
        raise ValueError(f"{quoi} refusée : pas d'identifiant dans l'URL")
    if morceaux.query or morceaux.fragment:
        raise ValueError(f"{quoi} refusée : ni requête ni fragment")
    return url


class Reglages(BaseSettings):
    """Réglages du service.

    Aucun secret ici : le service n'a pas de route métier à protéger, et les
    identifiants Atlassian (``ATLASSIAN_USERNAME``, ``ATLASSIAN_API_TOKEN``)
    sont fournis par le client UTCP, jamais par ce service. Une variable
    ``ATLASSIAN_API_TOKEN`` présente par erreur dans l'environnement du service
    est ignorée (aucun champ ne la lit).
    """

    model_config = SettingsConfigDict(env_prefix="ATLASSIAN_", extra="ignore")

    site: str = Field(
        description="Site Atlassian Cloud, ex. https://monsite.atlassian.net ; "
        "rendu dans le manuel à la place de ${ATLASSIAN_SITE}"
    )
    url_publique: str | None = Field(
        default=None,
        description="URL publique de ce service, rendue à la place de ${BASE_URL} s'il apparaît",
    )
    ecoute_hote: str = "127.0.0.1"
    ecoute_port: int = Field(default=8081, ge=1, le=65535)
    journal: str = Field(default="INFO", description="Niveau du journal racine")
    journal_format: str = Field(default="texte", description="texte ou json")

    @field_validator("site")
    @classmethod
    def _site(cls, v: str) -> str:
        return valider_url_https(v, "ATLASSIAN_SITE")

    @field_validator("url_publique")
    @classmethod
    def _url_publique(cls, v: str | None) -> str | None:
        return None if v is None else valider_url_https(v, "ATLASSIAN_URL_PUBLIQUE")
