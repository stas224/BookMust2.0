from flask import Flask, request
from flask_admin import Admin
from models import db
from views import AuthAdminIndexView, show_books_view, top_books_view, index_view, activate_admin_views, \
    register_view, after_registration_view, login_view, logout_view, account_view

from bookmust.utils.s3 import fill_s3_if_not_filled

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


# presentation for users
@app.route('/top')
def top_books():
    return top_books_view()


@app.route('/show-book')
def show_books():
    return show_books_view()


@app.route('/account', methods=['GET', 'POST'])
def account():
    return account_view(request)


if __name__ == "__main__":
    fill_s3_if_not_filled()
    app.run(debug=True)
