import logging

from flask import Flask
from flask_cors import CORS

import models  # noqa: F401  (registra os models no metadata antes do create_all)
from config.settings import Settings
from database import db
from middlewares.error_handler import register_error_handlers
from routes import ALL_BLUEPRINTS
from services.notification_service import NotificationService


def create_app():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

    app = Flask(__name__)
    app.config.from_object(Settings)
    CORS(app)
    db.init_app(app)
    app.extensions['notification_service'] = NotificationService.from_config(app.config)

    for blueprint in ALL_BLUEPRINTS:
        app.register_blueprint(blueprint)
    register_error_handlers(app)

    with app.app_context():
        db.create_all()
    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=Settings.DEBUG, host=Settings.HOST, port=Settings.PORT)
