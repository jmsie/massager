# AI Coding Assistant Instructions
Don't fix lint
Don't fix lint
Don't fix lint

## 🏗️ Project Overview
This is a **Django-based massage therapy management system** with a REST API backend and server-rendered frontend. The system manages massage shops, therapists, service plans, reservations, and customer reviews.

## 📋 Core Requirements

### Frontend Development Principles
- **盡可能利用框架，少寫原生 CSS** (Use frameworks as much as possible, minimize native CSS)
- Prefer Django templates with server-side rendering
- Use existing CSS framework patterns from `/static/css/styles.css`
- Leverage Django's built-in form handling and CSRF protection

## 🎯 Architecture Overview

### Tech Stack
- **Backend**: Django 3.2+ with Django REST Framework
- **Database**: PostgreSQL 
- **Frontend**: Server-rendered Django templates with vanilla JavaScript
- **Deployment**: Docker + Nginx + Gunicorn
- **Authentication**: Django's built-in auth with session-based authentication

### Directory Structure
```
www/
├── panel/                    # Main Django app
│   ├── models.py            # Data models
│   ├── serializers.py       # DRF serializers
│   ├── viewsets/           # API ViewSets (organized by feature)
│   ├── views/              # Web views (organized by concern)
│   ├── templates/panel/    # Django templates
│   └── urls.py             # URL routing
├── project/                # Django project settings
├── static/                 # Static assets (CSS, JS)
├── staticfiles/           # Collected static files (auto-generated)
└── docker-compose.yml     # Container orchestration
```

## 🔑 Key Design Patterns

### 1. Multi-Tenant Architecture
Every model is scoped to a `Store` through foreign keys. The system uses session-based store context:

```python
# Pattern: Always filter by current user's store
store = getattr(self.request.user, "store", None)
queryset = Model.objects.filter(store=store)
```

### 2. Soft Delete Pattern
Models use `is_deleted` flag instead of hard deletion:

```python
# ViewSet Mixin Pattern
class SoftDeleteViewSetMixin:
    def destroy(self, request, *args, **kwargs):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])
```

### 3. ViewSet Organization
API endpoints are organized into dedicated ViewSet files:
- `viewsets/therapist.py` - Therapist management
- `viewsets/service_survey.py` - Customer reviews
- `viewsets/massage_plan.py` - Service plans
- `viewsets/reservation.py` - Booking management
- `viewsets/massage_invitation.py` - Public invitation links

### 4. Public vs Private APIs
- **Private APIs**: Require authentication, filter by store
- **Public APIs**: Use `@csrf_exempt` for customer-facing endpoints
- **Mixed APIs**: Different permissions per action (e.g., ServiceSurveyViewSet)

## 💡 Critical Business Rules

### Store Isolation
- **NEVER** allow cross-store data access
- All queries must be filtered by the authenticated user's store
- Store assignment happens at object creation and is immutable

### Public Features
1. **Customer Reviews**: `/review/<therapist_id>/` - Public page for rating therapists
2. **Massage Invitations**: `/invitation/<uuid>/` - Public booking links with UUID slugs

### Data Validation Patterns
```python
# Serializer validation pattern
def validate_therapist(self, value):
    """Ensure therapist belongs to current store"""
    store = getattr(self.request.user, "store", None)
    if store and value.store != store:
        raise serializers.ValidationError("師傅不屬於您的店家")
    return value
```

## 🔧 Development Guidelines

### API Development
1. **Use DRF ViewSets** for CRUD operations
2. **Implement proper serializers** with validation
3. **Return meaningful error messages** in Chinese for user-facing errors
4. **Use mixins** for common functionality (SoftDeleteViewSetMixin, StoreFilteredViewSetMixin)

### Frontend Development
1. **Use Django templates** - avoid SPA complexity
2. **Leverage existing CSS classes** from the design system
3. **Include CSRF tokens** in all forms: `{% csrf_token %}`
4. **Use Django's URL reversing**: `{% url 'view_name' %}`

### Database Queries
1. **Use select_related/prefetch_related** to avoid N+1 queries
2. **Filter at database level**, not in Python
3. **Use appropriate indexes** for frequently queried fields

## 🚀 Common Tasks

### Adding a New Feature
1. Create model in `panel/models.py`
2. Create serializer in `panel/serializers.py`
3. Create ViewSet in `panel/viewsets/feature_name.py`
4. Register in `panel/urls.py` router
5. Create templates in `panel/templates/panel/`
6. Add navigation link in `base.html`

### Creating a Public Endpoint
```python
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["POST"])
def public_endpoint(request):
    # Handle public submission
```

### Adding Store-Scoped Model
```python
class NewModel(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    # Always include store reference
    
    class Meta:
        # Ensure unique constraints include store
        unique_together = ['store', 'name']
```

## 🔒 Security Considerations

1. **Always validate store ownership** in ViewSets
2. **Use Django's CSRF protection** except for public APIs
3. **Sanitize user input** in serializers
4. **Check permissions** at view level, not just URL level
5. **Use UUID slugs** for public shareable links

## 📝 Testing Approach

### API Testing
```python
# Test store isolation
def test_cannot_access_other_store_data(self):
    other_store_therapist = Therapist.objects.create(store=other_store)
    response = self.client.get(f'/api/therapists/{other_store_therapist.id}/')
    self.assertEqual(response.status_code, 404)
```

### View Testing
- Test authentication requirements
- Test store context preservation
- Test form validation
- Test CSRF protection

## 🐳 Docker Development

### Local Development
```bash
docker-compose up       # Start all services
docker-compose exec web python manage.py migrate  # Run migrations
docker-compose exec web python manage.py createsuperuser  # Create admin
```

### Production Deployment
```bash
docker-compose -f docker-compose.prod.yaml up -d
```

## 📚 Key Models Reference

### Store
- Central tenant model
- One-to-one with Django User
- All other models reference this

### Therapist
- Belongs to Store
- Has soft delete (`is_deleted`)
- Can be enabled/disabled

### MassagePlan
- Service offerings per store
- Price and duration
- Cannot change store after creation

### Reservation
- Links Customer, Therapist, MassagePlan
- Time-based scheduling
- Status tracking

### ServiceSurvey
- Public customer reviews
- 1-5 star rating system
- Anonymous submissions allowed

### MassageInvitation
- UUID-based public links
- Time-limited validity
- Converts to Reservation when accepted

## ⚠️ Common Pitfalls to Avoid

1. **Don't forget store filtering** - Always scope queries to current store
2. **Don't expose internal IDs** - Use UUIDs for public URLs
3. **Don't trust client data** - Validate everything in serializers
4. **Don't hard-code Chinese text** - Consider i18n for the future
5. **Don't skip CSRF tokens** - Only exempt truly public endpoints
6. **Don't modify store assignment** - Store is immutable after creation

## 🔄 Workflow Patterns

### Customer Review Flow
1. Shop generates review link: `/review/<therapist_id>/`
2. Customer accesses public page (no auth required)
3. Customer submits rating via AJAX
4. System stores review linked to therapist

### Invitation Booking Flow
1. Shop creates MassageInvitation with UUID
2. Shares link: `/invitation/<uuid>/`
3. Customer views available slots
4. Customer confirms booking
5. System creates Reservation

## 🎨 UI/UX Patterns

### Navigation Structure
- Collapsible sidebar sections
- Section headers with toggle indicators
- Responsive mobile menu
- Active state highlighting

### Form Patterns
- Server-side validation with error display
- CSRF token inclusion
- Progressive enhancement
- Chinese language labels and messages

### CSS Framework Usage
- Utility classes for spacing and layout
- Component classes for cards and navigation
- Responsive grid system
- Dark/light theme variables

## 📦 Dependencies

### Python Packages
- Django>=3.2,<4.0
- djangorestframework>=3.14.0
- psycopg2-binary>=2.9.1
- gunicorn>=20.1.0
- django-cors-headers>=3.13.0

### JavaScript Libraries
- No frontend framework (vanilla JS)
- Django template engine for rendering
- Native fetch API for AJAX

## 🔍 Debugging Tips

1. **Check store context**: `request.session.get('store_name')`
2. **Verify authentication**: `request.user.is_authenticated`
3. **Inspect SQL queries**: Use Django Debug Toolbar in development
4. **Check Docker logs**: `docker-compose logs -f web`
5. **Validate serializer errors**: Check `serializer.errors` for details

---

## Quick Reference Commands

```bash
# Create new migration
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic

# Run tests
docker-compose exec web python manage.py test

# Access Django shell
docker-compose exec web python manage.py shell

# View logs
docker-compose logs -f web
```

---

**Remember**: When in doubt, check existing patterns in the codebase. The system is designed for consistency and maintainability over clever optimizations.
