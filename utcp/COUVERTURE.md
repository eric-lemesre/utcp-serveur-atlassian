# Atlassian : couverture du manuel UTCP

Manuel `atlassian` 0.1.0, UTCP 1.0.2, 50 outils, un seul protocole `http`. Auth `basic` (`${ATLASSIAN_USERNAME}` + `${ATLASSIAN_API_TOKEN}`) ; `${ATLASSIAN_SITE}` est l'URL du site (`https://xxx.atlassian.net`). Source des cas : `etudes/atlassian-mcp-vs-utcp/synthese-couverture.md` (grilles 1, 2 et 4.1).

## 1. Outils

| Outil | Méthode | Chemin | Spec |
|---|---|---|---|
| `jira_search_jql` | GET | `/rest/api/3/search/jql` | Jira v3 |
| `jira_search_jql_post` | POST | `/rest/api/3/search/jql` | Jira v3 |
| `jira_get_issue` | GET | `/rest/api/3/issue/{issueIdOrKey}` | Jira v3 |
| `jira_create_issue` | POST | `/rest/api/3/issue` | Jira v3 |
| `jira_update_issue` | PUT | `/rest/api/3/issue/{issueIdOrKey}` | Jira v3 |
| `jira_delete_issue` | DELETE | `/rest/api/3/issue/{issueIdOrKey}` | Jira v3 |
| `jira_assign_issue` | PUT | `/rest/api/3/issue/{issueIdOrKey}/assignee` | Jira v3 |
| `jira_get_transitions` | GET | `/rest/api/3/issue/{issueIdOrKey}/transitions` | Jira v3 |
| `jira_transition_issue` | POST | `/rest/api/3/issue/{issueIdOrKey}/transitions` | Jira v3 |
| `jira_get_comments` | GET | `/rest/api/3/issue/{issueIdOrKey}/comment` | Jira v3 |
| `jira_add_comment` | POST | `/rest/api/3/issue/{issueIdOrKey}/comment` | Jira v3 |
| `jira_update_comment` | PUT | `/rest/api/3/issue/{issueIdOrKey}/comment/{id}` | Jira v3 |
| `jira_delete_comment` | DELETE | `/rest/api/3/issue/{issueIdOrKey}/comment/{id}` | Jira v3 |
| `jira_get_attachment_content` | GET | `/rest/api/3/attachment/content/{id}` | Jira v3 |
| `jira_delete_attachment` | DELETE | `/rest/api/3/attachment/{id}` | Jira v3 |
| `jira_list_worklogs` | GET | `/rest/api/3/issue/{issueIdOrKey}/worklog` | Jira v3 |
| `jira_add_worklog` | POST | `/rest/api/3/issue/{issueIdOrKey}/worklog` | Jira v3 |
| `jira_delete_worklog` | DELETE | `/rest/api/3/issue/{issueIdOrKey}/worklog/{id}` | Jira v3 |
| `jira_list_link_types` | GET | `/rest/api/3/issueLinkType` | Jira v3 |
| `jira_create_issue_link` | POST | `/rest/api/3/issueLink` | Jira v3 |
| `jira_delete_issue_link` | DELETE | `/rest/api/3/issueLink/{linkId}` | Jira v3 |
| `jira_get_remote_links` | GET | `/rest/api/3/issue/{issueIdOrKey}/remotelink` | Jira v3 |
| `jira_create_remote_link` | POST | `/rest/api/3/issue/{issueIdOrKey}/remotelink` | Jira v3 |
| `jira_delete_remote_link` | DELETE | `/rest/api/3/issue/{issueIdOrKey}/remotelink/{linkId}` | Jira v3 |
| `jira_search_projects` | GET | `/rest/api/3/project/search` | Jira v3 |
| `jira_get_project` | GET | `/rest/api/3/project/{projectIdOrKey}` | Jira v3 |
| `jira_search_users` | GET | `/rest/api/3/user/search` | Jira v3 |
| `jira_list_fields` | GET | `/rest/api/3/field` | Jira v3 |
| `jira_agile_list_boards` | GET | `/rest/agile/1.0/board` | Jira Software (Agile) |
| `jira_agile_list_sprints` | GET | `/rest/agile/1.0/board/{boardId}/sprint` | Jira Software (Agile) |
| `jira_agile_get_sprint_issues` | GET | `/rest/agile/1.0/sprint/{sprintId}/issue` | Jira Software (Agile) |
| `jira_agile_move_issues_to_sprint` | POST | `/rest/agile/1.0/sprint/{sprintId}/issue` | Jira Software (Agile) |
| `jsm_list_service_desks` | GET | `/rest/servicedeskapi/servicedesk` | JSM |
| `jsm_list_queues` | GET | `/rest/servicedeskapi/servicedesk/{serviceDeskId}/queue` | JSM |
| `jsm_get_queue_issues` | GET | `/rest/servicedeskapi/servicedesk/{serviceDeskId}/queue/{queueId}/issue` | JSM |
| `jsm_get_request_sla` | GET | `/rest/servicedeskapi/request/{issueIdOrKey}/sla` | JSM |
| `confluence_search_cql` | GET | `/wiki/rest/api/search` | Confluence v1 |
| `confluence_get_page` | GET | `/wiki/api/v2/pages/{id}` | Confluence v2 |
| `confluence_create_page` | POST | `/wiki/api/v2/pages` | Confluence v2 |
| `confluence_update_page` | PUT | `/wiki/api/v2/pages/{id}` | Confluence v2 |
| `confluence_delete_page` | DELETE | `/wiki/api/v2/pages/{id}` | Confluence v2 |
| `confluence_get_page_children` | GET | `/wiki/api/v2/pages/{id}/children` | Confluence v2 |
| `confluence_get_page_ancestors` | GET | `/wiki/api/v2/pages/{id}/ancestors` | Confluence v2 |
| `confluence_get_footer_comments` | GET | `/wiki/api/v2/pages/{id}/footer-comments` | Confluence v2 |
| `confluence_create_footer_comment` | POST | `/wiki/api/v2/footer-comments` | Confluence v2 |
| `confluence_get_inline_comments` | GET | `/wiki/api/v2/pages/{id}/inline-comments` | Confluence v2 |
| `confluence_list_page_attachments` | GET | `/wiki/api/v2/pages/{id}/attachments` | Confluence v2 |
| `confluence_list_spaces` | GET | `/wiki/api/v2/spaces` | Confluence v2 |
| `confluence_add_labels` | POST | `/wiki/rest/api/content/{id}/label` | Confluence v1 |
| `confluence_remove_label` | DELETE | `/wiki/rest/api/content/{id}/label/{label}` | Confluence v1 |

Notes de conception :
- Jira en v3 : les textes riches (description, commentaires, worklogs) sont en ADF, jamais en texte wiki.
- Recherche JQL : `/search/jql` avec `nextPageToken` ; l'ancienne `/search` est écartée. Les epics se lisent par JQL (`parent = KEY`, `issuetype = Epic`).
- Confluence : lecture et écriture de pages en v2 (`body-format`, `version.number`) ; CQL, libellés (ajout, retrait) en v1, seule à les offrir.
- Booléens de requête déclarés en `enum` `"true"`/`"false"` (chaînes), pour que la query string soit sans ambiguïté.
- Pas de tableau en paramètre de requête ; les listes sont des chaînes séparées par des virgules.
- Les pièces jointes Jira se listent par `jira_get_issue` avec `fields=attachment` ; les composants et versions d'un projet sont dans la réponse de `jira_get_project`.

## 2. Cas de la synthèse non couverts

Pour tenir la limite de 50 outils, ces opérations HTTP simples ont été laissées de côté (elles se décrivent en une ligne si besoin) :
- Métadonnées d'une pièce jointe seule (`GET /attachment/{id}`) : le ticket les renvoie déjà.
- Modification d'une saisie de temps (`PUT .../worklog/{id}`) : lecture, ajout et suppression sont couverts ; modifier = supprimer puis ajouter.
- Utilisateurs assignables (`/user/assignable/search`), profil courant (`/myself`), métadonnées de création (`/issue/createmeta/...`).
- Écriture d'un composant ou d'une version de projet (`POST /component`, `/version`), création, démarrage et clôture de sprint, tableaux (configuration, tickets), lien ticket vers epic (`POST /epic/{key}/issue`, à remplacer par `jira_update_issue` avec `fields.parent`).
- JSM : lecture et création de demandes, transitions, approbations ; seuls service desks, files, tickets de file et SLA sont décrits.
- Confluence : lecture d'un espace seul (`GET /spaces/{id}`, remplacée par le filtre `keys`/`ids` de `confluence_list_spaces`), libellés d'une page en lecture (`GET /pages/{id}/labels`), historique des versions, modification et suppression des commentaires, commentaires en ligne en écriture, résolution de pièce jointe, `descendants`.
- Confluence : tableaux blancs (`/whiteboards`) et bases de données (`/databases`).

Volontairement exclus, pour une raison de protocole :
- **Envoi de pièces jointes** (Jira `POST /issue/{key}/attachments`, Confluence `POST /content/{id}/child/attachment`) : exigent un corps `multipart/form-data` et l'en-tête `X-Atlassian-Token: no-check`. Le template `http` d'UTCP n'envoie que du JSON ; à traiter hors manuel (curl, MCP).
- **Contenu binaire** : `jira_get_attachment_content` renvoie le fichier brut ; le client le lit comme du texte, donc utile seulement pour les fichiers texte.
- **OAuth 2.0 (3LO)** et passerelle `api.atlassian.com/ex/jira/{cloudId}` : le manuel vise l'accès direct au site par jeton d'API (`basic`). OAuth 2.0 (3LO) exige un flux avec consentement utilisateur, que le `oauth2` d'UTCP (client credentials) ne fait pas.
- **Bitbucket, Assets, Compass, Opsgenie, Statuspage** : hors périmètre (Jira + Confluence + JSM seulement).
- **Découverte différée et confirmation d'écriture** de Rovo : sans équivalent UTCP ; les outils destructifs (`*_delete_*`) sont signalés dans leur description.
