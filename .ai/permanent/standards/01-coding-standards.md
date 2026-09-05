# Coding Standards — AlamiaTravelOS

## General Guidelines
- **Language**: Python 3.11+ for Odoo addons; YAML for Docker/Docker-Compose configs
- **Code Style**: Follow Odoo community conventions (PEP8 adapted for Odoo)
- **Naming**: `snake_case` for Python functions/variables; `UPPER_SNAKE_CASE` for env vars and constants
- **File Headers**: All Python files must have module-level docstring describing purpose

## Odoo Addon Conventions

### Model Files (`models/*.py`)
```python
# Good: descriptive class name, proper _name convention
class TravelSale(models.Model):
    _name = 'alamia_travel_sales.sale'
    _description = 'Alamia Travel Sale Order'

    # Fields grouped by logical section
    name = fields.Char(string='Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    # ... etc
```

### View Files (`views/*.xml`)
- IDs should follow module convention: `module_name_object_action`
- QWeb templates: use `t-attribution`, `t-group`, `t-row` classes consistently
- Always include `menu_id` reference for tree/list views

### Manifest (`__manifest__.py`)
- `name`: Human-readable module title
- `version`: Semantic version (e.g., `1.0.0.0.1` per Odoo 19 convention)
- `depends`: List only direct dependencies
- `data`: XML files for demo/data; keep CSV minimal
- `qweb`: QWeb templates to load
- `installable`: `True` by default

### Python Linting
- `flake8` or `odoo-qweb-lint` pre-commit recommended
- No `except:` without `as e` (must capture exception)
- All methods must have docstrings if they expose RPC or are public
- Maximum 80 characters per line for readability (IDE column guide)

## YAML / Docker Conventions
- `docker-compose.yml` and `docker-compose.prod.yml` must use consistent env var pattern: `${VAR:-default}`
- Named volumes defined at bottom of file (per current standard)
- No tabs — 2-space indentation only
- Comments only at top of file or above significant blocks (no inline `#` for logic)
- Environment variables with secrets must NOT have default values in compose (use `.env` or Portainer UI)

## Markdown Documentation
- All `.md` files must start with H1 header matching filename (except README.md)
- Tables must have header row with `|` delimiters
- All links must be relative where possible (avoid absolute paths in commits)
- Code blocks require language specifier (e.g., ```yaml, ```python)

## Commit Messages
- Format: `<type>: <description>`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Scope optional: e.g., `feat: add task-2 data-import guide`
- Body should explain WHAT and WHY, not HOW (code shows how)