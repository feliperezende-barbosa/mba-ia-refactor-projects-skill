from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class PersistenceMixin:
    """Persistência compartilhada pelos models: controllers nunca tocam a sessão diretamente."""

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
