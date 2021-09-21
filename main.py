from datetime import timedelta

from flask import Flask, g
from flask_redis import FlaskRedis
from flask_login import LoginManager
from flask_session import Session
import redis


from url_handlers.login import User

from url_handlers.reads_per_position import reads_per_position
from url_handlers.periodicity import periodicity
from url_handlers.periodicity_heatmap import periodicity_heatmap
from url_handlers.login import login_page
from url_handlers.projects import projects_page
from url_handlers.project_info import project_page
from url_handlers.ma_plot import ma_plot
from url_handlers.heatmap import heatmap
from url_handlers.ribo_diff import ribo_diff
from url_handlers.alignments import alignments
from url_handlers.liquid_nitrogen import liquid_nitrogen
from url_handlers.user_details import user_details
from url_handlers.volcano_plot import volcano_plot
from url_handlers.psite_plot import psite_plot
from url_handlers.psite_dotplot import psite_dotplot
from url_handlers.ucsc_links import ucsc_links

app = Flask(__name__)

app.register_blueprint(reads_per_position)
app.register_blueprint(periodicity)
app.register_blueprint(periodicity_heatmap)
app.register_blueprint(login_page)
app.register_blueprint(projects_page)
app.register_blueprint(project_page)
app.register_blueprint(ma_plot)
app.register_blueprint(heatmap)
app.register_blueprint(ribo_diff)
app.register_blueprint(alignments)
app.register_blueprint(liquid_nitrogen)
app.register_blueprint(user_details)
app.register_blueprint(volcano_plot)
app.register_blueprint(psite_plot)
app.register_blueprint(psite_dotplot)
app.register_blueprint(ucsc_links)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(weeks=26)

app.config['APP_ADMINS'] = ['e.stepanova@dkfz-heidelberg.de']
app.config['LIQUID_NITROGEN_ADMINS'] = ['c.amayaramirez@dkfz-heidelberg.de']

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
#    redis_store = FlaskRedis(health_check_interval=30)
#    redis_store.init_app(app)
    ip = "172.22.54.5" # hz
    # ip = 'localhost' # localhost
    redis_store = redis.StrictRedis(host="172.22.25.100", health_check_interval=30)
    #redis_store = redis.StrictRedis(host=ip, health_check_interval=30)

    return redis_store


def get_db():
    """ opens a new database connection if there is none yet for the
        current application context
    """
    if not hasattr(g, 'redis_db'):
        g.redis_db = connect_db()
    return g.redis_db


if __name__ == '__main__':
    app.run(debug=True, port=int("80"))
