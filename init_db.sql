create table country(
    id serial primary key,
    full_name varchar(32),
    short_name varchar(8),
    flag_url varchar(64)
);
insert into country (full_name, short_name, flag_url)
values
    ('Russia', 'RU', 'flag_ru.png'),
    ('United States of America', 'US', 'flag_usa.png'),
    ('France', 'FR', 'flag_fr.png'),
    ('Germany', 'DE', 'flag_de.png'),
    ('Australia', 'AU', 'flag_au.png'),
    ('China', 'CN', 'flag_cn.png'),
    ('Canada', 'CA', 'flag_ca.png'),
    ('United Kingdom', 'UK', 'flag_uk.png');

create table authors(
    id serial primary key,
    name varchar(256),
    last_name varchar(256),
    birth_date date,
    country_id int references country(id)
);
INSERT INTO authors (name, last_name, birth_date, country_id)
VALUES
    ('J.R.R.', 'Tolkien', '1892-01-03', 8),
    ('Leo', 'Tolstoy', '1828-09-09', 1),
    ('Mark', 'Twain', '1835-11-30', 2),
    ('Charles', 'Dickens', '1812-02-07', 8),
    ('Virginia', 'Woolf', '1882-01-25', 2),
    ('Harper', 'Lee', '1926-04-28', 3),
    ('F. Scott', 'Fitzgerald', '1896-09-24', 5),
    ('Ernest', 'Hemingway', '1899-07-21', 2);

create table genres(
    id serial primary key,
    name varchar(256),
    description varchar(256)
);
INSERT INTO genres (name, description)
VALUES
    ('Fantasy', 'Imaginative fiction set in alternate worlds or realities.'),
    ('Historical Fiction', 'Fiction set in the past, often featuring real historical events and figures.'),
    ('Mystery', 'A genre of fiction that deals with the solution of a crime or the unraveling of secrets.'),
    ('Science Fiction', 'Fiction that deals with imaginative concepts such as futuristic science and technology.'),
    ('Romance', 'A genre focused on romantic love stories between characters.'),
    ('Thriller', 'A genre characterized by fast-paced plots, frequent action, and danger.'),
    ('Horror', 'A genre of fiction intended to frighten, scare, or disgust the reader/viewer.');

create table book_base(
    id serial primary key,
    name varchar(256),
    isbn varchar(256),
    write_date date
);
INSERT INTO book_base (name, isbn, write_date)
VALUES
    ('The Lord of the Rings', '9780618640157', '1954-07-29'),
    ('The Hobbit', '9780547928227', '1937-09-21'),
    ('War and Peace', '9780199232765', '1869-01-01'),
    ('Anna Karenina', '9780143035008', '1877-01-01'),
    ('The Adventures of Huckleberry Finn', '9780199536559', '1884-12-10'),
    ('Oliver Twist', '9780141439747', '1837-01-01'),
    ('To the Lighthouse', '9780156907392', '1927-05-05'),
    ('Mrs. Dalloway', '9780156030359', '1925-05-14'),
    ('To Kill a Mockingbird', '9780446310789', '1960-07-11'),
    ('The Great Gatsby', '9780743273565', '1925-04-10'),
    ('For Whom the Bell Tolls', '9780684803357', '1940-10-21'),
    ('A Farewell to Arms', '9780684801469', '1929-09-27');

create table book_base_genres(
    id serial primary key,
    book_base_id int references book_base(id),
    genre_id int references genres(id)
);
insert into book_base_genres (book_base_id, genre_id)
values
    (1, 1),
    (2, 1),
    (3, 2),
    (4, 5),
    (5, 5),
    (6, 5),
    (7, 5),
    (8, 5),
    (9, 5),
    (10, 5),
    (11, 5),
    (12, 5);

create table books_authors(
    id serial primary key,
    book_id int references book_base(id),
    author_id int references authors(id)
);
insert into books_authors (book_id, author_id)
values
    (1, 1),
    (2, 1),
    (3, 2),
    (4, 2),
    (5, 3),
    (6, 4),
    (7, 5),
    (8, 5),
    (9, 6),
    (10, 7),
    (11, 8),
    (12, 8);

create table publishers(
    id serial primary key,
    name varchar(256),
    description varchar(256),
    country_id int references country(id),
    contacts varchar(256)
);
INSERT INTO publishers (name, description, country_id, contacts)
VALUES
    ('Penguin Random House', 'Publishing company known for a wide range of books.', 2, 'contact@penguinrandomhouse.com'),
    ('HarperCollins Publishers', 'One of the world largest publishing companies.', 2, 'info@harpercollins.com'),
    ('Simon & Schuster', 'Global publishing company known for bestsellers and literary fiction.', 2, 'info@simonandschuster.com'),
    ('Macmillan Publishers', 'Global trade publishing company.', 8, 'info@macmillan.com'),
    ('Hachette Livre', 'Largest publishing company in France and one of the largest in the world.', 3, 'info@hachette.fr'),
    ('Pearson plc', 'Multinational publishing and education company.', 8, 'contact@pearson.com'),
    ('Oxford University Press', 'Largest university press in the world.', 8, 'info@oup.com');

create table book_publisher(
    id serial primary key,
    book_id int references book_base(id),
    publisher_id int references publishers(id)
);
INSERT INTO book_publisher (book_id, publisher_id)
VALUES
    (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7),
    (8, 1), (9, 2), (10, 3), (11, 4), (12, 5), (1, 6), (2, 7),
    (3, 1), (4, 2), (5, 3), (6, 4), (7, 5), (8, 6);

create table languages(
    id serial primary key,
    full_name varchar(256),
    short_name varchar(256)
);
INSERT INTO languages (full_name, short_name)
VALUES
    ('English', 'EN'),
    ('Spanish', 'ES'),
    ('French', 'FR'),
    ('German', 'DE'),
    ('Chinese', 'ZH'),
    ('Russian', 'RU'),
    ('Japanese', 'JA');

create table book_edition(
    id serial primary key,
    book_publisher_id int references book_publisher(id),
    release_date date,
    language_id int references languages(id),
    url varchar(256),
    cover_path varchar(256),
    description varchar(1024),
    rating decimal default 0
);
INSERT INTO book_edition (book_publisher_id, release_date, language_id, url, cover_path, description)
VALUES
    (1, '2023-01-15', 1, 'lotr1.txt', 'lotr1.png', 'Good book'),
    (2, '2023-02-20', 2, 'hobbit1.txt', 'hobbit1.png', 'Bad book'),
    (3, '2023-03-25', 3, 'wap1.txt', 'wap1.png', 'Excellent book'),
    (4, '2023-04-30', 4, 'ak1.txt', 'ak1.png', 'Romance book'),
    (5, '2023-05-05', 5, 'hf1.txt', 'hf1.png', 'Happy book'),
    (6, '2023-06-10', 6, 'ot1.txt', 'ot1.png', 'Sad book'),
    (7, '2023-07-15', 7, 'tl1.txt', 'tl1.png', 'Nice book'),
    (8, '2023-08-20', 1, 'mrd1.txt', 'mrd1.png', 'Interesting book'),
    (9, '2023-09-25', 2, 'km1.txt', 'km1.png', 'Ordinary book'),
    (10, '2023-10-30', 3, 'gg1.txt', 'gg1.png', 'Captivating book'),
    (11, '2023-11-05', 4, 'fh1.txt', 'fh1.png', 'Trivial book'),
    (12, '2023-12-10', 5, 'fa1.txt', 'fa1.png', 'Extraordinary book'),
    (13, '2024-01-15', 6, 'lotr2.txt', 'lotr2.png', 'Meh book'),
    (14, '2024-02-20', 7, 'hobbit2.txt', 'hobbit2.png', 'Fine book'),
    (15, '2024-03-25', 1, 'wap2.txt', 'wap2.png', 'Cool book'),
    (16, '2024-04-30', 2, 'ak2.txt', 'ak2.png', 'Best book'),
    (17, '2024-05-05', 3, 'hf2.txt', 'hf2.png', 'Great book'),
    (18, '2024-06-10', 4, 'ot2.txt', 'ot2.png', 'Banal book'),
    (19, '2024-07-15', 5, 'tl2.txt', 'tl2.png', 'Super book'),
    (20, '2024-08-20', 6, 'mrd2.txt', 'mrd2.png', 'Fascinating book'),
    (1, '2024-09-25', 7, 'lotr3.txt', 'lotr3.png', 'Regular book'),
    (2, '2024-10-30', 1, 'hobbit3.txt', 'hobbit3.png', 'Mediocre book'),
    (3, '2024-11-05', 2, 'wap3.txt', 'wap3.png', 'Boring book'),
    (4, '2024-12-10', 3, 'ak47.txt', 'ak47.png', 'Fantastic book');

create table users(
    id serial primary key,
    first_name varchar(256),
    last_name varchar(256)
);
INSERT INTO users (first_name, last_name)
VALUES
    ('John', 'Doe'),
    ('Jane', 'Smith'),
    ('Michael', 'Johnson'),
    ('Emily', 'Brown'),
    ('David', 'Jones'),
    ('Sarah', 'Williams'),
    ('James', 'Taylor'),
    ('Emma', 'Wilson'),
    ('William', 'Davis'),
    ('Olivia', 'Martinez'),
    ('Benjamin', 'Anderson'),
    ('Ava', 'Thomas'),
    ('Daniel', 'Hernandez');

create table user_edition(
    id serial primary key,
    user_id int references users(id),
    edition_id int references book_edition(id)
);
INSERT INTO user_edition (user_id, edition_id)
VALUES
    (1, 1), (1, 2), (1, 3), (2, 4), (2, 5),
    (3, 6), (3, 7), (4, 8), (4, 9), (5, 10),
    (6, 11), (6, 12), (7, 13), (7, 14), (8, 15),
    (9, 16), (9, 17), (10, 18), (10, 19), (11, 20),
    (2, 1);

create table reviews(
    id serial primary key,
    user_edition_id int references user_edition(id),
    review varchar(1024),
    rating decimal
);

CREATE OR REPLACE FUNCTION update_book_edition_rating()
RETURNS TRIGGER AS $$
DECLARE
    new_average DECIMAL;
BEGIN
    SELECT AVG(rating) INTO new_average
    FROM reviews
    JOIN user_edition ON user_edition.id = reviews.user_edition_id
    WHERE user_edition.edition_id = (
        SELECT edition_id
        FROM user_edition
        WHERE id = NEW.user_edition_id
    );

    IF new_average IS NOT NULL THEN
        UPDATE book_edition
        SET rating = new_average
        WHERE id = (
            SELECT edition_id
            FROM user_edition
            WHERE id = NEW.user_edition_id
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_book_rating
AFTER INSERT ON reviews
FOR EACH ROW
EXECUTE FUNCTION update_book_edition_rating();

INSERT INTO reviews (user_edition_id, review, rating)
VALUES
    (1, 'Great book! Loved the storyline and characters.', 5),
    (2, 'The plot was engaging, but the ending felt rushed.', 4),
    (3, 'Disappointing. Expected more from this author.', 2),
    (4, 'Couldn''t put it down! A must-read for mystery lovers.', 5),
    (5, 'Not my cup of tea. Slow pacing and uninteresting characters.', 2),
    (6, 'An engaging story with captivating characters, but the pacing felt slightly uneven', 4),
    (7, 'Struggled to get through it. Found it boring and predictable.', 2),
    (8, 'A timeless classic. Beautifully written.', 5),
    (9, 'Enjoyable read with some unexpected twists.', 4),
    (10, 'Didn''t live up to the hype. Overrated.', 3),
    (11, 'Heartwarming story with memorable characters.', 4),
    (12, 'Thrilling from start to finish. Highly recommend!', 5),
    (13, 'Interesting premise, but execution fell short.', 3),
    (14, 'Couldn''t connect with the characters. Story lacked depth.', 2),
    (15, 'Compelling and thought-provoking. Left me wanting more.', 4),
    (21, 'Not good book', 1);

create table user_description(
    id serial primary key,
    email varchar(64),
    password varchar(64),
    join_date date,
    bio varchar(512),
    country_id int references country(id),
    user_id int references users(id),
    icon_url varchar(64)
);
INSERT INTO user_description (email, password, join_date, bio, country_id, user_id, icon_url)
VALUES
    ('1@1.1', MD5('1'), '2023-01-01', 'Bio for User 1', 1, 1, '1.png'),
    ('2@2.2', MD5('2'), '2023-02-02', 'Bio for User 2', 2, 2, '2.png'),
    ('3@3.3', MD5('3'), '2023-03-03', 'Bio for User 3', 3, 3, '3.png'),
    ('user4@example.com', MD5('password4'), '2023-04-04', 'Bio for User 4', 4, 4, '4.png'),
    ('user5@example.com', MD5('password5'), '2023-05-05', 'Bio for User 5', 5, 5, '5.png'),
    ('user6@example.com', MD5('password6'), '2023-06-06', 'Bio for User 6', 6, 6, '6.png'),
    ('user7@example.com', MD5('password7'), '2023-07-07', 'Bio for User 7', 7, 7, '7.png'),
    ('user8@example.com', MD5('password8'), '2023-08-08', 'Bio for User 8', 1, 8, '8.png'),
    ('user9@example.com', MD5('password9'), '2023-09-09', 'Bio for User 9', 2, 9, '9.png'),
    ('user10@example.com', MD5('password10'), '2023-10-10', 'Bio for User 10', 3, 10, '10.png'),
    ('user11@example.com', MD5('password11'), '2023-11-11', 'Bio for User 11', 4, 11, '11.png'),
    ('user12@example.com', MD5('password12'), '2023-12-12', 'Bio for User 12', 5, 12, '12.png'),
    ('user13@example.com', MD5('password13'), '2024-01-01', 'Bio for User 13', 6, 13, '13.png');


create table bookmarks(
    id serial primary key,
    user_edition_id int references user_edition(id),
    page int
);
INSERT INTO bookmarks (user_edition_id, page)
VALUES
    (1, 10),
    (2, 20),
    (3, 30),
    (4, 40),
    (5, 50),
    (6, 60),
    (7, 70);

create table status(
    id serial primary key,
    status varchar(32)
);
INSERT INTO status (status)
VALUES
    ('Reading'),
    ('To Read'),
    ('Completed'),
    ('Paused'),
    ('Abandoned'),
    ('Reviewing'),
    ('Planning');

create table book_status(
    id serial primary key,
    user_edition_id int references user_edition(id),
    status_id int references status(id)
);
insert into book_status (user_edition_id, status_id)
values
    (4, 1),
    (1, 2),
    (6, 3),
    (7, 4),
    (11, 5),
    (2, 6),
    (9, 7);

create table roles(
    id serial primary key,
    role varchar(32)
);
insert into roles (role)
values
    ('Admin'),
    ('Moderator');

create table users_roles(
    id serial primary key,
    user_id int references users(id),
    role_id int references roles(id)
);
insert into users_roles (user_id, role_id)
values
    (1, 1),
    (2, 2);
