from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from database import PersistenceMixin, db
from utils.helpers import utcnow


class User(PersistenceMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        # o hash da senha nunca é serializado
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    def set_password(self, pwd):
        # pbkdf2 funciona em qualquer build do Python (scrypt depende do OpenSSL)
        self.password = generate_password_hash(pwd, method='pbkdf2:sha256')

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

    def is_admin(self):
        return self.role == 'admin'

    @staticmethod
    def find(user_id):
        return db.session.get(User, user_id)

    @staticmethod
    def find_by_email(email):
        return db.session.scalars(db.select(User).where(User.email == email)).first()

    @staticmethod
    def list_all():
        return db.session.scalars(db.select(User).order_by(User.id)).all()

    @staticmethod
    def task_counts():
        from models.task import Task
        rows = db.session.execute(
            db.select(Task.user_id, func.count(Task.id)).where(Task.user_id.isnot(None)).group_by(Task.user_id)
        ).all()
        return dict(rows)

    def delete_with_tasks(self):
        from models.task import Task
        db.session.execute(db.delete(Task).where(Task.user_id == self.id))
        db.session.delete(self)
        db.session.commit()
