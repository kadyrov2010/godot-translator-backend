import sys
# Принудительное использование кодировки UTF-8 для стандартного ввода/вывода (stdin/stdout)
# Это исправляет проблемы с Gunicorn, который по умолчанию использует latin-1
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

from app import app as application

if __name__ == "__main__":
    application.run()