from sqlalchemy import case, func
from sqlalchemy.orm import joinedload

from config.settings import CLOSED_STATUSES, DEFAULT_PRIORITY, DEFAULT_STATUS
from database import PersistenceMixin, db
from utils.helpers import utcnow


class Task(PersistenceMixin, db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=DEFAULT_STATUS)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    # ---- regras de domínio ----
    def is_overdue(self):
        return bool(self.due_date and self.due_date < utcnow() and self.status not in CLOSED_STATUSES)

    # ---- serialização ----
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else [],
        }

    def to_detail_dict(self):
        data = self.to_dict()
        data['overdue'] = self.is_overdue()
        return data

    def to_listing_dict(self):
        data = self.to_detail_dict()
        data['user_name'] = self.user.name if self.user else None
        data['category_name'] = self.category.name if self.category else None
        return data

    def to_summary_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': str(self.created_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'overdue': self.is_overdue(),
        }

    # ---- acesso a dados ----
    @staticmethod
    def find(task_id):
        return db.session.get(Task, task_id)

    @staticmethod
    def list_with_relations():
        query = db.select(Task).options(joinedload(Task.user), joinedload(Task.category)).order_by(Task.id)
        return db.session.scalars(query).unique().all()

    @staticmethod
    def list_for_user(user_id):
        return db.session.scalars(db.select(Task).where(Task.user_id == user_id).order_by(Task.id)).all()

    @staticmethod
    def search(text=None, status=None, priority=None, user_id=None):
        query = db.select(Task)
        if text:
            query = query.where(db.or_(Task.title.like(f'%{text}%'), Task.description.like(f'%{text}%')))
        if status:
            query = query.where(Task.status == status)
        if priority is not None:
            query = query.where(Task.priority == priority)
        if user_id is not None:
            query = query.where(Task.user_id == user_id)
        return db.session.scalars(query.order_by(Task.id)).all()

    @staticmethod
    def _overdue_filter():
        return db.and_(Task.due_date.isnot(None), Task.due_date < utcnow(), Task.status.notin_(CLOSED_STATUSES))

    @staticmethod
    def count_total():
        return db.session.scalar(db.select(func.count(Task.id)))

    @staticmethod
    def count_by(column):
        rows = db.session.execute(db.select(column, func.count(Task.id)).group_by(column)).all()
        return dict(rows)

    @staticmethod
    def count_overdue():
        return db.session.scalar(db.select(func.count(Task.id)).where(Task._overdue_filter()))

    @staticmethod
    def list_overdue():
        return db.session.scalars(db.select(Task).where(Task._overdue_filter()).order_by(Task.id)).all()

    @staticmethod
    def count_created_since(moment):
        return db.session.scalar(db.select(func.count(Task.id)).where(Task.created_at >= moment))

    @staticmethod
    def count_done_since(moment):
        return db.session.scalar(
            db.select(func.count(Task.id)).where(Task.status == 'done', Task.updated_at >= moment)
        )

    @staticmethod
    def totals_by_user():
        """{user_id: (total, concluídas)} em uma única query."""
        done = func.sum(case((Task.status == 'done', 1), else_=0))
        rows = db.session.execute(
            db.select(Task.user_id, func.count(Task.id), done).where(Task.user_id.isnot(None)).group_by(Task.user_id)
        ).all()
        return {user_id: (total, int(completed or 0)) for user_id, total, completed in rows}
