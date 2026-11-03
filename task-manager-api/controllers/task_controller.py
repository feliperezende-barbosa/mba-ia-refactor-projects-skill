import logging

from flask import current_app, jsonify, request

from models.category import Category
from models.task import Task
from models.user import User
from utils.errors import NotFoundError
from utils.validators import parse_optional_int, validate_task_payload

logger = logging.getLogger(__name__)


def _get_task_or_404(task_id):
    task = Task.find(task_id)
    if not task:
        raise NotFoundError('Task não encontrada')
    return task


def _ensure_references(fields):
    if fields.get('user_id') and not User.find(fields['user_id']):
        raise NotFoundError('Usuário não encontrado')
    if fields.get('category_id') and not Category.find(fields['category_id']):
        raise NotFoundError('Categoria não encontrada')


def list_tasks():
    return jsonify([task.to_listing_dict() for task in Task.list_with_relations()]), 200


def get_task(task_id):
    return jsonify(_get_task_or_404(task_id).to_detail_dict()), 200


def create_task():
    fields = validate_task_payload(request.get_json(silent=True))
    _ensure_references(fields)

    task = Task(**fields).save()
    logger.info('Task criada: %s - %s', task.id, task.title)
    if task.user_id:
        current_app.extensions['notification_service'].notify_task_assigned(User.find(task.user_id), task)
    return jsonify(task.to_dict()), 201


def update_task(task_id):
    task = _get_task_or_404(task_id)
    fields = validate_task_payload(request.get_json(silent=True), partial=True)
    _ensure_references(fields)

    for key, value in fields.items():
        setattr(task, key, value)
    task.save()
    logger.info('Task atualizada: %s', task.id)
    return jsonify(task.to_dict()), 200


def delete_task(task_id):
    _get_task_or_404(task_id).delete()
    logger.info('Task deletada: %s', task_id)
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    tasks = Task.search(
        text=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=parse_optional_int(request.args.get('priority'), 'priority'),
        user_id=parse_optional_int(request.args.get('user_id'), 'user_id'),
    )
    return jsonify([task.to_dict() for task in tasks]), 200


def task_stats():
    by_status = Task.count_by(Task.status)
    total = Task.count_total()
    done = by_status.get('done', 0)
    return jsonify({
        'total': total,
        'pending': by_status.get('pending', 0),
        'in_progress': by_status.get('in_progress', 0),
        'done': done,
        'cancelled': by_status.get('cancelled', 0),
        'overdue': Task.count_overdue(),
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }), 200
