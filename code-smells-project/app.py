import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Settings
from database.bootstrap import init_db
from database.connection import close_db
from middlewares.error_handler import register_error_handlers
from views.routes import api


def create_app():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    app = Flask(__name__)
    app.config.from_object(Settings)
    CORS(app)

    init_db(app.config["DATABASE_PATH"])
    app.teardown_appcontext(close_db)
    app.register_blueprint(api)
    register_error_handlers(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.logger.info("Servidor iniciado em http://%s:%s", Settings.HOST, Settings.PORT)
    app.run(host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG)
