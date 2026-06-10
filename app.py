from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Bu sayfayı görmek için giriş yapmalısınız.'
login_manager.login_message_category = 'warning'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from routes.transactions import transactions_bp
    app.register_blueprint(transactions_bp)

    from routes.reports import reports_bp
    app.register_blueprint(reports_bp)

    from routes.users import users_bp
    app.register_blueprint(users_bp)

    from routes.backup import backup_bp
    app.register_blueprint(backup_bp)

    from routes.categories import categories_bp
    app.register_blueprint(categories_bp)

    from routes.financiers import financiers_bp
    app.register_blueprint(financiers_bp)

    from routes.payment_methods import payment_methods_bp
    app.register_blueprint(payment_methods_bp)

    # Context processors
    @app.context_processor
    def inject_user_permissions():
        from flask_login import current_user
        if current_user.is_authenticated:
            return {'user_permissions': current_user.get_permissions()}
        return {'user_permissions': {}}

    return app
