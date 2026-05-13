# Food Recognition — фронт

React + Vite + Framer Motion. Палитра muted-bordeaux, серьёзная типографика, оригинальная SVG-анимация загрузки.

## Установка

```bash
cd frontend
npm install
```

## Запуск (dev)

Убедитесь, что **api-service** запущен на `http://127.0.0.1:8000`. Затем:

```bash
npm run dev
```

Откроется на `http://localhost:5173`.

## Прод-сборка

```bash
npm run build
npm run preview
```

## Конфигурация

Адрес бэкенда можно поменять через `.env`:

```
VITE_API_BASE=http://127.0.0.1:8000
```

По умолчанию — `http://127.0.0.1:8000`.

## Структура

```
src/
├── App.jsx              # роутинг между экранами
├── main.jsx             # точка входа
├── api/client.js        # fetch к /api/v1/recognize
├── styles/global.css    # дизайн-токены, CSS-переменные
└── components/
    ├── DropZone.jsx     # экран 1 — загрузка
    ├── CookingLoader.jsx # экран 2 — анимация
    ├── RecipeGrid.jsx   # экран 3 — карточки
    └── RecipeDetail.jsx # экран 4 — рецепт
```

## CORS

В `api-service/app/main.py` должны быть прописаны origins фронта (см. `api-service-main.py` в outputs). Если фронт запускается на другом порту — добавьте его в `allow_origins`.
