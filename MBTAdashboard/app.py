import json
from flask import Flask, request, render_template, jsonify

import sys, os
sys.path.append('./')  # allow access to MBTAriderSegmentation
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # allow reading files from within MBTAriderSegmentation

from MBTAriderSegmentation.config import *  # setting global file params

import src.utils as utils

app = Flask(__name__)

@app.route('/request_view', methods=['GET', 'POST'])
@app.route('/dashboard', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/report')
def test_page():
    return render_template('Generative_report.html')

@app.route('/initialize_data')
def initialize_view():
    '''Initialize page with default values'''
    backend_data = utils.get_backend_data()
    frontend_data = utils.get_frontend_data(backend_data)
    return jsonify(frontend_data)

@app.route('/reload_data', methods=['GET', 'POST'])
def reload_data():
    '''Update page with user selection'''
    if request.method == 'POST':
        req_view = request.args.get('view')
        req_start_month = request.args.get('start_month')
        req_duration = request.args.get('duration')
        req_time_weight = request.args.get('time_weight')
        req_algorithm = request.args.get('algorithm')

        req_backend_data = utils.get_backend_data(view=req_view,
                                                  start_month=req_start_month,
                                                  duration=req_duration,
                                                  time_weight=req_time_weight,
                                                  algorithm=req_algorithm)

        req_frontend_data = utils.get_frontend_data(req_backend_data)
    return jsonify(req_frontend_data)


@app.route('/load_MBTA_geoJSON')
def load_MBTA_geoJSON():
    '''Return the geoJson data of MBTA lines'''
    filename = DATA_PATH + INPUT_PATH + 'geojson/MBTA-lines.json'
    if filename:
        with open(filename, 'r') as f:
            mbta_geojson = json.load(f)
    return jsonify(mbta_geojson)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
