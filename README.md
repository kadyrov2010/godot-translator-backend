# Godot Translator Backend

Простой Flask-сервер для перевода текста с использованием `py-googletrans`.

## API Endpoint

**POST** `/translate`

### Параметры запроса (JSON):
```json
{
  "text": "tere",
  "src": "et",
  "dest": "ru"
}
```

### Пример ответа:
```json
{
  "original_text": "tere",
  "translated_text": "привет",
  "source_language": "et",
  "target_language": "ru"
}
```

## Развертывание на Render

1. Подключить GitHub репозиторий
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `gunicorn app:app`
4. **Environment:** Python 3

## Локальный запуск

```bash
python app.py
```

Сервер запустится на `http://localhost:5000`

