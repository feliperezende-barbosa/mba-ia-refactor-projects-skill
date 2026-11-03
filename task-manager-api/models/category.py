from sqlalchemy import func, update

from config.settings import DEFAULT_COLOR
from database import PersistenceMixin, db
from utils.helpers import utcnow


class Category(PersistenceMixin, db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(7), default=DEFAULT_COLOR)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'created_at': str(self.created_at),
        }

    @staticmethod
    def find(category_id):
        return db.session.get(Category, category_id)

    @staticmethod
    def list_all():
        return db.session.scalars(db.select(Category).order_by(Category.id)).all()

    @staticmethod
    def task_counts():
        from models.task import Task
        rows = db.session.execute(
            db.select(Task.category_id, func.count(Task.id)).where(Task.category_id.isnot(None)).group_by(Task.category_id)
        ).all()
        return dict(rows)

    def delete_detaching_tasks(self):
        """Remove a categoria deixando as tasks sem categoria (evita referências órfãs)."""
        from models.task import Task
        db.session.execute(update(Task).where(Task.category_id == self.id).values(category_id=None))
        db.session.delete(self)
        db.session.commit()
