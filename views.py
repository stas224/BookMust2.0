import datetime
from hashlib import md5

from flask import (Request, make_response, redirect, render_template, session,
                   url_for)
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from sqlalchemy.orm import joinedload
from wtforms import StringField, SubmitField

from bookmust.utils.s3 import bucket_name, get_presigned_url, get_s3
from models import (Author, BookBase, BookBaseGenre, BookEdition, Bookmark,
                    BookPublisher, BooksAuthor, BookStatus, Genre, Language,
                    Publisher, Review, Status, User, UserDescription,
                    UserEdition, book_details, get_edition_info,
                    get_user_books, get_user_edition_by_id,
                    most_rating_editions, Role, UserRole)


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
    return render_template(
        'index.html',
        books=most_rating_editions(),
        publishers=len(Publisher.query.all()),
        users=len(User.query.all()),
        bbooks=len(BookEdition.query.all())
    )


def stats_view():
    return render_template('stats.html', books=get_user_books(session["user_id"], None_flag=True))


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

    exist = UserDescription.query.filter_by(email=email).all()
    if exist:
        return 'Такой уже есть, ссоре'
    new_user = User(first_name=first_name, last_name=last_name)
    db.session.add(new_user)
    db.session.commit()

    hashed_password = md5(password.encode()).hexdigest()
    new_user_description = UserDescription(
        user_id=new_user.id,
        email=email,
        password=hashed_password,
        join_date=datetime.datetime.now(),
        bio=""
    )
    db.session.add(new_user_description)
    db.session.commit()
    return redirect(url_for('after_registration'))


def after_registration_view():
    all_users = User.query.all()
    return render_template('after_registration.html', users=all_users, total=len(all_users))


def login_view(request, db):
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    password = request.form['password']

    user = UserDescription.query.filter_by(email=email, password=md5(password.encode()).hexdigest()).all()
    if not user:
        return make_response("Неправильные данные")
    user = user[0]
    role = UserRole.query.filter_by(user_id=user.id).all()
    if role:
        role_id = role[0].role_id
        role = Role.query.filter_by(id=role_id).first().role
    else:
        role = 'user'

    session['user_id'] = user.id
    session['login'] = True
    session['name'] = user.user.first_name
    session['role'] = role
    return redirect(url_for('index'))


def logout_view():
    session.pop('login', None)
    session.pop('user_id', None)
    session.pop('name', None)
    return redirect(url_for('index'))


def collection_view():
    if "user_id" in session:
        return render_template('collection.html', books=get_user_books(session['user_id'], review_flag=False))
    return redirect(url_for('index'))


def account_view():
    if 'user_id' in session:
        if session['user_id'] == "admin":
            return redirect('/admin')
        user_d = UserDescription.query.filter_by(user_id=session['user_id']).first()
        user = User.query.filter_by(id=session['user_id']).first()

        try:
            get_s3().get_object(Bucket=bucket_name, Key=f"icons/{user_d.icon_url}")
            user_d.icon_url = get_presigned_url(f"icons/{user_d.icon_url}")
        except:
            user_d.icon_url = get_presigned_url(f"icons/default.png")
        user_d.first_name = user.first_name
        user_d.last_name = user.last_name
        return render_template('account.html', user=user_d)
    return redirect(url_for('index'))


class SearchForm(FlaskForm):
    query = StringField('')
    submit = SubmitField('Поиск')


def search_and_add_view(request, db, cache):
    form = SearchForm()
    results = []
    message = text = ""

    if form.validate_on_submit() and 'query' in request.form:

        query = form.query.data
        rendered_template = cache.get(query)
        if rendered_template:
            return rendered_template

        results = search_results(query, db)
        if not results:
            text = "Ничего не найдено (╥﹏╥)"

    elif 'edition_id' in request.form:
        return add_to_collection(request.form['edition_id'], db)

    rendered_template = render_template('search.html', form=form, results=results, message=message, text=text)

    if form.validate_on_submit() and 'query' in request.form:
        cache.set(form.query.data, rendered_template, timeout=600)

    return rendered_template


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
    return redirect(url_for('collection'))


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


def change_profile_view(request, db):
    user_id = session['user_id']
    user_d = UserDescription.query.filter_by(user_id=user_id).first()
    if request.files['icon'].filename:
        get_s3().upload_fileobj(request.files['icon'], bucket_name, f"icons/{user_d.icon_url}")
    user = User.query.filter_by(id=user_id).first()
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user_d.bio = request.form['bio']
    db.session.commit()
    return redirect(url_for('account'))


def pool_add_book_view(request, db):
    if request.method == 'GET':
        publishers = Publisher.query.all()
        publisher_names = [publisher.name for publisher in publishers]
        genres = Genre.query.all()
        genre_names = [genre.name for genre in genres]
        languages = Language.query.all()
        language_names = [language.short_name for language in languages]
        authors = Author.query.all()
        authors_names = [f"{author.name} {author.last_name}" for author in authors]

        return render_template('add_book_in_pool.html',
                               publishers=publisher_names,
                               authors=authors_names,
                               genres=genre_names,
                               languages=language_names)
    image = request.files['image']
    title = request.form['title']
    author_name = request.form['author'].split()
    genre = request.form['genre']
    publisher_name = request.form['publisher']
    release_date = request.form['release_date']
    publish_date = request.form['publish_date']
    language_name = request.form['language']
    isbn = request.form['isbn']

    book_base = BookBase.query.filter_by(isbn=isbn).first()
    if not book_base:
        book_base = BookBase(name=title, isbn=isbn, write_date=publish_date)
        db.session.add(book_base)
        db.session.commit()
        autor = Author.query.filter_by(name=author_name[0], last_name=author_name[1]).first()
        book_autor = BooksAuthor(book_id=book_base.id, author_id=autor.id)
        db.session.add(book_autor)
        db.session.commit()
        publisher = Publisher.query.filter_by(name=publisher_name).first()
        book_publisher = BookPublisher(book_id=book_base.id, publisher_id=publisher.id)
        db.session.add(book_publisher)
        db.session.commit()
        genre = Genre.query.filter_by(name=genre).first()
        book_genre = BookBaseGenre(book_base_id=book_base.id, genre_id=genre.id)
        db.session.add(book_genre)
        db.session.commit()
    else:
        book_publisher = BookPublisher.query.filter_by(book_id=book_base.id).first()

    language = Language.query.filter_by(short_name=language_name).first()
    book_edition = BookEdition(book_publisher_id=book_publisher.id,
                               release_date=release_date,
                               language_id=language.id,
                               url='/',)
    db.session.add(book_edition)
    db.session.commit()

    return redirect(url_for('index'))
