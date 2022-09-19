# py-flask-redis-postgres Flask application з redis та postgres





## Запуск локально в режимі PROD

Запустити cmd

```bash
sh-composer-up-prod.cmd 
```

Сервіс буде доcnупний за адресою http://localhost:8081/



## Запуск локально в режимі PROD

Запустити cmd

```bash
sh-composer-up-debug.cmd 
```

Сервіс буде доcnупний за адресою http://localhost:8081/


Переключити visual studio code в режим debug і запустити **Sh-FLASK-Python: Remote Attach**



## Розроблені API

### Health check GET  /api/health

Використовується для перевірки працездатності сервісу

Повертає JSON

```json
{
  "success": true
}
```

# resoures

- https://stackoverflow.com/questions/43974888/run-script-after-container-entrypoint-in-docker-compose
How to execute script when posgres starts
our compose file then changes to something like this:

postgres:
  build: ./postgres
  volumes:
    - /shared_folder/postgresql:/var/lib/postgresql
    - ./db-init-scripts:/docker-entrypoint-initdb.d
  ports:
    - "5432:5432"

whereas a local directory, e.g. db-init-scripts, contains your initialization scripts (rename it if you want). Copy create_db.sh to this folder and it will be automatically executed when you create a new container.