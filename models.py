from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


from bookmust.utils.s3 import get_presigned_url

db = SQLAlchemy()


class Country(db.Model):
    __tablename__ = 'country'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(32))
    short_name = db.Column(db.String(8))
    flag_url = db.Column(db.String(64))


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    birth_date = db.Column(db.Date)
    country_id = db.Column(db.Integer, ForeignKey('country.id'))
    country = relationship("Country", backref="authors")


class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    description = db.Column(db.String(256))


class BookBase(db.Model):
    __tablename__ = 'book_base'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    isbn = db.Column(db.String(256))
    write_date = db.Column(db.Date)


class BookBaseGenre(db.Model):
    __tablename__ = 'book_base_genres'
    id = db.Column(db.Integer, primary_key=True)
    book_base_id = db.Column(db.Integer, ForeignKey('book_base.id'))
    genre_id = db.Column(db.Integer, ForeignKey('genres.id'))
    book_base = relationship("BookBase", backref="genres")
    genre = relationship("Genre", backref="books")


class BooksAuthor(db.Model):
    __tablename__ = 'books_authors'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, ForeignKey('book_base.id'))
    author_id = db.Column(db.Integer, ForeignKey('authors.id'))
    book = relationship("BookBase", backref="authors")
    author = relationship("Author", backref="books")


class Publisher(db.Model):
    __tablename__ = 'publishers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    description = db.Column(db.String(256))
    country_id = db.Column(db.Integer, ForeignKey('country.id'))
    contacts = db.Column(db.String(256))
    country = relationship("Country", backref="publishers")


class BookPublisher(db.Model):
    __tablename__ = 'book_publisher'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, ForeignKey('book_base.id'))
    publisher_id = db.Column(db.Integer, ForeignKey('publishers.id'))
    book = relationship("BookBase", backref="publishers")
    publisher = relationship("Publisher", backref="books")


class Language(db.Model):
    __tablename__ = 'languages'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(256))
    short_name = db.Column(db.String(256))


class BookEdition(db.Model):
    __tablename__ = 'book_edition'
    id = db.Column(db.Integer, primary_key=True)
    book_publisher_id = db.Column(db.Integer, ForeignKey('book_publisher.id'))
    release_date = db.Column(db.Date)
    language_id = db.Column(db.Integer, ForeignKey('languages.id'))
    url = db.Column(db.String(256))
    cover_path = db.Column(db.String(256))
    rating = db.Column(db.Numeric, default=0)
    language = relationship("Language", backref="editions")
    book_publisher = relationship("BookPublisher", backref="editions")


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))


class UserEdition(db.Model):
    __tablename__ = 'user_edition'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'))
    edition_id = db.Column(db.Integer, ForeignKey('book_edition.id'))
    user = relationship("User", backref="editions")
    edition = relationship("BookEdition", backref="users")


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_edition_id = db.Column(db.Integer, ForeignKey('user_edition.id'))
    review = db.Column(db.String(1024))
    rating = db.Column(db.Numeric)


class UserDescription(db.Model):
    __tablename__ = 'user_description'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64))
    password = db.Column(db.String(64))
    join_date = db.Column(db.Date)
    bio = db.Column(db.String(512))
    country_id = db.Column(db.Integer, ForeignKey('country.id'))
    user_id = db.Column(db.Integer, ForeignKey('users.id'))
    icon_url = db.Column(db.String(64))
    country = relationship("Country", backref="user_descriptions")
    user = relationship("User", backref="description")


class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    id = db.Column(db.Integer, primary_key=True)
    user_edition_id = db.Column(db.Integer, ForeignKey('user_edition.id'))
    page = db.Column(db.Integer)


class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(32))


class BookStatus(db.Model):
    __tablename__ = 'book_status'
    id = db.Column(db.Integer, primary_key=True)
    user_edition_id = db.Column(db.Integer, ForeignKey('user_edition.id'))
    status_id = db.Column(db.Integer, ForeignKey('status.id'))


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(16))
    table_name = db.Column(db.String(32))
    record_id = db.Column(db.Integer)


def book_details():
    return db.session.query(
        BookBase.name.label('book_name'),
        Genre.name.label('genre_name'),
        Author.name.label('author_name'),
        Author.last_name.label('author_last_name'),
        Publisher.name.label('publisher_name')
    ).join(Genre, BookBase.genre_id == Genre.id
           ).join(BooksAuthor, BookBase.id == BooksAuthor.book_id
                  ).join(Author, BooksAuthor.author_id == Author.id
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
    user_editions = UserEdition.query.filter_by(user_id=user_id).all()

    results = []

    for user_edition in user_editions:
        # Информация об отзыве
        reviews = Review.query.filter_by(user_edition_id=user_edition.id).all()

        # Информация об издании
        edition = user_edition.edition

        if edition:
            # Информация об издателе и книге
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
                "user_review": None,
                "image_url": get_presigned_url(f"covers/{edition.cover_path}")
            }

            # Информация об отзывах пользователя
            if reviews:
                # Предполагаем, что у каждого издания только один отзыв от пользователя
                review = reviews[0]
                edition_details["user_rating"] = review.rating
                edition_details["user_review"] = review.review

            results.append(edition_details)

    return results


def get_stats(user_id):
    data = []
    user_editions = UserEdition.query.filter_by(user_id=user_id).all()

    for user_edition in user_editions:
        reviews = Review.query.filter_by(user_edition_id=user_edition.id).all()
        if not reviews:
            continue
        user_rating = reviews[0].rating
        edition_id = user_edition.edition_id
        book_edition = BookEdition.query.filter_by(id=edition_id).all()[0]
        language = Language.query.filter_by(id=book_edition.language_id).all()[0].short_name
        book_publisher_id = book_edition.book_publisher_id
        book_publisher = BookPublisher.query.filter_by(id=book_publisher_id).all()[0]
        book_id = book_publisher.book_id
        publisher_id = book_publisher.publisher_id
        book = BookBase.query.filter_by(id=book_id).all()[0]
        publisher_name = Publisher.query.filter_by(id=publisher_id).all()[0].name
        data.append({
            "title": book.name,
            "publisher_name": publisher_name,
            "language": language,
            "date": book_edition.release_date,
            "user_rating": user_rating,
            "book_rating": book_edition.rating,
            "cover": get_presigned_url(f"covers/{book_edition.cover_path}")
        })
    return data
