import bcrypt

from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user
  
from application import app, db
from application.auth.models import User
from application.auth.forms import LoginForm, SignUpForm


@app.route('/signup', methods = ['GET', 'POST'])
def auth_signup():
    if request.method == 'GET':
        return render_template('auth/signup.html', form=SignUpForm())

    form = SignUpForm(request.form)

    if not form.validate():
        return render_template('auth/signup.html', form=form)
    

    password = form.password.data.encode()
    salt = bcrypt.gensalt(rounds=16)
    phash = bcrypt.hashpw(password, salt)

    user = User(
        username=form.username.data,
        phash=phash.decode(),
        salt=salt.decode()
    )

    db.session().add(user)
    db.session().commit()

    return redirect(url_for("auth_login"))


@app.route('/login', methods = ['GET', 'POST'])
def auth_login():
    if request.method == 'GET':
        return render_template('auth/login.html', form=LoginForm())

    form = LoginForm(request.form)

    if not form.validate():
        return render_template('auth/login.html', form=form)

    user = User.query.filter_by(username=form.username.data).first()

    if not user:
        return render_template('auth/login.html', form=form,
                                error = 'No such username or password')
    
    password = form.password.data.encode()
    salt = user.salt.encode()
    phash = bcrypt.hashpw(password, salt)

    if phash != user.phash.encode():
        return render_template('auth/login.html', form=form,
                                error = 'No such username or password')

    login_user(user)

    return redirect(url_for('posts_index'))

@app.route('/logout')
def auth_logout():
    logout_user()
    
    return redirect(url_for('posts_index'))