from flask import Flask, request, jsonify
from googletrans import Translator

app = Flask(__name__)
# Явная поддержка UTF-8 для JSON
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

# Инициализация переводчика (как в твоём Jupyter скрипте)
translator = Translator()

# --- КОРНЕВОЙ МАРШРУТ (ДЛЯ ПРОВЕРКИ) ---
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'online',
        'message': 'Godot Translator Backend (googletrans 4.0.0-rc1) is running!',
        'library': 'googletrans==4.0.0-rc1 (same as Jupyter)',
        'endpoints': ['/translate'],
        'example': {
            'url': '/translate',
            'method': 'POST',
            'body': {
                'text': 'tere',
                'src': 'et',
                'dest': 'ru'
            }
        }
    }), 200

# --- ЭНДПОИНТ ДЛЯ ПЕРЕВОДА ---
@app.route('/translate', methods=['POST'])
def translate_text():
    # 1. Получаем данные из POST-запроса с явной поддержкой UTF-8
    try:
        data = request.get_json(force=True)
    except:
        # Если не получилось распарсить JSON, пробуем вручную
        raw_data = request.get_data(as_text=True)
        import json
        data = json.loads(raw_data)
    
    # Проверка обязательных полей
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing "text" parameter'}), 400

    text_to_translate = data.get('text', '')
    
    # Явно гарантируем UTF-8
    if isinstance(text_to_translate, bytes):
        text_to_translate = text_to_translate.decode('utf-8')
    
    src_lang = data.get('src', 'et') # Язык по умолчанию: эстонский
    dest_lang = data.get('dest', 'ru') # Язык по умолчанию: русский
    
    # Отладка: логируем полученный текст (для проверки UTF-8)
    print(f"[DEBUG] Received text: '{text_to_translate}' (len={len(text_to_translate)})")
    print(f"[DEBUG] UTF-8 bytes: {text_to_translate.encode('utf-8')}")
    
    try:
        # 2. Выполняем перевод (ТОЧНО КАК В JUPYTER СКРИПТЕ)
        translation = translator.translate(text_to_translate, src=src_lang, dest=dest_lang)
        
        # 3. Возвращаем результат в формате JSON
        return jsonify({
            'original_text': translation.origin,
            'translated_text': translation.text,
            'source_language': translation.src,
            'target_language': translation.dest
        }), 200

    except Exception as e:
        # 4. Обработка ошибок перевода
        return jsonify({'error': 'Translation failed', 'details': str(e)}), 500

# Запуск сервера локально (для тестирования)
if __name__ == '__main__':
    # В проде (Render/Heroku) gunicorn будет запускать приложение
    # Для локального теста:
    app.run(debug=True)