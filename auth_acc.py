from pyrogram import Client
import sqlite3
import sys
# Создание подключения к базе данных
conn = sqlite3.connect('accounts.db')

# Создание курсора для выполнения SQL-запросов
cur = conn.cursor()
api_id = 12010295
api_hash = 'd9680b7ed54f9b8b48e7c71deb136a33'
try:
    cur.execute(
        "SELECT phone_number FROM accounts")
    phone_numbers = [row[0] for row in cur.fetchall()]
    # Создание клиента
    clients = []

    for phone_number in phone_numbers:
        ses_name = f"session_{phone_number}"
        clients.append(Client(ses_name, api_id, api_hash,
                              phone_number=phone_number))
    # Запрос номера телефона и отправка кода подтверждения
except Exception as e:
    print(f"Ошибка при получении данных: {e}")
    sys.exit()


def get_self_info(client):
    me = client.get_me()
    username = me.username
    id_user = me.id
    phone_number = me.phone_number
    ses_name = str(client.name)
    if username and id_user and phone_number:
        # Проверяем, существует ли уже запись с таким id_user в базе данных
        cur.execute(
            "SELECT id_user FROM accounts_auth WHERE phone_number = ?", (phone_number,))
        existing_record = cur.fetchone()
        if existing_record:
            cur.execute(
                "DELETE FROM accounts WHERE phone_number = ?", (f"+{phone_number}",))
            # Сохранение изменений в базе данных
            conn.commit()
            print(
                f"User with phone_number +{phone_number} already exists in the database.Im delete this number from DB")

        else:
            try:
                cur.execute("INSERT INTO accounts_auth (username, phone_number, id_user, ses_name) VALUES (?, ?, ?, ?)",
                            (username, phone_number, id_user, ses_name))
                # Сохранение изменений в базе данных
                conn.commit()
                cur.execute(
                    "DELETE FROM accounts WHERE phone_number = ?", (f"+{phone_number}",))
                # Сохранение изменений в базе данных
                conn.commit()
                print('Complete')
            except Exception as e:
                print("Error inserting record into the database:", e)
    else:
        print("Error: Some of the required user information is missing.")


try:
    for client in clients:
        if not client.is_initialized:
            print(f"Введите код с номера {client.phone_number}")
            client.start()
        get_self_info(client)
        client.stop()
except Exception as e:
    print(f"Ошибка при запуске клиентов: {e}")
print("Авторизация завершина")
print("Нажмите Enter для завершения программы...")
input()
