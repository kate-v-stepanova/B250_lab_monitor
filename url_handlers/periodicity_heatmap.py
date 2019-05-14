import os
import glob

import pandas as pd
from flask import Blueprint, render_template

periodicity_heatmap = Blueprint('periodicity', __name__)

@periodicity_heatmap.route('/periodicity_heatmap/<dataset_id>')
def get_periodicity_heatmap(dataset_id):
