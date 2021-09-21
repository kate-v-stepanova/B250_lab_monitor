import pandas as pd
import numpy as np
from flask import Blueprint, render_template, request
from flask_login import login_required
import json

ucsc_links = Blueprint('ucsc_links', __name__)


@ucsc_links.route('/ucsc_links', methods=['GET'])
@login_required
def get_ucsc_links():
    from main import get_db
    rdb = get_db()
    ucsc_links = rdb.smembers('ucsc_links')
    ucsc_links = [link.decode('utf-8') for link in ucsc_links]
    ucsc_links=sorted(ucsc_links)
    return render_template('ucsc_links.html', ucsc_links=ucsc_links)
