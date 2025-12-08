from functions import db_utils

from flask import render_template, request, redirect, url_for
from flask_login import current_user

def envelopes_home():
    return render_template('envelopes_home.html')

def envelopes_view():
    return render_template('envelopes_view.html')