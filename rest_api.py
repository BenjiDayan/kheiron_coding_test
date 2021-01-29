# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 16:51:48 2021

@author: benja
"""

from flask import Flask, json
from flask import request, jsonify

from compute import compute_expression_v2

api = Flask(__name__)


@api.route('/compute', methods=['GET'])
def compute_request():
    if 'expression' in request.args:
        expr = str(request.args['expression'])
        print(expr)
        return str(compute_expression_v2(expr))
    else:
        return "Error: No 'expression' field present."


if __name__ == '__main__':
    api.run()
    
"""
Query with python requests module. e.g.
>>> requests.get('http://127.0.0.1:5000/compute', params={'expression': "( ( ( 1 + 1 ) / 10 ) - ( 1 * 2 ) )"}).text
'-1.8'
"""