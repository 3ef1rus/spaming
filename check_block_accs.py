import asyncio
import os
from pyrogram import Client
import sqlite3
import pyrogram


# Создание подключения к базе данных
conn = sqlite3.connect('accounts.db')
cur = conn.cursor()
api_id = 12010295
api_hash = 'd9680b7ed54f9b8b48e7c71deb136a33'
# Получение списка номеров телефонов из базы данных
cur.execute(
    "SELECT phone_number FROM accounts_auth WHERE Error = 1 OR spam_block= 'Yes' ")
phone_numbers = [row[0] for row in cur.fetchall()]
# Создание клиента
clients = []
user_ids = []
with open("message.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Разделение текста на абзацы по символу "\"
messages = text.split("\\")

for phone_number in phone_numbers:
    ses_name = f"session_+{phone_number}"
    clients.append(Client(ses_name, api_id, api_hash,
                   phone_number=phone_number))
# Получение списка user_id из базы данных
cur.execute("SELECT username FROM members_info")
usernames = [row[0] for row in cur.fetchall()]


async def check_spam_block(client):
    try:
        # Проверяем, имеется ли спам-блокировка
        await client.send_message("failopk", "test")
        print(f"Аккаунт {client.phone_number} не имеет заморозки.")
        cur.execute(
            "UPDATE accounts_auth SET Error = ? WHERE phone_number = ?", (0, client.phone_number))
        conn.commit()
        cur.execute("UPDATE accounts_auth SET spam_block = ? WHERE phone_number = ?",
                    ('No', client.phone_number))
        conn.commit()
        return False
    except pyrogram.errors.exceptions.flood_420.FloodWait as e:
        print(f"Аккаунт {client.phone_number} заморожен на {e.value} секунд.")
        return True
    except pyrogram.errors.exceptions.bad_request_400.PeerFlood:
        print(
            f"Аккаунт {client.phone_number} не может отправлять сообщения другим пользователям из-за флуда.")
        cur.execute("UPDATE accounts_auth SET spam_block = ? WHERE phone_number = ?",
                    ('Yes', client.phone_number))
        conn.commit()
        cur.execute(
            "UPDATE accounts_auth SET Error = ? WHERE phone_number = ?", (0, client.phone_number))
        conn.commit()
        return True
    except Exception as e:
        print(f"Произошла ошибка при проверке заморозки аккаунта: {e}")
        return False


async def start_client(client):
    try:
        if not client.is_initialized:
            await client.start()
    except pyrogram.errors.exceptions.unauthorized_401.UserDeactivatedBan:
        print(f"Аккаунт {client.phone_number} удален или деактивирован.")
        cur.execute(
            "SELECT ses_name FROM accounts_auth WHERE phone_number = ?", (client.phone_number,))
        ses_name = [row[0] for row in cur.fetchall()]
        file = ses_name[0]
        os.remove(f"{file}.session")
        cur.execute(
            "DELETE FROM accounts_auth WHERE phone_number = ?", (client.phone_number,))
        ses_name = cur.fetchall()
        conn.commit()
        return True


async def run_clients():
    # Запуск всех клиентов
    start_tasks = [start_client(client) for client in clients]
    await asyncio.gather(*start_tasks)

    # выполнение функции на всех клиентах
    message_tasks = []
    for client in clients:
        message_tasks.append(check_spam_block(client))

    await asyncio.gather(*message_tasks)
    stop_tasks = []
    # Остановка всех клиентов после отправки сообщений
    for client in clients:
        if client.is_initialized:
            stop_tasks.append(client.stop())
    await asyncio.gather(*stop_tasks)

# Получаем event loop
loop = asyncio.get_event_loop()

# Запускаем функцию run_clients в текущем event loop
loop.run_until_complete(run_clients())
cur.close()
conn.close()
print("Проверка завершина")
print("Нажмите Enter для завершения программы...")
input()
