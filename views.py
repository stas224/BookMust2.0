from hashlib import md5

from flask import Request, flash, redirect, render_template, session, url_for
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from sqlalchemy.orm import joinedload
from wtforms import StringField, SubmitField

from bookmust.utils.s3 import get_presigned_url
from models import (Author, BookBase, BookBaseGenre, BookEdition, Bookmark,
                    BookPublisher, BooksAuthor, BookStatus, Genre, Language,
                    Publisher, Review, Status, User, UserDescription,
                    UserEdition, book_details, get_edition_info,
                    get_user_books, get_user_edition_by_id,
                    most_rating_editions)


class AuthAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if 'user_id' in session and session['user_id'] == 'admin':
            return super(AuthAdminIndexView, self).index()
        else:
            return redirect(url_for('login'))

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


def stats_view():
    return render_template('stats.html', books=get_user_books(session["user_id"]))


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
        return render_template('account.html', books=get_user_books(session['user_id'], review_flag=False))
    return redirect(url_for('index'))


class SearchForm(FlaskForm):
    query = StringField('')
    submit = SubmitField('Поиск')


def search_and_add_view(request, db):
    form = SearchForm()
    results = []
    message = text = ""

    if form.validate_on_submit() and 'query' in request.form:
        query = form.query.data
        results = search_results(query, db)
        if not results:
            text = "Ничего не найдено (╥﹏╥)"

    elif 'edition_id' in request.form:
        # Добавление книги в коллекцию
        return add_to_collection(request.form['edition_id'], db)

    return render_template('search.html', form=form, results=results, message=message, text=text)


def search_results(query, db):
    # Объединение запросов для поиска по различным полям
    results = BookEdition.query \
        .join(BookPublisher) \
        .join(BookBase) \
        .join(BooksAuthor) \
        .join(Author) \
        .join(BookBaseGenre) \
        .join(Genre) \
        .join(Publisher) \
        .options(joinedload(BookEdition.book_publisher).joinedload(BookPublisher.publisher),
                 joinedload(BookEdition.book_publisher).joinedload(BookPublisher.book).joinedload(
                     BookBase.authors).joinedload(BooksAuthor.author),
                 joinedload(BookEdition.book_publisher).joinedload(BookPublisher.book).joinedload(
                     BookBase.genres).joinedload(BookBaseGenre.genre)) \
        .filter(
        db.or_(
            BookBase.name.ilike(f'%{query}%'),
            Author.name.ilike(f'%{query}%'),
            Author.last_name.ilike(f'%{query}%'),
            Genre.name.ilike(f'%{query}%'),
            Publisher.name.ilike(f'%{query}%'),
            BookEdition.rating.cast(db.String).ilike(f'%{query}%')
        )
    ).distinct().all()
    for book_edition in results:
        book_edition.cover = get_presigned_url(f"covers/{book_edition.cover_path}")
    return results


def add_to_collection(edition_id, db):
    user_id = session['user_id']
    existing_entry = UserEdition.query.filter_by(user_id=user_id, edition_id=edition_id).first()
    if not existing_entry:
        new_entry = UserEdition(user_id=user_id, edition_id=edition_id)
        db.session.add(new_entry)
        db.session.commit()
        return detailed_page_view(new_entry)
    else:
        message = "Эта книга уже есть у тебя в коллекции!"
        return render_template('search.html', form=SearchForm(), results=None, message=message, text=None)


def detailed_page_view(user_edition):
    if isinstance(user_edition, Request):
        user_edition = get_user_edition_by_id(user_edition.form.get('user_edition_id'))
    book_info = get_edition_info(user_edition, review_flag=False)
    book_info["description"] = "Это описание книги если что"
    statuses = Status.query.all()
    book_info['statuses'] = [status.status for status in statuses]

    return render_template('detailed_page.html', book=book_info)


def add_book_account_view(request, db):
    form_data = request.form
    user_edition_id = form_data.get('user_edition_id')
    reading_status = form_data.get('reading_status') if form_data.get('reading_status') else None
    page_number = form_data.get('page_number') if form_data.get('page_number') else None
    rating = form_data.get('rating') if form_data.get('rating') else None
    review = form_data.get('review') if form_data.get('review') else None

    review_entry = Review.query.filter_by(user_edition_id=user_edition_id).first()
    if review_entry:
        review_entry.review = review if review else review_entry.review
        review_entry.rating = rating if rating else review_entry.rating
    else:
        new_review = Review(user_edition_id=user_edition_id, review=review, rating=rating)
        db.session.add(new_review)

    bookmark_entry = Bookmark.query.filter_by(user_edition_id=user_edition_id).first()
    if bookmark_entry:
        bookmark_entry.page = page_number if page_number else bookmark_entry.page
    else:
        new_bookmark = Bookmark(user_edition_id=user_edition_id, page=page_number)
        db.session.add(new_bookmark)

    if reading_status:
        book_status_entry = BookStatus.query.filter_by(user_edition_id=user_edition_id).first()
        status_entry = Status.query.filter_by(status=reading_status).first()
        if book_status_entry:
            book_status_entry.status_id = status_entry.id
        else:
            new_status = BookStatus(user_edition_id=user_edition_id, status_id=status_entry.id)
            db.session.add(new_status)

    db.session.commit()
    return redirect(url_for('account'))


def delete_user_edition_view(request, db):
    user_edition_id = request.form['user_edition_id']

    try:
        Bookmark.query.filter_by(user_edition_id=user_edition_id).delete()
        Review.query.filter_by(user_edition_id=user_edition_id).delete()
        BookStatus.query.filter_by(user_edition_id=user_edition_id).delete()
        UserEdition.query.filter_by(id=user_edition_id).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    return redirect(url_for('account'))
