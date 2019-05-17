from flask import Flask, g
from flask_redis import FlaskRedis

from url_handlers.reads_per_position import reads_per_position
from url_handlers.periodicity import periodicity
from url_handlers.periodicity_heatmap import periodicity_heatmap

app = Flask(__name__)

app.register_blueprint(reads_per_position)
app.register_blueprint(periodicity)
app.register_blueprint(periodicity_heatmap)


# Database stuff
def connect_db():
    """ connects to our redis database """
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