from flask import Flask, request, jsonify, send_file
from googletrans import Translator
from gtts import gTTS  # Импортируем gTTS для озвучки
import io  # Импортируем для работы с байтами в памяти
import json  # Добавьте импорт для ручного парсинга
import os  # Для переменных окружения
import requests  # Для запросов к Gemini API

app = Flask(__name__)
# Убедитесь, что эта конфигурация осталась
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

translator = Translator()

# ============================================
# IN-MEMORY КЕШ ДЛЯ ПЕРЕВОДОВ
# ============================================
TRANSLATION_CACHE = {}
MAX_CACHE_SIZE = 2000  # Макс 2000 переводов (~200KB RAM)

def get_cache_key(text: str, src: str, dest: str) -> str:
    """Создаёт уникальный ключ для кеша"""
    return f"{src}:{dest}:{text.lower().strip()}"

def get_cached_translation(cache_key: str):
    """Получает перевод из кеша"""
    return TRANSLATION_CACHE.get(cache_key)

def save_to_cache(cache_key: str, result: dict):
    """Сохраняет перевод в кеш с FIFO очисткой"""
    if len(TRANSLATION_CACHE) >= MAX_CACHE_SIZE:
        # Удаляем самую старую запись (первую добавленную)
        TRANSLATION_CACHE.pop(next(iter(TRANSLATION_CACHE)))
    TRANSLATION_CACHE[cache_key] = result

# ============================================
# GEMINI API PROXY (защищает API ключ)
# ============================================
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# Проверяем загрузку ключа при старте
if GEMINI_API_KEY:
    print(f"[INFO] Gemini API key loaded successfully")
else:
    print("[WARNING] GEMINI_API_KEY not found in environment!")

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
    
    # === ПРОВЕРКА КЕША ===
    cache_key = get_cache_key(text_to_translate, src_lang, dest_lang)
    cached_result = get_cached_translation(cache_key)
    
    if cached_result:
        print(f"[CACHE HIT] Returning cached translation for: '{text_to_translate}'")
        return jsonify(cached_result), 200
    
    # Отладка:
    print(f"[CACHE MISS] Translating: '{text_to_translate}'")
    
    try:
        # 3. Выполняем перевод
        translation = translator.translate(text_to_translate, src=src_lang, dest=dest_lang)
        
        # 4. Формируем результат
        result = {
            'original_text': translation.origin,
            'translated_text': translation.text,
            'source_language': translation.src,
            'target_language': translation.dest
        }
        
        # 5. Сохраняем в кеш
        save_to_cache(cache_key, result)
        
        # 6. Возвращаем результат
        return jsonify(result), 200

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

# ============================================
# ЭНДПОИНТ ДЛЯ GEMINI API (через proxy)
# ============================================
@app.route('/api/gemini', methods=['POST'])
def gemini_proxy():
    """
    Proxy для Gemini API - защищает API ключ от декомпиляции
    """
    try:
        # 1. Читаем данные от Godot
        raw_data = request.data
        data = json.loads(raw_data.decode('utf-8'))
        
        # 2. Валидация обязательных полей
        if not data or 'model' not in data or 'contents' not in data:
            return jsonify({'error': 'Missing required fields (model, contents)'}), 400
        
        # 3. Проверяем наличие API ключа
        if not GEMINI_API_KEY:
            print(f"[ERROR] GEMINI_API_KEY is empty!")
            return jsonify({'error': 'Server configuration error: API key not set'}), 500
        
        # 4. Формируем URL к Gemini API
        model = data.get('model', 'gemini-2.5-flash')
        gemini_url = f"{GEMINI_BASE_URL}/{model}:generateContent?key={GEMINI_API_KEY}"
        
        # === ПРОВЕРКА КЕША ДЛЯ GEMINI ===
        # Извлекаем текст из contents для ключа кеша
        request_text = ""
        gemini_cache_key = ""
        contents = data.get('contents', [])
        if contents and len(contents) > 0:
            parts = contents[0].get('parts', [])
            if parts and len(parts) > 0:
                request_text = parts[0].get('text', '')
                # Используем model как "src" для уникальности
                gemini_cache_key = get_cache_key(request_text, model, "gemini")
                cached_gemini = get_cached_translation(gemini_cache_key)
                
                if cached_gemini:
                    print(f"[CACHE HIT] Returning cached Gemini response for: '{request_text[:50]}...'")
                    return jsonify(cached_gemini), 200
                
                print(f"[CACHE MISS] Gemini request: '{request_text[:50]}...'")
        
        # 5. Подготавливаем payload для Gemini
        payload = {
            'contents': data['contents']
        }
        
        # Добавляем опциональные параметры если есть
        if 'generationConfig' in data:
            payload['generationConfig'] = data['generationConfig']
        if 'systemInstruction' in data:
            payload['systemInstruction'] = data['systemInstruction']
        
        # 6. Отправляем запрос к Gemini API
        response = requests.post(
            gemini_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        # 7. Проверяем статус ответа
        if response.status_code != 200:
            print(f"[ERROR] Gemini API error: {response.status_code}")
            print(f"[ERROR] Response body: {response.text}")
            
            # Специальная обработка 403 (Forbidden)
            if response.status_code == 403:
                print(f"[ERROR] 403 Forbidden - check API key validity and restrictions")
            
            return jsonify({
                'error': 'Gemini API error',
                'status_code': response.status_code,
                'details': response.text
            }), response.status_code
        
        # 8. Сохраняем в кеш и возвращаем результат
        gemini_result = response.json()
        if request_text and gemini_cache_key:
            save_to_cache(gemini_cache_key, gemini_result)
        
        return jsonify(gemini_result), 200
        
    except requests.Timeout:
        print(f"[ERROR] Gemini request timed out")
        return jsonify({'error': 'Request timed out (15 sec)'}), 504
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON from client: {e}")
        return jsonify({'error': 'Invalid JSON', 'details': str(e)}), 400
        
    except Exception as e:
        print(f"[ERROR] Gemini proxy failed: {e}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

# ... (Оставьте запуск if __name__ == '__main__')