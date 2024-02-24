import os
import curses
import subprocess
import sys

# Функция для отображения меню


def show_menu(stdscr):
    stdscr.clear()
    curses.curs_set(0)
    stdscr.addstr(0, 0, "Выберите действие:")
    stdscr.addstr(2, 0, "Открыть меню Базы данных")
    stdscr.addstr(3, 0, "Активировать аккаунты")
    stdscr.addstr(4, 0, "Проверить аккаунты на блокировку")
    stdscr.addstr(5, 0, "Получить пользователей из чата")
    stdscr.addstr(6, 0, "Начать заспам сообщениями")
    stdscr.addstr(7, 0, "Выход")
    stdscr.refresh()

    current_idx = 0
    while True:
        key = stdscr.getch()
        stdscr.clear()
        if key == curses.KEY_UP and current_idx > 0:
            current_idx -= 1
        elif key == curses.KEY_DOWN and current_idx < 5:
            current_idx += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_idx == 0:
                stdscr.clear()
                subprocess.run(["python", "show_db_menu.py"])
            elif current_idx == 1:
                stdscr.clear()
                os.system('cls')
                subprocess.run(["python", "auth_acc.py"])
            elif current_idx == 2:
                stdscr.clear()
                os.system('cls')
                subprocess.run(["python", "check_block_accs.py"])
            elif current_idx == 3:
                stdscr.clear()
                os.system('cls')
                subprocess.run(["python", "grp_in_to_db.py"])
            elif current_idx == 4:
                stdscr.clear()
                os.system('cls')
                subprocess.run(["python", "send_mess.py"])
            elif current_idx == 5:
                sys.exit()

            stdscr.refresh()
            show_menu(stdscr)  # Показываем меню снова после выполнения скрипта
            return
        elif key == 27:
            sys.exit()
        stdscr.addstr(0, 0, "Выберите действие:")
        for idx, action in enumerate(["Открыть меню Базы данных", "Активировать аккаунты", "Проверить аккаунты на блокировку", "Получить пользователей из чата", "Начать заспам сообщениями", "Выход"], start=2):
            if idx - 2 == current_idx:
                stdscr.addstr(idx, 0, f"> {action}")
            else:
                stdscr.addstr(idx, 0, f"  {action}")
        stdscr.refresh()


def main(stdscr):
    while True:
        show_menu(stdscr)


curses.wrapper(main)
