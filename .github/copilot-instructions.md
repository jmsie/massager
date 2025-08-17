# Copilot Instructions for massager

## Project Overview
- This is a Django 3.2 project for managing massage therapists and stores, with REST API endpoints and web views.
- Main app: `panel` (models, views, serializers, templates)
- Project config: `project` (settings, URLs)
- Uses PostgreSQL (see `docker-compose.yml`), and is containerized for local/dev/prod use.

## Key Architecture & Data Flow
- **User/Store Relationship**: Each `Store` is linked to a Django `User` via a OneToOneField (`Store.user`).
- **Therapist Management**: `Therapist` objects belong to a `Store` (ForeignKey). Soft delete is implemented via `is_deleted` Boolean field.
- **API**: DRF `ModelViewSet` for `Therapist` (`panel/views.py`). Querysets filter by current user's store and exclude deleted therapists.
- **Session/Authentication**: Login sets `store_name` in session. API creation uses this to associate new therapists with the correct store.
- **Web Views**: HTML templates in `panel/templates/panel/`. Admin and portal views use Django's session and authentication.

## Developer Workflows
- **Build/Run**: Use Docker (`docker-compose.yml`) for local dev. Entrypoint runs migrations, collects static files, and starts server.
- **Database**: PostgreSQL. Connection details set via environment variables in Docker Compose.
- **Static Files**: Managed via Django's `collectstatic`. Served by Nginx in production.
- **Custom Management Commands**: Place in `panel/management/commands/`. Use for custom ORM queries or admin tasks.
- **Testing**: Tests live in `panel/tests.py`. Use `python manage.py test panel`.

## Project-Specific Patterns
- **Soft Delete**: Always filter `Therapist` by `is_deleted=False` in queries and API responses.
- **Store Context**: Always use session or user context to determine the current store for API and web actions.
- **Serializer Validation**: See `panel/serializers.py` for custom field cleaning and validation.
- **API Routing**: DRF router in `panel/urls.py` exposes `/api/therapists/` endpoint.
- **Settings**: All sensitive config (DB, secret key) is set via environment variables.

## Integration Points
- **Nginx**: Serves static files and proxies to Django app in production.
- **PostgreSQL**: Main DB, managed via Docker Compose.
- **REST API**: All therapist management is via `/api/therapists/` (see router).

## Examples
- To get all active therapists for a store:
  ```python
  Therapist.objects.filter(store=store, is_deleted=False)
  ```
- To soft-delete a therapist via API:
  ```python
  therapist.is_deleted = True
  therapist.save(update_fields=["is_deleted"])
  ```

## Key Files/Directories
- `www/panel/models.py` – Data models
- `www/panel/views.py` – API and web views
- `www/panel/serializers.py` – DRF serializers
- `www/panel/urls.py` – URL routing
- `www/project/settings.py` – Django settings
- `www/requirements.txt` – Python dependencies
- `www/Dockerfile`, `www/docker-compose.yml` – Container setup

---
If any section is unclear or missing, please provide feedback so this guide can be improved for future AI agents.
