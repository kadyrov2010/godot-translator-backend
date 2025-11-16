# Godot Translator Backend

Простой Flask-сервер для перевода текста с использованием `googletrans==4.0.0-rc1`.

**Преимущества:**
- ✅ Переводит **слова И фразы**
- ✅ Та же библиотека, что в Jupyter (проверено!)
- ✅ Без лимитов API ключа
- ✅ Бесплатно

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

### Примеры использования:

**Одно слово:**
```json
POST /translate
{
  "text": "kass",
  "src": "et",
  "dest": "ru"
}
→ "кошка"
```

**Фраза:**
```json
POST /translate
{
  "text": "ma lähen koju",
  "src": "et",
  "dest": "ru"
}
→ "я иду домой"
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

