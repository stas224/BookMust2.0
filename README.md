# launch:
```sh
git clone https://github.com/stas224/BookMust2.0.git
brew install pkg-config libvirt
python3 -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
/usr/bin/bash ./postgres_init.sh
localstack start --host
```
## todo-list:
- [x] Придумать тему 
- [x] Организовать отношения в реляционной базе данных
- [ ] личный кабинет
- [x] авторизация
- [x] поиск
- [x] s3 connector
- [ ] key-value

- [ ] логика добавления книги в коллекцию пользователя
- [ ] логика добавления книги в пул
- [ ] логика изменения/удаления статусов книги в коллекции пользователя
- [ ] логика изменения/добавления книги в пуле

- [ ] Топы
- [ ] Подборки
- [ ] Статистика

## sql-schema:
![sql-schema.jpg](media/sql-schema.jpg)


### book-details:
![book-details.png](media/book-details.png)

### top-editions:
![top-editions.png](media/top-editions.png)