# 🚀 Deployment Instructions

## 📦 Что изменено:

### 1. **Procfile** (новый файл)
Оптимизированная команда запуска Gunicorn:
```bash
gunicorn app:app \
  --workers 2          # 2 процесса (оптимально для 0.1 CPU)
  --threads 3          # 3 потока на worker = 6 concurrent requests
  --worker-class gthread  # Потоки для I/O операций
  --timeout 30         # Таймаут 30 сек (не 40)
  --max-requests 500   # Перезапуск worker после 500 запросов
  --max-requests-jitter 50  # Случайное отклонение
```

### 2. **app.py** — In-Memory кеш
Добавлен кеш для переводов:
- **Google Translate**: кеширует все переводы
- **Gemini API**: кеширует все ответы
- **Лимит**: 2000 записей (~200KB RAM)
- **Очистка**: FIFO (удаляет самые старые)

---

## 🔧 Деплой на Render:

### Шаг 1: Push изменений в Git
```bash
cd godot-translator-backend
git add .
git commit -m "Optimize Gunicorn config + add in-memory cache"
git push
```

### Шаг 2: Render автоматически пересоберёт сервис
- Render обнаружит новый `Procfile`
- Автоматически применит новую конфигурацию
- Перезапустит сервис с 2 workers

### Шаг 3: Проверка логов
После деплоя проверьте логи Render:
```
[INFO] Gemini API key loaded successfully
[INFO] Booting worker with pid: XXXX (worker 1)
[INFO] Booting worker with pid: YYYY (worker 2)
```

---

## 📊 Ожидаемые результаты:

| Метрика | До | После |
|---------|-----|-------|
| **Workers** | 4 | 2 |
| **Threads** | - | 3 на worker |
| **Concurrent requests** | 4 | 6 (2×3) |
| **RAM usage** | ~250 MB | ~150 MB |
| **CPU load** | Высокая | Низкая |
| **Cache hits** | 0% | 30-50% (популярные слова) |
| **Response time** (cached) | 1-3 сек | **0.01 сек** ⚡ |

---

## ✅ Проверка работы кеша:

### В логах Render появится:
```
[CACHE MISS] Translating: 'hello'
[CACHE HIT] Returning cached translation for: 'hello'
[CACHE MISS] Gemini request: 'translate this...'
[CACHE HIT] Returning cached Gemini response for: 'translate this...'
```

---

## 🐛 Возможные проблемы:

### Проблема 1: Render не применил Procfile
**Решение:**
1. Зайдите в Settings → Build & Deploy
2. Убедитесь, что **Build Command** пустое или стандартное
3. **Start Command** должно быть пустым (Render читает Procfile автоматически)

### Проблема 2: Ошибка "No module named 'app'"
**Решение:**
- Убедитесь, что `app.py` находится в корне репозитория
- В Procfile используется `app:app` (файл:переменная Flask)

---

## 📈 Мониторинг:

Следите за метриками в Render Dashboard:
- **CPU usage**: должна быть < 80%
- **Memory usage**: должна быть < 400 MB
- **Response time**: < 2 сек для некешированных запросов

---

## 🔄 Откат изменений (если что-то пошло не так):

```bash
git revert HEAD
git push
```

Render автоматически откатится к предыдущей версии.
