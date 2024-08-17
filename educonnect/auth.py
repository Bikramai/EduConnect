from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import logout_user, login_user, current_user

from educonnect import db
from educonnect.models import User

auth = Blueprint('auth', __name__)


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        fullname = request.form.get("fullname")
        username = request.form.get("username")
        password = request.form.get("password")
        is_teacher = request.form.get("is_teacher")

        exists = User.query.filter_by(username=username).first()
        if exists:
            flash("Username already exists!", "danger")
            return redirect(url_for("auth.signup"))

        user = User(full_name=fullname, username=username, password=password)
        if is_teacher:
            user.is_teacher = True
        db.session.add(user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for("auth.signin"))

    return render_template("signup.html")


@auth.route("/", methods=["GET", "POST"])
@auth.route("/signin", methods=["GET", "POST"])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                login_user(user)
                if current_user.is_teacher:
                    return redirect(url_for("teacher.index"))
                return redirect(url_for("main.index"))
            else:
                flash("Incorrect password!", "danger")
                return redirect(url_for("auth.signin"))
        else:
            flash("User doesn't exist!", "danger")
            return redirect(url_for("auth.signin"))

    return render_template("signin.html")


@auth.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out!", "warning")
    return redirect(url_for("auth.signin"))
