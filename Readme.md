Вопросы по ревью:
Когда захожу через 80 порт (nginx),  то api выдает ошибку.
При этом если запустить локально через 8100, то запрос возвращает корректные данныею

<html>
<head><title>404 Not Found</title></head>
<body>
<center><h1>404 Not Found</h1></center>
<hr><center>nginx</center>
</body>
</html>
____

Запуск приложения:
`docker-compose up --build`

Список переменных окружения:
.env.example

[Документация по OpenApi](http://127.0.0.1:80/api/openapi )
