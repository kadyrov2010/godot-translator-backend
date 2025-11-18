from flask import Flask, request, jsonify, send_file
from googletrans import Translator
from gtts import gTTS  # Импортируем gTTS для озвучки
import io  # Импортируем для работы с байтами в памяти
import json  # Добавьте импорт для ручного парсинга

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

# --- ЭНДПОИНТ ДЛЯ ОЗВУЧКИ (gTTS) ---
@app.route('/speak', methods=['POST'])
def speak_text():
    # 1. ЧИТАЕМ СЫРЫЕ БАЙТЫ ТЕЛА ЗАПРОСА
    try:
        raw_data = request.data
        data = json.loads(raw_data.decode('utf-8'))
    except Exception as e:
        print(f"[ERROR] Failed to decode/parse JSON in /speak: {e}")
        return jsonify({'error': 'Invalid JSON or empty request body', 'details': str(e)}), 400
    
    # Проверка обязательных полей
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing "text" parameter'}), 400
    
    text_to_speak = data.get('text', '')
    # Используем 'et' (эстонский) для озвучки по умолчанию
    lang = data.get('lang', 'et')
    
    print(f"[DEBUG] TTS request: text='{text_to_speak}', lang='{lang}'")
    
    try:
        # 2. Генерируем аудио в памяти
        tts = gTTS(text=text_to_speak, lang=lang, slow=False)
        
        # Используем BytesIO для сохранения MP3 в оперативную память
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)  # Переводим указатель в начало файла
        
        # 3. Отправляем аудиофайл обратно в Godot
        return send_file(
            mp3_fp,
            mimetype='audio/mpeg',
            as_attachment=False,  # Отправляем как прямое содержимое
            download_name='translation_audio.mp3'
        )
    except Exception as e:
        # Обработка ошибок gTTS
        print(f"[ERROR] TTS generation failed: {e}")
        return jsonify({
            'error': 'TTS generation failed',
            'details': str(e)
        }), 500

# ... (Оставьте запуск if __name__ == '__main__')