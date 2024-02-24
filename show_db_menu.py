import sqlite3
import curses

# Функция для вывода всей информации из таблицы


def print_table_data(connection, table_name, stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, f"Информация из таблицы '{table_name}':")
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    if rows:
        idx = 2
        for row in rows:
            for i, line in enumerate(str(row).split('\n')):
                try:
                    stdscr.addstr(idx + i, 0, line)
                except curses.error:
                    pass  # Игнорируем строки, вызывающие ошибку при добавлении на экран
            idx += i + 1  # увеличиваем idx на количество добавленных строк в текущей итерации
    else:
        stdscr.addstr(1, 0, "В таблице нет данных.")
    stdscr.refresh()

# Функция для добавления новой записи в таблицу


def add_record(connection, table_name, stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, f"Добавление новой записи в таблицу '{table_name}':")
    stdscr.addstr(2, 0, "Введите данные для новой записи и нажмите Enter:")
    stdscr.refresh()

    # Получение списка колонок из базы данных
    cursor = connection.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    # Словарь для хранения введенных пользователем данных для каждой колонки
    data = {}

    # Запрос данных от пользователя для каждой колонки
    for idx, column in enumerate(columns):
        if column[1] not in ("id", "auth"):
            stdscr.addstr(idx + 3, 0, f"{column[1]}: ")
            stdscr.refresh()
            curses.echo()  # Размораживаем ввод с клавиатуры
            input_text = stdscr.getstr().decode(
                encoding="utf-8")  # Получаем ввод пользователя
            curses.noecho()  # Замораживаем ввод с клавиатуры
            data[column[1]] = input_text

    # Формирование SQL-запроса для вставки данных
    column_names = ', '.join(data.keys())
    column_values = ', '.join([f"'{value}'" for value in data.values()])
    query = f"INSERT INTO {table_name} ({column_names}) VALUES ({column_values})"

    # Вставка новой записи в таблицу
    cursor.execute(query)
    connection.commit()


def delete_record(connection, table_name, stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, f"Удаление записи из таблицы '{table_name}':")
    stdscr.refresh()

    # Получение списка записей из базы данных
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    if not rows:
        stdscr.addstr(2, 0, "В таблице нет записей для удаления.")
        stdscr.refresh()
        stdscr.getch()  # Ожидание нажатия любой клавиши
        return

    # Отображение записей и получение выбора пользователя
    selected_row = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Удаление записи из таблицы '{table_name}':")
        for idx, row in enumerate(rows):
            if idx == selected_row:
                stdscr.addstr(idx + 2, 0, f"> {row}")
            else:
                stdscr.addstr(idx + 2, 0, f"  {row}")
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and selected_row > 0:
            selected_row -= 1
        elif key == curses.KEY_DOWN and selected_row < len(rows) - 1:
            selected_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            # Удаление выбранной записи
            deleted_row = rows[selected_row]
            cursor.execute(
                f"DELETE FROM {table_name} WHERE rowid=?", (deleted_row[0],))
            connection.commit()
            stdscr.addstr(len(rows) + 2, 0, f"Запись {deleted_row} удалена.")
            stdscr.refresh()
            stdscr.getch()  # Ожидание нажатия любой клавиши для выхода
            break
        elif key == ord('q'):
            break


# Подключение к базе данных
try:
    # Замените 'example.db' на ваш файл базы данных
    connection = sqlite3.connect('accounts.db')
except sqlite3.Error as e:
    print("Ошибка при подключении к базе данных:", e)
else:
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    # Получение списка всех таблиц в базе данных
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    if tables:
        current_idx = 0
        while True:
            stdscr.clear()
            stdscr.addstr(
                0, 0, "Выберите таблицу для просмотра (используйте стрелки):")
            for idx, table in enumerate(tables):
                if idx == current_idx:
                    stdscr.addstr(idx + 2, 0, f"> {table[0]}")
                else:
                    stdscr.addstr(idx + 2, 0, f"  {table[0]}")
            stdscr.refresh()
            key = stdscr.getch()
            if key == curses.KEY_UP and current_idx > 0:
                current_idx -= 1
            elif key == curses.KEY_DOWN and current_idx < len(tables) - 1:
                current_idx += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                table_name = tables[current_idx][0]
                action_idx = 0
                while True:
                    stdscr.clear()
                    stdscr.addstr(0, 0, f"Действия с таблицей '{table_name}':")
                    stdscr.addstr(
                        1, 0, "Выберите действие (используйте стрелки):")
                    stdscr.addstr(2, 0, "1. Просмотреть таблицу")
                    stdscr.addstr(3, 0, "2. Добавить запись в таблицу")
                    stdscr.addstr(4, 0, "3. Удалить запись из таблицы")
                    if action_idx == 0:
                        stdscr.addstr(2, 0, "> Просмотреть таблицу")
                    elif action_idx == 1:
                        stdscr.addstr(3, 0, "> Добавить запись в таблицу")
                    elif action_idx == 2:
                        stdscr.addstr(4, 0, "> Удалить запись из таблицы")
                    stdscr.refresh()
                    key = stdscr.getch()
                    if key == curses.KEY_UP and action_idx > 0:
                        action_idx -= 1
                    elif key == curses.KEY_DOWN and action_idx < 2:
                        action_idx += 1
                    elif key == curses.KEY_ENTER or key in [10, 13]:
                        if action_idx == 0:
                            print_table_data(connection, table_name, stdscr)
                            stdscr.getch()  # Ожидание нажатия любой клавиши для выхода из режима просмотра таблицы
                        elif action_idx == 1:
                            add_record(connection, table_name, stdscr)
                        elif action_idx == 2:
                            delete_record(connection, table_name, stdscr)
                    elif key == 27:
                        break

            elif key == 27:
                break

    else:
        print("База данных не содержит таблиц.")
    curses.endwin()
    connection.close()
