from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from extensions import db, login_manager
from models import User
from forms import RegisterForm, LoginForm

auth = Blueprint("auth", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already exists", "danger")
            return render_template("register.html", form=form)

        user = User(
            fullname=form.fullname.data,
            username=form.username.data,
            role=form.role.data,
            specialization=form.specialization.data if form.role.data == "doctor" else None
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("auth.register_success"))

    return render_template("register.html", form=form)



@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)

            # ✅ ROLE BASED REDIRECT
            if user.role == "doctor":
                return redirect(url_for("main.doctor_dashboard"))
            else:
                return redirect(url_for("main.dashboard"))

        flash("Invalid username or password", "danger")

    return render_template("login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
@auth.route("/register-success")
def register_success():
    return render_template("register_success.html")
