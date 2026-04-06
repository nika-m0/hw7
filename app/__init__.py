from flask import Flask 
from .config import Config 
from .models import db

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)


    with app.app_context():
        db.create_all()

        from .models import User 
        if User.query.count() == 0:
            test_users = [
                User(name='Иван Петров', email='ivan@example.com'),
                User(name='Мария Сидорова', email='maria@example.com'),
                User(name='Алексей Иванов', email='alexey@example.com')
            ]
            db.session.add_all(test_users)
            db.session.commit()


    from . import routes 
    app.register_blueprint(routes.bp)

    return app