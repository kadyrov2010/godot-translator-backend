from flask import Flask, request, jsonify
from deep_translator import GoogleTranslator

app = Flask(__name__)

# --- КОРНЕВОЙ МАРШРУТ (ДЛЯ ПРОВЕРКИ) ---
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'online',
        'message': 'Godot Translator Backend (deep-translator) is running!',
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
    data = request.get_json()
    
    # Проверка обязательных полей
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing "text" parameter'}), 400

    text_to_translate = data.get('text', '')
    src_lang = data.get('src', 'et') # Язык по умолчанию: эстонский
    dest_lang = data.get('dest', 'ru') # Язык по умолчанию: русский
    
    try:
        # 2. Выполняем перевод с помощью deep-translator
        translated_text = GoogleTranslator(source=src_lang, target=dest_lang).translate(text_to_translate)
        
        # 3. Возвращаем результат в формате JSON
        return jsonify({
            'original_text': text_to_translate,
            'translated_text': translated_text,
            'source_language': src_lang,
            'target_language': dest_lang
        }), 200

    except Exception as e:
        # 4. Обработка ошибок перевода
        return jsonify({'error': 'Translation failed', 'details': str(e)}), 500

# Запуск сервера локально (для тестирования)
if __name__ == '__main__':
    # В проде (Render/Heroku) gunicorn будет запускать приложение
    # Для локального теста:
    app.run(debug=True)