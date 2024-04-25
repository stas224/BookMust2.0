from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(256), nullable=False)
    birth_date = db.Column(db.Date)
    books = db.relationship('BookAuthor', back_populates='author')


class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    # Удалите genre_id из BookBase и используйте это отношение для связи многие ко многим
    books = db.relationship('BookBaseGenre', back_populates='genre', lazy='dynamic')


class BookBase(db.Model):
    __tablename__ = 'book_base'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    isbn = db.Column(db.String(256))
    write_date = db.Column(db.Date)
    genres = db.relationship('BookBaseGenre', back_populates='book', lazy='dynamic')
    # Другие отношения
    authors = db.relationship('BookAuthor', back_populates='book')
    publishers = db.relationship('BookPublisher', back_populates='book')


class BookBaseGenre(db.Model):
    __tablename__ = 'book_base_genres'
    id = db.Column(db.Integer, primary_key=True)
    book_base_id = db.Column(db.Integer, db.ForeignKey('book_base.id'), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=False)

    book = db.relationship('BookBase', back_populates='genres')
    genre = db.relationship('Genre', back_populates='books')


class BookAuthor(db.Model):
    __tablename__ = 'books_authors'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book_base.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    book = db.relationship('BookBase', back_populates='authors')
    author = db.relationship('Author', back_populates='books')


class Publisher(db.Model):
    __tablename__ = 'publishers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(256))
    # country = db.Column(db.String(256))
    contacts = db.Column(db.String(256))
    books = db.relationship('BookPublisher', back_populates='publisher')


class BookPublisher(db.Model):
    __tablename__ = 'book_publisher'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book_base.id'))
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))
    book = db.relationship('BookBase', back_populates='publishers')
    publisher = db.relationship('Publisher', back_populates='books')


class Language(db.Model):
    __tablename__ = 'languages'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(256), nullable=False)
    short_name = db.Column(db.String(256), nullable=False)


class BookEdition(db.Model):
    __tablename__ = 'book_edition'
    id = db.Column(db.Integer, primary_key=True)
    book_publisher_id = db.Column(db.Integer, db.ForeignKey('book_publisher.id'))
    release_date = db.Column(db.Date)
    language_id = db.Column(db.Integer, db.ForeignKey('languages.id'))
    url = db.Column(db.String(256))
    rating = db.Column(db.Numeric, default=0)
    language = db.relationship('Language')
    book_publisher = db.relationship('BookPublisher')


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(256), nullable=False)
    editions = db.relationship('UserEdition', back_populates='user')
    descriptions = db.relationship('UserDescription', backref='user', lazy=True,
                                   primaryjoin="User.id==UserDescription.user_id")


class UserDescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    join_date = db.Column(db.Date, default=datetime.utcnow)
    bio = db.Column(db.String(512))
    # country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    icon_url = db.Column(db.String(64))


class UserEdition(db.Model):
    __tablename__ = 'user_edition'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    edition_id = db.Column(db.Integer, db.ForeignKey('book_edition.id'))
    user = db.relationship('User', back_populates='editions')
    edition = db.relationship('BookEdition')
    reviews = db.relationship('Review', back_populates='user_edition')


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_edition_id = db.Column(db.Integer, db.ForeignKey('user_edition.id'))
    review = db.Column(db.String(1024))
    rating = db.Column(db.Numeric)
    user_edition = db.relationship('UserEdition', back_populates='reviews')


def book_details():
    return db.session.query(
        BookBase.name.label('book_name'),
        Genre.name.label('genre_name'),
        Author.name.label('author_name'),
        Author.last_name.label('author_last_name'),
        Publisher.name.label('publisher_name')
    ).join(Genre, BookBase.genre_id == Genre.id
           ).join(BookAuthor, BookBase.id == BookAuthor.book_id
                  ).join(Author, BookAuthor.author_id == Author.id
                         ).join(BookPublisher, BookBase.id == BookPublisher.book_id
                                ).join(Publisher, BookPublisher.publisher_id == Publisher.id
                                       ).all()


def most_rating_editions(count=5):
    return db.session.query(
        BookBase.name.label('name'),
        Publisher.name.label('publisher'),
        BookEdition.rating
    ).join(BookPublisher, BookPublisher.id == BookEdition.book_publisher_id
           ).join(BookBase, BookBase.id == BookPublisher.book_id
                  ).join(Publisher, Publisher.id == BookPublisher.publisher_id
                         ).distinct(BookBase.name, Publisher.name, BookEdition.rating
                                    ).order_by(BookEdition.rating.desc()
                                               ).limit(count).all()


def get_user_books(user_id):
    # Найти все издания пользователя
    user_id = 1 if user_id != 1 else user_id
    user_editions = UserEdition.query.filter_by(user_id=user_id).all()

    results = []

    for user_edition in user_editions:
        # Информация об отзыве
        reviews = Review.query.filter_by(user_edition_id=user_edition.id).all()

        # Информация об издании
        edition = user_edition.edition

        if edition:
            # Информация о издателе и книге
            book_publisher = edition.book_publisher
            publisher = book_publisher.publisher if book_publisher else None
            book = book_publisher.book if book_publisher else None
            genre_names = [genre_association.genre.name for genre_association in book.genres]

            if book:
                # Информация об авторах книги
                authors = [ba.author for ba in book.authors]
                author_names = ', '.join([f"{author.name} {author.last_name}" for author in authors if author])
            else:
                author_names = None

            # Сбор данных для данного издания
            edition_details = {
                "name": book.name if book else "Недоступно",
                "genres": ', '.join(genre_names),
                "author": author_names,
                "publisher": publisher.name if publisher else "Недоступно",
                "site_rating": edition.rating,
                "user_rating": None,
                "user_review": None
            }

            # Информация об отзывах пользователя
            if reviews:
                # Предполагаем, что у каждого издания только один отзыв от пользователя
                review = reviews[0]
                edition_details["user_rating"] = review.rating
                edition_details["user_review"] = review.review

            results.append(edition_details)

    return results
