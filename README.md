# Fournisseur UTCP `atlassian`

Service FastAPI qui publie sur `GET /utcp` un manuel UTCP décrivant les API
REST d'**Atlassian Cloud** (Jira, Jira Software, Jira Service Management,
Confluence). Un agent qui charge ce manuel appelle ensuite Jira et Confluence
**directement**, sans serveur MCP intermédiaire.

Origine : étude `etudes/atlassian-mcp-vs-utcp/` du dépôt parent (synthèse de
couverture, §4) ; le détail des opérations couvertes est dans
`utcp/COUVERTURE.md`.

## Forme « manuel seul »

Le service n'a **aucune route métier** : il sert `GET /utcp` et `GET /health`,
rien d'autre. Les URL d'outils du manuel visent le site Atlassian configuré
(`ATLASSIAN_SITE`), pas ce service.

### Pourquoi pas de clé d'API

- Il n'y a rien à protéger ici : le manuel est public par nature (il décrit
  l'API publique d'Atlassian) et ne contient aucun secret.
- Les identifiants Atlassian restent des variables dans le manuel,
  `${ATLASSIAN_USERNAME}` et `${ATLASSIAN_API_TOKEN}` : c'est le **client UTCP**
  qui les fournit et les envoie à Atlassian en auth basic.
- Ils ne transitent donc **jamais** par ce service : il ne les lit pas, même
  s'ils traînent dans son environnement (aucun réglage ne les déclare).
- Le gabarit FastAPI a donc perdu ici son middleware `X-Api-Key` et le réglage
  `GABARIT_CLE_API`.

Seule précaution : `ATLASSIAN_SITE` révèle le nom du site Atlassian. Si ce nom
est confidentiel, exposer le service sur un réseau interne seulement.

## Fichiers

| Fichier | Rôle |
|---|---|
| `utcp/manual.json` | manuel source ; `${ATLASSIAN_SITE}` (et `${BASE_URL}` s'il apparaît) rendus au démarrage |
| `utcp/COUVERTURE.md` | opérations couvertes et écarts avec les serveurs MCP |
| `utcp/validation.vars` | variables rendues avant validation par `tools/valider_tous.sh` du parent |
| `serveur_utcp_atlassian/__main__.py` | seul endroit qui configure `logging`, lit les réglages, lance uvicorn ; refuse de démarrer si réglages ou manuel invalides |
| `serveur_utcp_atlassian/main.py` | `creer_application()` : `X-Request-Id` lu ou généré et renvoyé, une ligne de journal par requête sur la route générique |
| `serveur_utcp_atlassian/config.py` | réglages `ATLASSIAN_*` (pydantic-settings) ; URL HTTPS (http seulement vers loopback), sans identifiant ni slash final |
| `serveur_utcp_atlassian/utcp.py` | `rendre()` et ses contrôles, routeur `/utcp` |
| `serveur_utcp_atlassian/routes.py` | `/health` |
| `tests/test_utcp_manual.py` | contrat : `/utcp` public, JSON, cache ; marqueurs rendus ; URL d'outils ; aucun secret ; corrélation ; refus au démarrage |

## Réglages du service

| Variable | Défaut | Rôle |
|---|---|---|
| `ATLASSIAN_SITE` | — (obligatoire) | `https://<site>.atlassian.net` ; toute URL HTTPS, ou http vers loopback (tests) |
| `ATLASSIAN_URL_PUBLIQUE` | — | URL publique de ce service ; exigée seulement si le manuel cite `${BASE_URL}` |
| `ATLASSIAN_ECOUTE_HOTE` | `127.0.0.1` | adresse d'écoute |
| `ATLASSIAN_ECOUTE_PORT` | `8081` | port d'écoute |
| `ATLASSIAN_JOURNAL` | `INFO` | niveau du journal |
| `ATLASSIAN_JOURNAL_FORMAT` | `texte` | `texte` ou `json` (stderr) |

Au démarrage, `rendre()` remplace `${ATLASSIAN_SITE}` et `${BASE_URL}`, puis
refuse de démarrer, avec un message clair, si :

- `utcp_version` manque ou `tools` est vide ;
- il reste un `${…}` autre que `${ATLASSIAN_USERNAME}` et `${ATLASSIAN_API_TOKEN}` ;
- une URL d'outil n'est ni HTTPS ni loopback, ou contient un identifiant ;
- un champ secret d'`auth` (`username`, `password`, `api_key`…) n'est pas une variable `${…}`.

## Lancer

```bash
just installer                                     # uv venv + pip install -e .[dev]
ATLASSIAN_SITE=https://monsite.atlassian.net .venv/bin/python -m serveur_utcp_atlassian
# ou : just run https://monsite.atlassian.net
curl -s http://127.0.0.1:8081/utcp | jq '.tools | length'
```

## Consommer le manuel avec python-utcp

```bash
pip install utcp utcp-http
```

Template de manuel côté client (le nom `atlassian` fixe le préfixe des variables) :

```json
{
  "manual_call_templates": [
    {"name": "atlassian", "call_template_type": "http",
     "url": "http://127.0.0.1:8081/utcp", "http_method": "GET"}
  ],
  "load_variables_from": [{"variable_loader_type": "dotenv", "env_file_path": ".env"}]
}
```

Le client namespace les variables par le nom du manuel (`_` doublés, `-` → `_`,
puis `_` + variable) : il faut donc fournir, dans `.env` ou l'environnement
(voir `client.env.example`) :

```bash
atlassian_ATLASSIAN_USERNAME=prenom.nom@monentreprise.example
atlassian_ATLASSIAN_API_TOKEN=<jeton>
```

La découverte (`search_tools`) ne demande aucun jeton ; l'appel d'un outil
(`call_tool("atlassian.jira_get_issue", {...})`) en demande un. Depuis le dépôt
parent : passer l'entrée `atlassian` du catalogue à `actif: true`, lancer
`tools/generer_config_client.py`, puis `client/verifier_tous.py`.

### Créer un jeton d'API Atlassian

1. Ouvrir https://id.atlassian.com/manage-profile/security/api-tokens avec le
   compte qui fera les appels.
2. « Create API token », lui donner un nom et une date d'expiration.
3. Copier le jeton (il n'est plus affiché ensuite) dans
   `atlassian_ATLASSIAN_API_TOKEN` ; `atlassian_ATLASSIAN_USERNAME` est le
   courriel du compte.

Le jeton porte les droits de ce compte : préférer un compte dédié aux droits
limités, et ne jamais le mettre dans l'environnement du service.

## Limites

- **Pas de multipart** : l'envoi de pièces jointes (Jira, Confluence) ne se
  décrit pas en appel JSON HTTP ; le téléchargement renvoie le fichier brut.
- **Pas d'OAuth 2.0 (3LO)** : auth basic courriel + jeton d'API seulement ; la
  passerelle `api.atlassian.com/ex/jira/{cloudId}` n'est pas utilisée.
- **Cloud seulement** : Jira/Confluence Server et Data Center ont d'autres
  chemins et une autre authentification.
- Pas de conversion ADF → texte ni d'agrégation multi-appels (voir §4.2 de la
  synthèse) : un outil = un appel HTTP.

## Vérifier

```bash
just verifier        # ruff, pytest, validation du manuel (validateur du parent)
```

`ATLASSIAN_MANUEL_TEST=/chemin/autre.json .venv/bin/pytest -q` teste un autre
manuel que `utcp/manual.json`.

À tout changement de contrat, incrémenter ensemble `version` de
`pyproject.toml` et `manual_version` du manuel (un test le vérifie).
