# Транскрипция аудио с помощью Whisper + Flask + PostgreSQL

## 📋 Описание

Это веб-приложение на Flask, которое позволяет загружать аудиофайлы и получать их текстовую расшифровку.  
Текст сохраняется в PostgreSQL, и может быть просмотрен и скачан через веб-интерфейс.

---

## 🚀 Быстрый запуск (локально)

### 1. Клонируй репозиторий

```bash
git clone https://github.com/your-username/project_transcribe.git
cd project_transcribe 
```
### 2. Установка зависимостей
- Создай и активируй виртуальное окружение:

``` bash
python3 -m venv venv
source venv/bin/activate  # или .\venv\Scripts\activate на Windows
```
- Установи зависимости:

```bash
pip install -r requirements.txt
```
### 3. Установка и настройка PostgreSQL
- Установи PostgreSQL (если ещё не установлен):

``` bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```
- Создай пользователя и базу данных:

``` bash
sudo -u postgres psql
```

- В интерактивной консоли psql:

``` sql
CREATE USER admin WITH PASSWORD 'yourpassword' SUPERUSER;
CREATE DATABASE transcribe_db OWNER admin;
\q
```

#### Дополнительная настройка для удалённого доступа и нестандартного порта  
Если планируешь подключаться к базе данных удалённо или используешь нестандартный порт (например, 5433 вместо стандартного 5432), нужно сделать следующие шаги:

1) Измени конфигурацию PostgreSQL

Открой файл postgresql.conf (обычно в /etc/postgresql/<версия>/main/postgresql.conf) и установи:

``` conf
listen_addresses = '*'
port = 5433  # или твой выбранный порт
```

2) Настрой правила доступа

Открой файл pg_hba.conf (обычно в той же директории) и добавь строку, разрешающую доступ:

``` conf
host    all             all             0.0.0.0/0               md5
```

3) Перезапусти сервис PostgreSQL

``` bash
sudo systemctl restart postgresql
```

4) Открой порт в файерволе (если активен)

``` bash
sudo ufw allow 5433/tcp
```
При подключении через pgAdmin или другой клиент укажи порт 5433 (или используемый тобой).


### 4. Настрой конфигурацию
Создай файл config.py в корне проекта и добавь строку подключения, укажи правильный порт:

```python 
DB_URL = "postgresql://admin:yourpassword@yourlocalip:5433/transcribe_db"
```

Чтобы узнать IP-адрес ноутбука в локальной сети выполни:
``` bash
ip a
```
или

``` bash
hostname -I
```

### 5. Запусти сервер
``` bash
gunicorn app:app --bind 192.168.0.103:5000 --workers 4 # для многопоточности
```

``` bash
flask run --host=192.168.0.103 --port=5000 # один поток
```

(заменить на айпи устройства в локальной сети)

Приложение будет доступно на http://192.168.0.103:5000

## 📂 Структура проекта
``` csharp
project_transcribe/
├── app.py
├── config.py
├── db.py
├── requirements.txt
├── templates/
│   ├── index.html
│   ├── history.html
│   └── view_transcript.html
├── static/
│   └── styles.css
├── uploads/               # создаётся автоматически
├── transcripts/           # создаётся автоматически
└── venv/                  # виртуальное окружение
```