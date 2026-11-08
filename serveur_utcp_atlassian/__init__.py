"""Fournisseur UTCP ``atlassian`` : sert le manuel des API REST Atlassian Cloud.

Forme « manuel seul » : le service publie ``GET /utcp`` et ``GET /health``,
sans route métier ; les outils du manuel appellent Atlassian Cloud directement.
Le paquet émet des journaux mais ne configure jamais ``logging`` : c'est le
rôle du seul point d'entrée, ``serveur_utcp_atlassian/__main__.py``.
"""
