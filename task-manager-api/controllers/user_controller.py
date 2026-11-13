import logging

from flask import jsonify, request

from middlewares.auth import ensure_admin, ensure_owner_or_admin
from models.task import Task
from models.user import User
from services.auth_service import generate_token
from utils.errors import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError, ValidationError
from utils.validators import (
    exigir_json,
    validate_email,
    validate_new_user_payload,
    validate_password,
    validate_role,
)

logger = logging.getLogger(__name__)


def _get_user_or_404(user_id):
    user = User.find(user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')
    return user


def list_users():
    counts = User.task_counts()
    result = []
    for user in User.list_all():
        data = user.to_dict()
        data['task_count'] = counts.get(user.id, 0)
        result.append(data)
    return jsonify(result), 200


def get_user(user_id):
    user = _get_user_or_404(user_id)
    data = user.to_dict()
    data['tasks'] = [task.to_dict() for task in Task.list_for_user(user_id)]
    return jsonify(data), 200


def create_user():
    name, email, password, role = validate_new_user_payload(request.get_json(silent=True))
    if role != 'user':
        ensure_admin()
    if User.find_by_email(email):
        raise ConflictError('Email já cadastrado')

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    user.save()
    logger.info('Usuário criado: %s', user.id)
    return jsonify(user.to_dict()), 201


def update_user(user_id):
    ensure_owner_or_admin(user_id)
    user = _get_user_or_404(user_id)
    data = exigir_json(request.get_json(silent=True))

    if 'role' in data or 'active' in data:
        ensure_admin()

    if 'name' in data:
        if not isinstance(data['name'], str) or not data['name']:
            raise ValidationError('Nome inválido')
        user.name = data['name']
    if 'email' in data:
        validate_email(data['email'])
        existing = User.find_by_email(data['email'])
        if existing and existing.id != user_id:
            raise ConflictError('Email já cadastrado')
        user.email = data['email']
    if 'password' in data:
        user.set_password(validate_password(data['password']))
    if 'role' in data:
        user.role = validate_role(data['role'])
    if 'active' in data:
        if not isinstance(data['active'], bool):
            raise ValidationError('Active deve ser booleano')
        user.active = data['active']

    user.save()
    return jsonify(user.to_dict()), 200


def delete_user(user_id):
    _get_user_or_404(user_id).delete_with_tasks()
    logger.info('Usuário deletado: %s', user_id)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def list_user_tasks(user_id):
    _get_user_or_404(user_id)
    return jsonify([task.to_summary_dict() for task in Task.list_for_user(user_id)]), 200


def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        raise ValidationError('Dados inválidos')

    email, password = data.get('email'), data.get('password')
    if not email or not password:
        raise ValidationError('Email e senha são obrigatórios')

    user = User.find_by_email(email) if isinstance(email, str) else None
    if not user or not isinstance(password, str) or not user.check_password(password):
        raise UnauthorizedError('Credenciais inválidas')
    if not user.active:
        raise ForbiddenError('Usuário inativo')

    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': generate_token(user),
    }), 200
