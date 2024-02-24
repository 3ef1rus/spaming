from pyrogram import Client
import sqlite3
# Создание клиента
app = Client("session_+380686086785")

# Определение идентификатора чата
# Замените на реальный идентификатор вашей группы
chat_id = input("Введите ссылку на чат или id")

# Функция для получения списка участников группы с айди, юзернеймом и ссылкой
conn = sqlite3.connect('accounts.db')
cur = conn.cursor()
cur.execute(f'''CREATE TABLE IF NOT EXISTS members_info (
                id INTEGER PRIMARY KEY,
                username TEXT,
                link TEXT
            )''')
conn.commit()


async def write_to_database():
    async for member in app.get_chat_members(chat_id):
        user_id = member.user.id
        username = member.user.username
        if username == None:
            continue
        link = f"https://t.me/{username}"
        # Вставка информации о пользователе в базу данных
        cur.execute("INSERT INTO members_info (id, username, link) VALUES (?, ?, ?)",
                    (user_id, username, link))
    conn.commit()

# Запуск клиента и вызов функции
with app:
    app.loop.run_until_complete(write_to_database())

# Вывод сообщения об успешной записи
print("Member information has been written to the database.")

# Закрытие соединения с базой данных
cur.close()
conn.close()
print("Получение пользователей завершен")
print("Нажмите Enter для завершения программы...")
input()
