from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))


class UserEdition(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'))
    edition_id = db.Column(db.BigInteger, db.ForeignKey('book_edition.id'))
    user = db.relationship('User', backref='user_editions')
    edition = db.relationship('BookEdition', backref='user_editions')


class BookEdition(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    book_publisher_id = db.Column(db.BigInteger, db.ForeignKey('book_publisher.id'))
    year = db.Column(db.Integer)
    language_id = db.Column(db.BigInteger, db.ForeignKey('languages.id'))
    url = db.Column(db.String(255))
    rating = db.Column(db.Integer)
    publisher = db.relationship('BookPublisher', backref='editions')
    language = db.relationship('Languages', backref='editions')


class BookPublisher(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    book_id = db.Column(db.BigInteger, db.ForeignKey('books_base.id'))
    publisher_id = db.Column(db.BigInteger, db.ForeignKey('publishers.id'))
    book = db.relationship('BooksBase', backref='publishers')
    publisher = db.relationship('Publishers', backref='published_books')


class Publishers(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    country = db.Column(db.String(255))
    contacts = db.Column(db.String(255))


class BooksBase(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255))
    genre_id = db.Column(db.BigInteger)
    isbn = db.Column(db.String(13))
    year_published = db.Column(db.Integer)


class Languages(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    short_name = db.Column(db.String(10))
    full_name = db.Column(db.String(100))


class Status(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    status = db.Column(db.String(255))


class BookStatus(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    user_edition_id = db.Column(db.BigInteger, db.ForeignKey('user_edition.id'))
    status_id = db.Column(db.BigInteger, db.ForeignKey('status.id'))
    user_edition = db.relationship('UserEdition', backref='statuses')
    status = db.relationship('Status', backref='book_statuses')


class Bookmarks(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    user_edition_id = db.Column(db.BigInteger, db.ForeignKey('user_edition.id'))
    page = db.Column(db.Integer)
    user_edition = db.relationship('UserEdition', backref='bookmarks')


class Reviews(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    user_edition_id = db.Column(db.BigInteger, db.ForeignKey('user_edition.id'))
    text = db.Column(db.Text)
    rating = db.Column(db.Integer)
    user_edition = db.relationship('UserEdition', backref='reviews')


class Transactions(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    transaction_type = db.Column(db.String(50))
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'))
    edition_id = db.Column(db.BigInteger, db.ForeignKey('book_edition.id'))
    user = db.relationship('User', backref='transactions')
    edition = db.relationship('BookEdition', backref='transactions')


class BooksAuthors(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    book_id = db.Column(db.BigInteger, db.ForeignKey('books_base.id'))
    author_id = db.Column(db.BigInteger)
    book = db.relationship('BooksBase', backref='authors')
