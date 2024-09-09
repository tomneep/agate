docker volume create --name postgres_data

docker run --name my_postgres_container -d -p 5432:5432 -e POSTGRES_PASSWORD=db_password_ljg_aj -e POSTGRES_USER=db_user -e POSTGRES_DB=db_nane  -v postgres_data:/var/lib/postgresql/data  postgres:13-alpine