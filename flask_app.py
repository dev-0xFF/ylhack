from database import *
from flask import abort
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# Main page


@app.route('/')
@app.route('/index')
def main():
    return render_template('base.html', fixed_footer=True)

# User logout


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    session.pop('admin', 0)
    return redirect('/')

# User login


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect('/')
    if request.method == "GET":
        return render_template('login.html', title=': Вход', fixed_footer=True)
    elif request.method == "POST":
        login = request.form["login"]
        password = request.form["u_password"]
        correct = User.query.filter(User.login == login).first()
        if correct is None:
            correct1 = User.query.filter(User.email == login).first()
            if not correct1 is None:
                correct = correct1
        if correct is None:
            error = 'Такого пользователя нет в системе'
        elif not (login and password):
            error = "Одно из полей не заполнено"
        elif not check_password_hash(correct.password, password):
            error = "Неправильный пароль"
        else:
            session['username'] = correct.login
            session['user_id'] = correct.id
            session['admin'] = correct.admin
            return redirect('/')
        return render_template('login.html', title=': Вход', fixed_footer=True, error=error)

# User registration


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
        elif password != password_conf:
            error = 'Пароли не совпадают'
        elif User.query.filter(User.login == login).first():
            error = "Пользователь с таким именем уже зарегистрирован в системе. Исправьте данные"
        elif User.query.filter(User.email == email).first():
            error = "Пользователь с таким e-mail уже зарегистрирован в системе. Исправьте данные"
        else:
            if not request.form["email"]:
                email = ''
            password = generate_password_hash(password)
            user = User(password=password, login=login, email=email, admin=0)
            db.session.add(user)
            db.session.commit()
            return render_template('registration_success.html')
        return render_template('registration.html', title=': Регистрация', fixed_footer=True, error=error)


@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    if 'user_id' not in session:
        return redirect('/')
    if request.method == "GET":
        problem = Problem(name='Новая задача', statement='', time_end=(datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d/%m/%Y %H:%M:%S"), author_id=session['user_id'], completion_stage=0)
        session['problem_id'] = problem.id
        return render_template('edit_task.html', title='Добавление задачи', problem=problem)
    elif request.method == "POST":
        name = request.form["name"]
        end_time = request.form["time_end"]
        description = request.form["description"]
        completion = request.form["completion_stage"]
        user = Problem(name=name, statement=description, time_end=end_time, author_id=session['user_id'], completion_stage=completion)
        User.query.filter(User.id == session['problem_id']).delete()
        db.session.add(user)
        session['problem_id'] = user.id
        db.session.commit()
        return redirect(f'/edit-task/{user.id}')


@app.route('/edit-task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'user_id' not in session:
        return abort(404)
    if request.method == "GET":
        problem = Problem.query.filter(Problem.id == task_id).first()
        if problem is None:
            return 'Not found :('
        session['problem_id'] = problem.id
        return render_template('edit_task.html', title='Добавление задачи', problem=problem)
    elif request.method == "POST":
        name = request.form["name"]
        end_time = request.form["time_end"]
        description = request.form["description"]
        completion = request.form["completion_stage"]
        user = Problem(name=name, statement=description, time_end=end_time, author_id=session['user_id'], completion_stage=completion)
        User.query.filter(User.id == session['problem_id']).delete()
        db.session.add(user)
        session['problem_id'] = user.id
        db.session.commit()
        return render_template('edit_task.html', problem=user)


@app.errorhandler(404)
def not_found(error):
    return render_template("error_404.html", title=": Страница не найдена", fixed_footer=True)


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)
