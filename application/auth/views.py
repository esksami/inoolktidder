import bcrypt
from contextlib import suppress

from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from application import app, db
from application.utils import session_scope

from application.auth.models import User
from application.auth.forms import LoginForm, SignUpForm, UsernameForm, PasswordForm

from application.posts.models import PostLike

from application.roles.models import Role, UserRole


@app.route('/profile', methods = ['GET'])
@login_required
def user_profile():
    user = User.query.filter(User.id == current_user.id).first()

    usernameForm = UsernameForm()
    passwordForm = PasswordForm()

    with suppress(KeyError):
        usernameForm = request.args['usernameForm']

    with suppress(KeyError):
        passwordForm = request.args['passwordForm']

    return render_template(
        'auth/profile.html',
        user=user,
        usernameForm=UsernameForm(),
        passwordForm=PasswordForm(),
    )

@app.route('/profile/edit_username', methods = ['GET', 'POST'])
@login_required
def user_edit_username():
    if request.method == 'GET':
        return redirect(url_for('user_profile'))

    form = UsernameForm(request.form)

    user = User.query.get(current_user.id)

    if not form.validate():
        return render_template(
            'auth/profile.html',
            user=user,
            usernameForm=form,
            passwordForm=PasswordForm(),
        )

    with session_scope() as session:
        username = form.username.data

        existingUser = session.query(User).filter(User.username == username).first()

        if (existingUser):
            form.username.errors.append('Username already exists')
            return render_template(
                'auth/profile.html',
                user=user,
                usernameForm=form,
                passwordForm=PasswordForm(),
            )

        user.username = username

        session.commit()

    return redirect(url_for('user_profile'))

@app.route('/profile/edit_password', methods = ['GET', 'POST'])
@login_required
def user_edit_password():
    if request.method == 'GET':
        return redirect(url_for('user_profile'))

    form = PasswordForm(request.form)

    user = User.query.get(current_user.id)

    if not form.validate():
        return render_template(
            'auth/profile.html',
            user=user,
            usernameForm=UsernameForm(),
            passwordForm=form,
        )

    with session_scope() as session:
        user = session.query(User).get(current_user.id)

        password = form.password.data.encode()
        salt = bcrypt.gensalt(rounds=10)
        phash = bcrypt.hashpw(password, salt)

        user.phash = phash.decode()

        session.commit()

    return redirect(url_for('user_profile'))

@app.route('/profile/delete', methods=['GET', 'POST'])
@login_required
def user_delete():
    if request.method == 'GET':
        return redirect(url_for('user_profile'))

    with session_scope() as session:
        user = User.query.get(current_user.id)

        (session.query(PostLike)
            .filter(PostLike.account_id == current_user.id)
            .delete())
        session.delete(user)

        session.commit()

    logout_user()

    return redirect(url_for('posts_index'))

@app.route('/signup', methods = ['GET', 'POST'])
def auth_signup():
    if request.method == 'GET':
        return render_template('auth/signup.html', form=SignUpForm())

    form = SignUpForm(request.form)

    if not form.validate():
        return render_template('auth/signup.html', form=form)
    
    user = User.query.filter_by(username=form.username.data).first()

    if user:
        return render_template('auth/signup.html', form=form, error='Username is taken')

    password = form.password.data.encode()
    salt = bcrypt.gensalt(rounds=10)
    phash = bcrypt.hashpw(password, salt)

    user = User(
        username=form.username.data,
        phash=phash.decode()
    )

    with session_scope() as session:
        session.add(user)
        session.flush()

        roles = Role.query.filter(Role.name.in_(['APPROVED', 'USER'])).all()
        session.bulk_save_objects(
            [UserRole(role_id=role.id, account_id=user.id) for role in roles]
        )

        session.commit()

    return redirect(url_for('auth_login'))


@app.route('/login', methods = ['GET', 'POST'])
def auth_login():
    if request.method == 'GET':
        return render_template('auth/login.html', form=LoginForm())

    form = LoginForm(request.form)

    if not form.validate():
        return render_template('auth/login.html', form=form)

    user = User.query.filter_by(username=form.username.data).first()

    if not user:
        return render_template(
            'auth/login.html',
            form=form,
            error = 'No such username or password'
        )
    
    password = form.password.data.encode()
    phash = user.phash.encode()

    if not bcrypt.checkpw(password, phash):
        return render_template(
            'auth/login.html',
            form=form,
            error = 'No such username or password'
        )

    login_user(user)

    return redirect(request.args.get('next') or url_for('posts_index'))

@app.route('/logout')
def auth_logout():
    logout_user()
    
    return redirect(url_for('posts_index'))