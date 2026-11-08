# Commandes du fournisseur atlassian. `just` : https://just.systems

validateur := env_var_or_default("UTCP_VALIDATEUR", "../../tools/valider_manuel.py")

# Tout ce que la CI vérifie
verifier: lint test valider

installer:
    uv venv .venv && uv pip install --python .venv/bin/python -e ".[dev]"

lint:
    .venv/bin/ruff check . && .venv/bin/ruff format --check .

test:
    .venv/bin/pytest -q

# Valide le manuel source (${ATLASSIAN_SITE} et ${BASE_URL} rendus avec des URL fictives)
valider:
    python3 -I {{validateur}} utcp/manual.json --var ATLASSIAN_SITE=https://exemple.atlassian.net --var BASE_URL=https://validation.invalid --strict

# Lance en local ; le manuel est alors servi sur http://127.0.0.1:8081/utcp
run site="https://exemple.atlassian.net":
    ATLASSIAN_SITE={{site}} ATLASSIAN_ECOUTE_PORT=8081 .venv/bin/python -m serveur_utcp_atlassian
