# launch:
```sh
git clone https://github.com/stas224/BookMust2.0.git
python3 -m venv venv
pip install -r requirements.txt
docker pull postgres
/usr/bin/bash ./postgres_init.sh
```
## todo-list:
- [x] Придумать тему 
- [x] Организовать отношения в реляционной базе данных
- [ ] личный кабинет
- [ ] авторизация
- [ ] поиск
- [ ] s3 connector
- [ ] key-value
- [ ] логика добавления

## sql-schema:
![sql-schema.jpg](media/sql-schema.jpg)


### book-details:
![book-details.png](media/book-details.png)

### top-editions:
![top-editions.png](media/top-editions.png)