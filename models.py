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
    description = db.Column(db.String(256))
    books = db.relationship('BookBase', back_populates='genre')


class BookBase(db.Model):
    __tablename__ = 'book_base'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))
    isbn = db.Column(db.String(256))
    write_date = db.Column(db.Date)
    genre = db.relationship('Genre', back_populates='books')
    authors = db.relationship('BookAuthor', back_populates='book')
    publishers = db.relationship('BookPublisher', back_populates='book')


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
    country = db.Column(db.String(256))
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
