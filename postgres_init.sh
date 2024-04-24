docker pull postgres && \
docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -e \
  POSTGRES_USER=myuser -e POSTGRES_DB=mydb -p 5432:5432 \
  -v ./init_db.sql:/docker-entrypoint-initdb.d/init_db.sql --rm postgres
