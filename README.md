# Food Recognition API

Микросервисное приложение для распознавания еды по изображению и подбора рецептов на основе найденных ингредиентов.

Пользователь загружает изображение с продуктами, система определяет ингредиенты, подбирает подходящие рецепты и автоматически переводит их на русский язык.

---

# Demo

Проект доступен по ссылке:

https://food-recognition.tailaaac65.ts.net/

Swagger документация:

https://food-recognition.tailaaac65.ts.net/docs

---

# Функциональность

- загрузка изображения с продуктами;
- распознавание ингредиентов с помощью ML-сервиса;
- подбор рецептов по найденным ингредиентам;
- отображение недостающих ингредиентов;
- получение пошаговых инструкций приготовления;
- автоматический перевод рецептов на русский язык;
- health-check для проверки доступности сервисов;
- запуск всей системы через Docker Compose.

---

# Архитектура проекта

Проект реализован в виде микросервисной архитектуры.

## Сервисы

- `frontend` — пользовательский интерфейс;
- `api-service` — основной REST API и orchestration layer;
- `ml-service` — распознавание ингредиентов по изображению;
- `recipe-service` — подбор рецептов;
- `translate-service` — перевод рецептов на русский язык.

---

## Структура проекта

```text
food-recognition-api/
├── api-service/
├── ml-service/
├── recipe-service/
├── translate-service/
├── frontend/
├── docker-compose.yml
├── README.md
└── .pre-commit-config.yaml
```

## Переменные окружения

## recipe-service/.env

```env
SPOONACULAR_API_KEY=your_key_here
SPOONACULAR_BASE_URL=https://api.spoonacular.com
```

## ml-service/.env

```env
GROQ_API_KEY=your_key_here
```

## translate-service/.env

```env
GROQ_API_KEY=your_key_here
```

## api-service/.env

```env
ML_SERVICE_URL=http://ml-service:8001
RECIPE_SERVICE_URL=http://recipe-service:8002
TRANSLATE_SERVICE_URL=http://translate-service:8003
MAX_IMAGE_SIZE_MB=10
```

---

# Локальный запуск проекта

## 1. Клонирование репозитория

```bash
git clone https://github.com/alenchesss/food-recognition-api.git
cd food-recognition-api
```

## 2. Создание .env файлов

Создайте `.env` файлы для каждого сервиса.

## 3. Запуск проекта

```bash
docker compose up --build
```

---

# Доступные сервисы

После запуска будут доступны:

| Сервис   | Адрес                                                    |
| -------- | -------------------------------------------------------- |
| Frontend | [http://localhost:5173](http://localhost:5173)           |
| API      | [http://localhost:8000](http://localhost:8000)           |
| Swagger  | [http://localhost:8000/docs](http://localhost:8000/docs) |

---

# Пример работы системы

1. Пользователь загружает изображение.
2. `api-service` проверяет тип и размер файла.
3. Изображение отправляется в `ml-service`.
4. `ml-service` распознаёт ингредиенты.
5. Список ингредиентов передаётся в `recipe-service`.
6. `recipe-service` подбирает рецепты.
7. `translate-service` переводит рецепты на русский язык.
8. Пользователь получает готовый результат.

---

# Обработка ошибок

Система поддерживает обработку следующих ошибок:

* неверный формат изображения;
* превышение размера файла;
* недоступность ML-сервиса;
* недоступность сервиса рецептов;
* ошибки внешних API;
* ошибки перевода;
* ошибки валидации данных.

---

# Deployment

Проект развёрнут в Kubernetes-кластере.

Используются:

* Docker containers;
* Kubernetes;
* Ingress NGINX;
* автоматическое обновление сервисов;
* микросервисная архитектура.

---

# Авторы

* Степаненко Алёна
* Подкалюк Анна
