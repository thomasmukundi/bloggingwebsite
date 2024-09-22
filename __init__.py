from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import inspect
import os

db = SQLAlchemy()
DB_NAME = 'thebloggers'


def  create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = "fdshdgsfjdgjdshgsgh"
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://root:tho380#M@localhost/{DB_NAME}"


    db.init_app(app)
    from models import User, Blog, BlogMeta, Comment

    create_database(app)


    from routes import routes
    from authentication import auth
    #from views import views


    app.register_blueprint(routes, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')



    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return  User.query.get(int(id))

    return app




def create_database(app):
    from models import User, Blog, BlogMeta, Comment
    # Assuming DB_NAME is a global variable or otherwise accessible
    if DB_NAME is None:
        raise ValueError('Database name not set')
    else:
        models = [Comment, BlogMeta, Blog, User]
        with app.app_context():
            inspector = inspect(db.engine)
            for model in models:
                if not inspector.has_table(model.__tablename__):
                    # Table doesn't exist, create it
                    model.__table__.create(db.engine)
                #else:
                    #print(f"Table '{model.__tablename__}' already exists.")

app = create_app()