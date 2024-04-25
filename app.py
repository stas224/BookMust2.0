from flask import Flask, request
from flask_admin import Admin

from bookmust.utils.s3 import fill_s3_if_not_filled
from models import db
from views import (AuthAdminIndexView, account_view, activate_admin_views,
                   search_and_add_view, after_registration_view, index_view,
                   login_view, logout_view, register_view, show_books_view,
                   top_books_view)

# configure app
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mysecretpassword@localhost/mydb'
db.init_app(app)

# configure admin panel
admin = Admin(app, name='BookMust AdminPanel', template_mode='bootstrap3', index_view=AuthAdminIndexView())
activate_admin_views(admin, db)


@app.route('/')
def index():
    return index_view()


# auth
@app.route('/register', methods=['GET', 'POST'])
def register():
    return register_view(request, db)


@app.route('/users')
def after_registration():
    return after_registration_view()


@app.route('/login', methods=['GET', 'POST'])
def login():
    return login_view(request)


@app.route('/logout')
def logout():
    return logout_view()


# common func
@app.route('/top')
def top_books():
    return top_books_view()


@app.route('/show-book')
def show_books():
    return show_books_view()


# for users
@app.route('/account', methods=['GET', 'POST'])
def account():
    return account_view(request)


@app.route('/search-and-add', methods=['GET', 'POST'])
def search_and_add():
    return search_and_add_view(request, db)


if __name__ == "__main__":
    fill_s3_if_not_filled()
    app.run(debug=True)
