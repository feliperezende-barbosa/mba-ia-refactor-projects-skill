from collections import Counter
from datetime import timedelta

from flask import jsonify

from config.settings import HIGH_PRIORITY_MAX, PRIORITY_LABELS, RECENT_DAYS
from models.category import Category
from models.task import Task
from models.user import User
from utils.errors import NotFoundError
from utils.helpers import utcnow


def _percentage(part, total):
    return round((part / total) * 100, 2) if total > 0 else 0


def summary_report():
    now = utcnow()
    by_status = Task.count_by(Task.status)
    by_priority = Task.count_by(Task.priority)
    since = now - timedelta(days=RECENT_DAYS)
    overdue_tasks = Task.list_overdue()
    totals_by_user = Task.totals_by_user()

    user_stats = []
    for user in User.list_all():
        total, completed = totals_by_user.get(user.id, (0, 0))
        user_stats.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': _percentage(completed, total),
        })

    return jsonify({
        'generated_at': str(now),
        'overview': {
            'total_tasks': Task.count_total(),
            'total_users': len(user_stats),
            'total_categories': len(Category.list_all()),
        },
        'tasks_by_status': {
            status: by_status.get(status, 0) for status in ('pending', 'in_progress', 'done', 'cancelled')
        },
        'tasks_by_priority': {label: by_priority.get(level, 0) for level, label in PRIORITY_LABELS.items()},
        'overdue': {
            'count': len(overdue_tasks),
            'tasks': [
                {
                    'id': task.id,
                    'title': task.title,
                    'due_date': str(task.due_date),
                    'days_overdue': (now - task.due_date).days,
                }
                for task in overdue_tasks
            ],
        },
        'recent_activity': {
            'tasks_created_last_7_days': Task.count_created_since(since),
            'tasks_completed_last_7_days': Task.count_done_since(since),
        },
        'user_productivity': user_stats,
    }), 200


def user_report(user_id):
    user = User.find(user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')

    tasks = Task.list_for_user(user_id)
    by_status = Counter(task.status for task in tasks)
    total, done = len(tasks), by_status['done']

    return jsonify({
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': by_status['pending'],
            'in_progress': by_status['in_progress'],
            'cancelled': by_status['cancelled'],
            'overdue': sum(1 for task in tasks if task.is_overdue()),
            'high_priority': sum(1 for task in tasks if task.priority <= HIGH_PRIORITY_MAX),
            'completion_rate': _percentage(done, total),
        },
    }), 200
