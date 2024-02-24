import os
import threading
from pyrogram import Client, errors
import sqlite3
import random
import aiosqlite
import asyncio
import nest_asyncio
nest_asyncio.apply()
# Создание подключения к базе данных
conn = sqlite3.connect('accounts.db')
cur = conn.cursor()
api_id = 12010295
api_hash = 'd9680b7ed54f9b8b48e7c71deb136a33'
# Получение списка номеров телефонов из базы данных
cur.execute(
    "SELECT phone_number FROM accounts_auth WHERE Error = 0 AND spam_block = 'No'")
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

cur.close()
conn.close()


async def select_from_db(select, table, condition='', elm=''):
    try:
        # Открытие соединения с базой данных
        async with aiosqlite.connect('accounts.db') as db:
            # Создание курсора
            async with db.cursor() as cursor:
                # Выполнение запроса
                if condition != '':
                    await cursor.execute(f"SELECT {select} FROM {table} WHERE {condition} = ?", (elm,))
                await cursor.execute(f"SELECT {select} FROM {table}")
                # Получение результатов
                rows = await cursor.fetchall()
                return rows
    except Exception as e:
        print(f"Произошла ошибка при выборе данных из БД: {e}")


async def delete_from_db(table, condition, elm):
    try:
        # Открытие соединения с базой данных
        async with aiosqlite.connect('accounts.db') as db:
            # Создание курсора
            async with db.cursor() as cursor:
                # Выполнение запроса
                await cursor.execute(f"DELETE FROM {table} WHERE {condition} = ?", (elm,))
                # Получение результатов
                await db.commit()
    except Exception as e:
        print(f"Произошла ошибка при удалении данных из БД: {e}")


async def update_from_db(table, value, condition='', elm=''):
    try:
        # Открытие соединения с базой данных
        async with aiosqlite.connect('accounts.db') as db:
            # Создание курсора
            async with db.cursor() as cursor:
                # Выполнение запроса
                await cursor.execute(f"UPDATE {table} SET {value}=? WHERE {condition} = ?", elm)
                # Получение результатов
                await db.commit()
    except Exception as e:
        print(f"Произошла ошибка при изменении данных из БД: {e}")


async def send_mess_more(client, username, message):

    await asyncio.sleep(round(random.uniform(2, 10), 3))

    try:

        await client.send_message(username, message)
        # print(f"{client.phone_number} отправил cообщение пользователю {username}")
        print(
            f"Поток {threading.current_thread().name} пользователь {client.phone_number} Сообщение отправлено пользователю {username}")

        # Обновление базы данных после успешной отправки сообщения
        await delete_from_db(table='members_info',
                             condition='username', elm=username)
        return True
    except errors.UsernameNotOccupied as e:

        print(f"Пользователь с ником {username} не найдет.")
        return True

    except errors.FloodWait as e:

        print(
            f"Аккаунт {client.phone_number} заморожен на {e.value+1} секунд.")
        x = e.value+1
        await asyncio.sleep(x)
        return True

    except errors.UserDeactivatedBan as e:

        print(f"Аккаунт {client.phone_number} удален или деактивирован.")
        ses_name = await select_from_db(select='ses_name', table='accounts_auth',
                                        condition='phone_number', elm=client.phone_number)
        file = ses_name[0]
        os.remove(f"{file}.session")
        return False

    except Exception as e:

        print(
            f"Аккаунт {client.phone_number} отправлен в заморозку с ошибкой :{e}")
        await update_from_db(table='accounts_auth', value='Error',
                             condition='phone_number', elm=(1, client.phone_number))
        return False


async def select_user_to_send(client, usernames, messages, count):
    await client.start()
    result = True
    for username in usernames[count:count+50]:
        while result == True:
            result = await send_mess_more(client, username, random.choice(messages))
            break


def start_select_user_to_send(client, usernames, messages, count):
    asyncio.run(select_user_to_send(client, usernames, messages, count))


i = 0
count = 0
threads = []
for client in clients:  # Например, создаем 5 потоков
    i += 1

    thread = threading.Thread(target=start_select_user_to_send,
                              args=(client, usernames, messages, count))
    thread.name = i
    thread.start()
    count += 50

    threads.append(thread)

for thread in threads:
    thread.join()
