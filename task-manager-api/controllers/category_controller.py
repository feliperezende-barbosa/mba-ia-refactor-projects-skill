from flask import jsonify, request

from middlewares.auth import ensure_admin
from models.category import Category
from utils.errors import NotFoundError
from utils.validators import validate_category_payload


def _get_category_or_404(category_id):
    category = Category.find(category_id)
    if not category:
        raise NotFoundError('Categoria não encontrada')
    return category


def list_categories():
    counts = Category.task_counts()
    result = []
    for category in Category.list_all():
        data = category.to_dict()
        data['task_count'] = counts.get(category.id, 0)
        result.append(data)
    return jsonify(result), 200


def create_category():
    fields = validate_category_payload(request.get_json(silent=True))
    return jsonify(Category(**fields).save().to_dict()), 201


def update_category(cat_id):
    category = _get_category_or_404(cat_id)
    fields = validate_category_payload(request.get_json(silent=True), partial=True)
    for key, value in fields.items():
        setattr(category, key, value)
    return jsonify(category.save().to_dict()), 200


def delete_category(cat_id):
    ensure_admin()
    _get_category_or_404(cat_id).delete_detaching_tasks()
    return jsonify({'message': 'Categoria deletada'}), 200
