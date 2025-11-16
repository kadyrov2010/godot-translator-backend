from flask import Flask, request, jsonify
from googletrans import Translator
import json # Добавьте импорт для ручного парсинга

app = Flask(__name__)
# Убедитесь, что эта конфигурация осталась
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

translator = Translator()

# ... (Оставьте корневой маршрут '/')

# --- ЭНДПОИНТ ДЛЯ ПЕРЕВОДА ---
@app.route('/translate', methods=['POST'])
def translate_text():
    
    # 1. ЧИТАЕМ СЫРЫЕ БАЙТЫ ТЕЛА ЗАПРОСА
    try:
        raw_data = request.data
        
        # 2. ВРУЧНУЮ ДЕКОДИРУЕМ В UTF-8 И ПАРСИМ JSON
        # Если body пустое или равно None, это вызовет ошибку, 
        # поэтому обрабатываем это внутри try/except.
        data = json.loads(raw_data.decode('utf-8')) 
        
    except Exception as e:
        # Эта ошибка 400 возникает, если Godot отправил пустые или невалидные байты
        print(f"[ERROR] Failed to decode/parse JSON: {e}")
        return jsonify({'error': 'Invalid JSON or empty request body', 'details': str(e)}), 400

    # Проверка обязательных полей
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing "text" parameter'}), 400

    text_to_translate = data.get('text', '')
    src_lang = data.get('src', 'et') 
    dest_lang = data.get('dest', 'ru')
    
    # Отладка:
    print(f"[DEBUG] Received text (Decoded): '{text_to_translate}'")
    
    try:
        # 3. Выполняем перевод
        translation = translator.translate(text_to_translate, src=src_lang, dest=dest_lang)
        
        # 4. Возвращаем результат
        return jsonify({
            'original_text': translation.origin,
            'translated_text': translation.text,
            'source_language': translation.src,
            'target_language': translation.dest
        }), 200

    except Exception as e:
        # 5. Обработка ошибок
        return jsonify({
            'error': 'Translation failed', 
            'details': str(e)
        }), 500

# ... (Оставьте запуск if __name__ == '__main__')