from flask import Flask, request, jsonify
from googletrans import Translator

app = Flask(__name__)
# Инициализация переводчика
translator = Translator()

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
        # 2. Выполняем перевод с помощью py-googletrans
        translation = translator.translate(
            text_to_translate, 
            src=src_lang, 
            dest=dest_lang
        )
        
        # 3. Возвращаем результат в формате JSON
        return jsonify({
            'original_text': text_to_translate,
            'translated_text': translation.text,
            'source_language': translation.src,
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