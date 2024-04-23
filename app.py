from flask import Flask, render_template
from models import db, BookEdition, book_details, most_rating_editions

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mysecretpassword@localhost/mydb'
db.init_app(app)


@app.route('/top')
def top_books():
    return render_template('top_books.html', books=most_rating_editions())


@app.route('/')
def show_books():
    return render_template('books_template.html', results=book_details())


if __name__ == "__main__":
    app.run(debug=True)
