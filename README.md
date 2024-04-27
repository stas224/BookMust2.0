# launch:
```sh
git clone https://github.com/stas224/BookMust2.0.git
brew install pkg-config libvirt
python3 -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
/usr/bin/bash ./postgres_init.sh
/usr/bin/bash ./redis_init.sh
localstack start --host
```

## sql-schema:
![sql-schema.jpg](media/sql-schema.jpg)

## index page:
![top-editions.jpg](media/top-editions.jpg)

## collection page:
![book-details.jpg](media/book-details.jpg)
