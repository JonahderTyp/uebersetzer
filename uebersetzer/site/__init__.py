import logging
import os
import traceback

from dotenv import load_dotenv
from flask import (Blueprint, current_app, flash, g, make_response, redirect,
                   render_template, request, send_from_directory, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from ..database.db import Message

site = Blueprint("site", __name__, template_folder="templates")


@site.route("/")
def index():
    return render_template("index.html")


@site.get("/chatroom")
def chatroom():
    return render_template("chatroom.html")
