from flask import Flask, request
from flask_admin import Admin
from flask_caching import Cache

from bookmust.utils.s3 import fill_s3_if_not_filled
from models import db
from views import (AuthAdminIndexView, account_view, activate_admin_views,
                   add_book_account_view, after_registration_view,
                   change_profile_view, collection_view,
                   delete_user_edition_view, detailed_page_view, index_view,
                   login_view, logout_view, pool_add_book_view, register_view,
                   search_and_add_view, show_books_view, stats_view,
                   top_books_view)

# configure app
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mysecretpassword@localhost/mydb'
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = "redis://localhost:6379/0"
db.init_app(app)
cache = Cache(app)

# configure admin panel
admin = Admin(app, name='BookMust AdminPanel', template_mode='bootstrap3', index_view=AuthAdminIndexView())
activate_admin_views(admin, db)


@app.route('/')
@cache.cached(timeout=600, key_prefix='index_page')
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
    return login_view(request, db)


@app.route('/logout')
def logout():
    if cache.has('index_page'):
        cache.delete('index_page')
    return logout_view()


# common func
@app.route('/top')
def top_books():
    return top_books_view()


@app.route('/show-book')
def show_books():
    return show_books_view()


@app.route('/collection', methods=['GET', 'POST'])
def collection():
    return collection_view()


# for users
@app.route('/account', methods=['GET', 'POST'])
def account():
    return account_view()


@app.route('/search-and-add', methods=['GET', 'POST'])
def search_and_add():
    return search_and_add_view(request, db, cache)


@app.route('/stats')
def stats():
    return stats_view()


@app.route('/detailed-description', methods=['POST'])
def detailed_page_with_adding():
    if cache.has('index_page'):
        cache.delete('index_page')
    return add_book_account_view(request, db)


@app.route('/detailed-description-update', methods=['POST'])
def detailed_page_with_update():
    if cache.has('index_page'):
        cache.delete('index_page')
    return detailed_page_view(request)


@app.route('/detailed-description-delete', methods=['POST'])
def delete_user_edition():
    return delete_user_edition_view(request, db)


@app.route('/pool-add-book', methods=['GET', 'POST'])
def pool_add_book():
    if request.method == 'POST':
        cache.clear()
    return pool_add_book_view(request, db)


@app.route('/change-profile', methods=['POST'])
def change_profile():
    return change_profile_view(request, db)


fill_s3_if_not_filled()
if __name__ == "__main__":
    app.run(debug=True)
