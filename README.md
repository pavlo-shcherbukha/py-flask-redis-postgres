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

### Отримати всі ключі в БД GET api/key

Повертає перелік всіх ключів в БД redis у вигляді масиву:

- Запит

   без параметрів

- Обов'язкові заголовки http в запиті

```text

    content-type: application/json

```

- Відповідь

```json
{
  "list": ["shhkey2", "shkey1", "APICALLS", "book1", "myhash", "jsondata", "get", "test1", "counter", "xcntr", "sh-book","gey"]
}

```

### Створити новий ключ та значення в БД POST api/key

- Запит

- Обов'язкові заголовки http в запиті

```text

    content-type: application/json


```json
{"keyname": "xkey1", "keyvalue": "xkeyvalue"}

```

- Успішна відповідь

```json
{
  "redis_result": true
}

```