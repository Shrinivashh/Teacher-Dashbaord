from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'tHIS IS SHRINIVAS'
    
    

    from .views import views
    from .auth import auth
    from .admin import admin
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/admin')
    
    return app


    
    
