from flask import Flask, g
from flask_redis import FlaskRedis
from flask_login import LoginManager
from flask_session import Session

from url_handlers.login import User

from url_handlers.reads_per_position import reads_per_position
from url_handlers.periodicity import periodicity
from url_handlers.periodicity_heatmap import periodicity_heatmap
from url_handlers.login import login_page
from url_handlers.projects import projects_page
from url_handlers.project_info import project_page
from url_handlers.ma_plot import ma_plot
from url_handlers.heatmap import heatmap
from url_handlers.translational_efficiency import translational_efficiency

app = Flask(__name__)

app.register_blueprint(reads_per_position)
app.register_blueprint(periodicity)
app.register_blueprint(periodicity_heatmap)
app.register_blueprint(login_page)
app.register_blueprint(projects_page)
app.register_blueprint(project_page)
app.register_blueprint(ma_plot)
app.register_blueprint(heatmap)
app.register_blueprint(translational_efficiency)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

sess = Session(app)

# login manager
login_manager = LoginManager()
login_manager.login_view = 'login_page.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


# Database stuff
def connect_db():
    """ connects to redis database """
    redis_store = FlaskRedis()
    redis_store.init_app(app)
    return redis_store


def get_db():
    """ opens a new database connection if there is none yet for the
        current application context
    """
    if not hasattr(g, 'redis_db'):
        g.redis_db = connect_db()
    return g.redis_db
