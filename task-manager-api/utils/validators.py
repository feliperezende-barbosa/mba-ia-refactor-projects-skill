from datetime import datetime

from config.settings import (
    DATE_FORMAT,
    DEFAULT_COLOR,
    DEFAULT_PRIORITY,
    DEFAULT_ROLE,
    DEFAULT_STATUS,
    EMAIL_PATTERN,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    VALID_ROLES,
    VALID_STATUSES,
)
from utils.errors import ValidationError


def exigir_json(data):
    if not isinstance(data, dict) or not data:
        raise ValidationError("Dados inválidos")
    return data


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def parse_due_date(value):
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except (TypeError, ValueError):
        raise ValidationError("Formato de data inválido. Use YYYY-MM-DD")


def _validate_title(title):
    if not isinstance(title, str) or not title:
        raise ValidationError("Título é obrigatório")
    if len(title) < MIN_TITLE_LENGTH:
        raise ValidationError("Título muito curto")
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError("Título muito longo")
    return title


def _validate_status(status):
    if status not in VALID_STATUSES:
        raise ValidationError("Status inválido")
    return status


def _validate_priority(priority):
    if not _is_int(priority) or not MIN_PRIORITY <= priority <= MAX_PRIORITY:
        raise ValidationError("Prioridade deve ser entre 1 e 5")
    return priority


def _normalize_tags(tags):
    if isinstance(tags, list):
        return ",".join(str(tag) for tag in tags)
    if isinstance(tags, str):
        return tags
    raise ValidationError("Tags inválidas")


def validate_task_payload(data, partial=False):
    """Valida o payload de task e devolve somente os campos a aplicar (create e update usam as mesmas regras)."""
    exigir_json(data)
    fields = {}

    if partial:
        if "title" in data:
            fields["title"] = _validate_title(data["title"])
    else:
        fields["title"] = _validate_title(data.get("title"))

    if not partial:
        fields["description"] = data.get("description", "")
        fields["status"] = _validate_status(data.get("status", DEFAULT_STATUS))
        fields["priority"] = _validate_priority(data.get("priority", DEFAULT_PRIORITY))
    else:
        if "description" in data:
            fields["description"] = data["description"]
        if "status" in data:
            fields["status"] = _validate_status(data["status"])
        if "priority" in data:
            fields["priority"] = _validate_priority(data["priority"])

    for key in ("user_id", "category_id"):
        if key in data or not partial:
            value = data.get(key)
            if value and not _is_int(value):
                raise ValidationError(f"{key} inválido")
            fields[key] = value or None

    if "due_date" in data:
        fields["due_date"] = parse_due_date(data["due_date"]) if data["due_date"] else None
    if "tags" in data:
        fields["tags"] = _normalize_tags(data["tags"]) if data["tags"] else None

    return fields


def validate_new_user_payload(data):
    exigir_json(data)
    name, email, password = data.get("name"), data.get("email"), data.get("password")
    role = data.get("role", DEFAULT_ROLE)

    if not name:
        raise ValidationError("Nome é obrigatório")
    if not email:
        raise ValidationError("Email é obrigatório")
    if not password:
        raise ValidationError("Senha é obrigatória")
    if not all(isinstance(v, str) for v in (name, email, password)):
        raise ValidationError("Nome, email e senha devem ser texto")

    validate_email(email)
    validate_password(password, "Senha deve ter no mínimo 4 caracteres")
    validate_role(role)
    return name, email, password, role


def validate_email(email):
    if not isinstance(email, str) or not EMAIL_PATTERN.match(email):
        raise ValidationError("Email inválido")
    return email


def validate_password(password, message="Senha muito curta"):
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(message)
    return password


def validate_role(role):
    if role not in VALID_ROLES:
        raise ValidationError("Role inválido")
    return role


def validate_category_payload(data, partial=False):
    exigir_json(data)
    fields = {}
    if not partial or "name" in data:
        name = data.get("name")
        if not name or not isinstance(name, str):
            raise ValidationError("Nome é obrigatório")
        fields["name"] = name
    if not partial:
        fields["description"] = data.get("description", "")
        fields["color"] = data.get("color", DEFAULT_COLOR)
    else:
        for key in ("description", "color"):
            if key in data:
                fields[key] = data[key]
    color = fields.get("color")
    if color is not None and not (isinstance(color, str) and len(color) == 7 and color.startswith("#")):
        raise ValidationError("Cor inválida. Use o formato #RRGGBB")
    return fields


def parse_optional_int(value, name):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"Parâmetro {name} inválido")
