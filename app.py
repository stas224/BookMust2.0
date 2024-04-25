from hashlib import md5

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from models import (User, UserDescription, book_details, db, get_user_books,
                    most_rating_editions, Author, Genre, BookBase, Publisher, Language,
                    BookEdition, Review)


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


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mysecretpassword@localhost/mydb'
db.init_app(app)

admin = Admin(app, name='BookMust AdminPanel', template_mode='bootstrap3', index_view=AuthAdminIndexView())

admin.add_view(BookBaseView(BookBase, db.session))
for table in [User, UserDescription, Author, Genre, Publisher, Language,
              BookEdition, Review]:
    admin.add_view(AuthAdminModelView(table, db.session))


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

    hashed_password = md5(password.encode()).hexdigest()
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


@app.route('/account', methods=['GET', 'POST'])
def account():
    if "user_id" in session:
        if session['user_id'] == 'admin':
            return redirect('/admin')
        return render_template('account.html', books=get_user_books(session['user_id']))
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
