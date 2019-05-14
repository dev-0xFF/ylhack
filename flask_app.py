from flask import Flask, url_for, request, render_template, redirect, flash
import json
from database import *
from werkzeug.security import generate_password_hash, check_password_hash
import time


@app.route('/')
@app.route('/index')
def main():
    return render_template('base.html', fixed_footer=True)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    session.pop('admin', 0)
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html', title=': Вход', fixed_footer=True)
    elif request.method == "POST":
        login = request.form["login"]
        password = request.form["u_password"]
        correct = User.query.filter(User.login == login).first()
        if not correct:
            error = ''
        if not (login and password):
            error = "Одно из полей не заполнено"
        elif not check_password_hash(correct.password, password):
            error = "Логин или пароль введены неверно"
        else:
            session['username'] = correct.login
            session['user_id'] = correct.id
            session['admin'] = correct.admin
            return redirect('/')
        return  render_template('login.html', title=': Вход', fixed_footer=True, error=error)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == "GET":
        return render_template('registration.html', title=': Регистрация', fixed_footer=True)
    elif request.method == "POST":
        login = request.form["login"]
        password = request.form["u_password"]
        password_conf = request.form["u_password_once_again"]
        email = request.form["email"]
        if not (login and password):
            error = "Одно из полей не заполнено"
        if password != password_conf:
            error = 'Пароли не совпадают'
        elif User.query.filter(User.login == login).first():
            error = "Пользователь с таким именем уже зарегистрирован в системе. Исправьте данные"
        else:
            if not request.form["email"]:
                email = ''
            password = generate_password_hash(password)
            user = User(password=password, login=login, email=email, admin=0)
            db.session.add(user)
            db.session.commit()
            correct = User.query.filter(User.login == login).first()
            session['username'] = correct.login
            session['user_id'] = correct.id
            session['admin'] = correct.admin
            return redirect('/')
        return render_template('registration.html', title=': Регистрация', fixed_footer=True, error=error)


@app.errorhandler(404)
def not_found(error):
    return render_template("error_404.html", title=": Страница не найдена", fixed_footer=True)


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)