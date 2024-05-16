# DataEngineering

### Info

* **Docker command for setting up connections** 
```docker
    docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v x:/Learnings/Data\ Engineering/DE_Zoomcamp/Week\ 1/2_DOCKER_SQL/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
    postgres:13
```

* **pgcli** is used for accessing the database and run queris  
* **5432** is the standard port from postgres  
* pgcli -h localhost -p 5432 -u root -d ny_taxi --> connecting to db

* **Docker command for setting up pgadmin** 
```docker
    docker run -it \
    -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
    -e PGADMIN_DEFAULT_PASSWORD="root" \
    -p 8080:80 \
    dpage/pgadmin4
``` 
    

### Describe tabel im pgcli  
    *\d yello_taxi_data;