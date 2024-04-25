from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask import session, redirect, url_for, render_template, flash
from models import (User, UserDescription, Author, Genre, Publisher, Language, BookEdition, Review, get_user_books,
                    BookBase)

from models import book_details, most_rating_editions
from hashlib import md5


class AuthAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if 'user_id' in session and session['user_id'] == 'admin':
            return super(AuthAdminIndexView, self).index()
        else:
            return redirect(url_for('login'))  # Предполагается, что у вас есть endpoint для login

    def is_accessible(self):
        return 'user_id' in session and session['user_id'] == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class AuthAdminModelView(ModelView):
    def is_accessible(self):
        return 'user_id' in session and session['user_id'] == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class BookBaseView(AuthAdminModelView):
    column_list = ("id", "name", "isbn", "write_date")
    form_columns = ("name", "isbn", "write_date")
    column_searchable_list = ('name', 'isbn')
    can_view_details = True
    column_details_list = ('id', "name", "isbn", "write_date")


def show_books_view():
    return render_template('books_template.html', results=book_details())


def top_books_view():
    return render_template('top_books.html', books=most_rating_editions())


def index_view():
    return render_template('index.html', books=most_rating_editions())


def activate_admin_views(admin, db):
    admin.add_view(BookBaseView(BookBase, db.session))
    for table in [User, UserDescription, Author, Genre, Publisher, Language,
                  BookEdition, Review]:
        admin.add_view(AuthAdminModelView(table, db.session))


def register_view(request, db):
    if request.method == 'GET':
        return render_template('register.html')

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']

    new_user = User(first_name=first_name, last_name=last_name)
    db.session.add(new_user)
    db.session.commit()

    hashed_password = md5(password.encode()).hexdigest()
    new_user_description = UserDescription(
        user_id=new_user.id,
        email=email,
        password=hashed_password
    )
    db.session.add(new_user_description)
    db.session.commit()
    return redirect(url_for('users'))


def after_registration_view():
    all_users = User.query.all()
    return render_template('after_registration.html', users=all_users, total=len(all_users))


def login_view(request):
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    password = request.form['password']

    if email == 'admin@admin.ru' and password == 'admin':
        session['user_id'] = 'admin'
        session['login'] = True
        session['name'] = 'admin'
        return redirect(url_for('index'))

    user = UserDescription.query.filter_by(email=email, password=md5(password.encode()).hexdigest()).first()
    if user:
        session['user_id'] = user.id
        session['login'] = True
        session['name'] = user.user.first_name
        return redirect(url_for('index'))
    else:
        flash('Неверный адрес электронной почты или пароль')


def logout_view():
    session.pop('login', None)
    session.pop('user_id', None)
    session.pop('name', None)
    return redirect(url_for('index'))


def account_view(request):
    if "user_id" in session:
        if session['user_id'] == 'admin':
            return redirect('/admin')
        return render_template('account.html', books=get_user_books(session['user_id']))
    return redirect(url_for('index'))
