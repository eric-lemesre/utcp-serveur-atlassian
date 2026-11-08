"""Le contrat du sous-module, vérifié sur l'application assemblée.

Le manuel testé est ``utcp/manual.json`` ; la variable d'environnement
``ATLASSIAN_MANUEL_TEST`` permet d'en injecter un autre (manuel en cours de
rédaction, substitut).
"""

from __future__ import annotations

import json
import logging
import os
import re
import tomllib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from serveur_utcp_atlassian import utcp
from serveur_utcp_atlassian.config import Reglages
from serveur_utcp_atlassian.main import creer_application

SITE = "https://exemple.atlassian.net"
JETON = "jeton-de-test-ne-doit-jamais-sortir"
PARAM_URL = re.compile(r"(?<!\$)\{([A-Za-z0-9_]+)\}")


@pytest.fixture
def source() -> Path:
    chemin = Path(os.environ.get("ATLASSIAN_MANUEL_TEST", utcp.CHEMIN_SOURCE))
    if not chemin.is_file():
        pytest.skip(f"manuel absent : {chemin}")
    return chemin


@pytest.fixture
def client(source: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    # Les identifiants présents par erreur dans l'environnement du service ne doivent rien changer.
    monkeypatch.setenv("ATLASSIAN_USERNAME", "moi@exemple.invalid")
    monkeypatch.setenv("ATLASSIAN_API_TOKEN", JETON)
    monkeypatch.setenv("ATLASSIAN_SITE", SITE)
    return TestClient(creer_application(Reglages(), source))


def ecrire(tmp_path: Path, manuel: dict) -> Path:
    chemin = tmp_path / "manual.json"
    chemin.write_text(json.dumps(manuel), encoding="utf-8")
    return chemin


def manuel_minimal(url: str, auth: dict | None = None) -> dict:
    modele = {"call_template_type": "http", "url": url, "http_method": "GET"}
    if auth is not None:
        modele["auth"] = auth
    return {
        "manual_version": "0.1.0",
        "utcp_version": "1.0.2",
        "tools": [{"name": "t", "description": "d", "inputs": {}, "tool_call_template": modele}],
    }


def test_utcp_repond_200_sans_authentification(client: TestClient) -> None:
    assert client.get("/utcp").status_code == 200


def test_utcp_est_servi_en_json_avec_cache_court(client: TestClient) -> None:
    r = client.get("/utcp")
    assert r.headers["content-type"].startswith("application/json")
    assert r.headers["cache-control"] == "public, max-age=300"


def test_manuel_rendu_porte_utcp_version_et_des_outils(client: TestClient) -> None:
    m = client.get("/utcp").json()
    assert isinstance(m["utcp_version"], str)
    assert m["tools"]


def test_manuel_rendu_ne_contient_plus_les_marqueurs_d_url(client: TestClient) -> None:
    texte = client.get("/utcp").text
    assert "${ATLASSIAN_SITE}" not in texte
    assert "${BASE_URL}" not in texte


def test_seules_les_variables_client_restent(client: TestClient) -> None:
    restants = set(re.findall(r"\$\{([^}]*)\}", client.get("/utcp").text))
    assert restants <= {"ATLASSIAN_USERNAME", "ATLASSIAN_API_TOKEN"}


def test_chaque_url_d_outil_vise_le_site_ou_est_https(client: TestClient) -> None:
    for outil in client.get("/utcp").json()["tools"]:
        url = outil["tool_call_template"]["url"]
        assert url.startswith((SITE + "/", "https://")), outil["name"]


def test_chaque_parametre_d_url_est_declare_dans_inputs(client: TestClient) -> None:
    for outil in client.get("/utcp").json()["tools"]:
        props = outil["inputs"].get("properties", {})
        for p in PARAM_URL.findall(outil["tool_call_template"]["url"]):
            assert p in props, f"{outil['name']} : {{{p}}} absent de inputs"


def test_aucun_secret_dans_le_manuel(client: TestClient) -> None:
    r = client.get("/utcp")
    assert JETON not in r.text
    assert "ATLASSIAN_API_TOKEN=" not in r.text
    for outil in r.json()["tools"]:
        auth = outil["tool_call_template"].get("auth")
        if auth and auth.get("auth_type") == "basic":
            assert auth["username"] == "${ATLASSIAN_USERNAME}"
            assert auth["password"] == "${ATLASSIAN_API_TOKEN}"


def test_health_est_public(client: TestClient) -> None:
    assert client.get("/health").json() == {"statut": "ok"}


def test_la_reponse_porte_un_x_request_id(client: TestClient) -> None:
    assert "x-request-id" in client.get("/utcp").headers


def test_un_x_request_id_entrant_est_renvoye_tel_quel(client: TestClient) -> None:
    r = client.get("/utcp", headers={"X-Request-Id": "corr-123"})
    assert r.headers["x-request-id"] == "corr-123"


def test_le_journal_d_acces_cite_la_route_generique(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger="serveur_utcp_atlassian"):
        client.get("/utcp", headers={"X-Request-Id": "corr-9"})
        client.get("/inconnu/donnee-privee")
    lignes = [r for r in caplog.records if r.getMessage() == "requête servie"]
    assert [(r.route, r.statut) for r in lignes] == [("/utcp", 200), ("-", 404)]
    assert lignes[0].id_requete == "corr-9"
    assert "donnee-privee" not in caplog.text


def test_reglages_refusent_un_site_http_distant() -> None:
    with pytest.raises(ValidationError):
        Reglages(site="http://exemple.atlassian.net")


def test_reglages_refusent_des_identifiants_dans_l_url_du_site() -> None:
    with pytest.raises(ValidationError):
        Reglages(site="https://moi:secret@exemple.atlassian.net")


def test_reglages_acceptent_loopback_en_http_et_retirent_le_slash_final() -> None:
    assert Reglages(site="http://127.0.0.1:9000/").site == "http://127.0.0.1:9000"
    assert Reglages(site=SITE + "/").site == SITE


def test_rendre_refuse_un_marqueur_non_rendu(tmp_path: Path) -> None:
    chemin = ecrire(tmp_path, manuel_minimal("${ATLASSIAN_SITE}/x?cle=${AUTRE_SECRET}"))
    with pytest.raises(utcp.ErreurManuel, match="AUTRE_SECRET"):
        utcp.rendre(SITE, source=chemin)


def test_rendre_exige_l_url_publique_si_le_manuel_cite_base_url(tmp_path: Path) -> None:
    chemin = ecrire(tmp_path, manuel_minimal("${BASE_URL}/x"))
    with pytest.raises(utcp.ErreurManuel, match="ATLASSIAN_URL_PUBLIQUE"):
        utcp.rendre(SITE, source=chemin)
    rendu = json.loads(utcp.rendre(SITE, "https://utcp.exemple.invalid", chemin))
    assert rendu["tools"][0]["tool_call_template"]["url"] == "https://utcp.exemple.invalid/x"


def test_rendre_refuse_une_url_d_outil_http_distante(tmp_path: Path) -> None:
    chemin = ecrire(tmp_path, manuel_minimal("http://ailleurs.exemple.invalid/x"))
    with pytest.raises(utcp.ErreurManuel, match="URL refusée"):
        utcp.rendre(SITE, source=chemin)


def test_rendre_refuse_un_secret_en_clair_dans_auth(tmp_path: Path) -> None:
    auth = {"auth_type": "basic", "username": "${ATLASSIAN_USERNAME}", "password": JETON}
    chemin = ecrire(tmp_path, manuel_minimal("${ATLASSIAN_SITE}/x", auth))
    with pytest.raises(utcp.ErreurManuel, match="auth.password"):
        utcp.rendre(SITE, source=chemin)


def test_manual_version_suit_la_version_du_paquet() -> None:
    if not utcp.CHEMIN_SOURCE.is_file():
        pytest.skip("utcp/manual.json absent")
    pyproject = tomllib.loads((utcp.CHEMIN_SOURCE.parents[1] / "pyproject.toml").read_text())
    manuel = json.loads(utcp.CHEMIN_SOURCE.read_text(encoding="utf-8"))
    assert manuel["manual_version"] == pyproject["project"]["version"]
