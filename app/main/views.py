from flask import render_template, request, redirect, url_for,abort
from . import main
from .. import db,photos
from flask_login import login_required,current_user
from ..request import get_quote
from app.models import User

@main.route('/')
def index():

    name  = "Quote"
    quote = get_quote()
    
    return render_template('index.html',name = name,quote = quote)

@main.route('/user/<uname>')
@login_required
def profile(uname):
    user = User.query.filter_by(username = uname).first()

    if user is None:
        abort(404)

    return render_template("profile/profile.html", user = user)