from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from models import (User, UserDescription, book_details, db,
                    most_rating_editions)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Нужен для безопасности сессий
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mysecretpassword@localhost/mydb'
db.init_app(app)


@app.route('/top')
def top_books():
    return render_template('top_books.html', books=most_rating_editions())


@app.route('/show-book')
def show_books():
    return render_template('books_template.html', results=book_details())


@app.route('/')
def index():
    return render_template('index.html', books=most_rating_editions())


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']

    new_user = User(first_name=first_name, last_name=last_name)
    db.session.add(new_user)
    db.session.commit()

    hashed_password = password
    new_user_description = UserDescription(
        user_id=new_user.id,
        email=email,
        password=hashed_password
    )
    db.session.add(new_user_description)
    db.session.commit()
    return redirect(url_for('users'))


@app.route('/users')
def users():
    all_users = User.query.all()
    return render_template('after_registration.html', users=all_users, total=len(all_users))


@app.route('/logout')
def logout():
    session.pop('login', None)
    session.pop('user_id', None)
    session.pop('name', None)
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    password = request.form['password']
    if email == 'admin@admin.ru' and password == 'admin':
        session['user_id'] = 'admin'
        return redirect(url_for('index'))
    user = UserDescription.query.filter_by(email=email, password=password).first()
    if user:
        session['user_id'] = user.id
        session['login'] = True
        session['name'] = user.user.first_name
        return redirect(url_for('index'))
    else:
        flash('Неверный адрес электронной почты или пароль')


if __name__ == "__main__":
    app.run(debug=True)
