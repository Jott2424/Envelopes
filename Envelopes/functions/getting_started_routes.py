from config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT
from functions import db_utils

from flask import render_template, redirect, url_for
from flask_login import current_user

def getting_started_home():
    return render_template('getting_started_home.html')

def getting_started_create_budget_route():
    return render_template('getting_started_create_budget.html')