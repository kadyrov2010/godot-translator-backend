import sys
# Принудительное использование UTF-8 для всех строковых операций
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

from flask import Flask, request, jsonify
from googletrans import Translator

app = Flask(__name__)
# Явная поддержка UTF-8 для JSON
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

# Инициализация переводчика
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
    # 1. Получаем данные из POST-запроса
    data = request.get_json(force=True)
    
    # Проверка обязательных полей
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing "text" parameter'}), 400

    text_to_translate = data.get('text', '')
    src_lang = data.get('src', 'et')
    dest_lang = data.get('dest', 'ru')
    
    try:
        # 2. Выполняем перевод (как в Jupyter)
        translation = translator.translate(text_to_translate, src=src_lang, dest=dest_lang)
        
        # 3. Возвращаем результат
        return jsonify({
            'original_text': translation.origin,
            'translated_text': translation.text,
            'source_language': translation.src,
            'target_language': translation.dest
        }), 200

    except Exception as e:
        # 4. Обработка ошибок
        return jsonify({
            'error': 'Translation failed', 
            'details': str(e)
        }), 500

# Запуск сервера локально (для тестирования)
if __name__ == '__main__':
    # В проде (Render/Heroku) gunicorn будет запускать приложение
    # Для локального теста:
    app.run(debug=True)