import telebot
from telebot import types
import sqlite3
import utils_timeclasses
from tokens import tokens
from datetime import timedelta, date
# from utils_func import timer


class TgBot:
    def __init__(self, bot, message):
        self._USER_ID = message.chat.id  # chat_id as user_id
        self._DEV_ID = 564406986  # id a developer

        self._BOT = bot  # Авторизуемся как сообщество
        self._MARKUP = types.ReplyKeyboardMarkup(resize_keyboard=True)

        self._MESSAGE = message

        self._WEEKS = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ']
        self._WEEKS_FULL = ['ПОНЕДЕЛЬНИК', 'ВТОРНИК', 'СРЕДА', 'ЧЕТВЕРГ', 'ПЯТНИЦА', 'СУББОТА']

        self._CONN = sqlite3.connect('user_config_tg.db', check_same_thread=False)  # подключаемся к базе данных
        self._CUR = self._CONN.cursor()  # наводим курсор в базу данных

    def write_msg(self, bot_text):                                                      # пишем сообщение
        self._BOT.send_message(self._MESSAGE.chat.id, bot_text, reply_markup=self._MARKUP)

    def add_button(self, btn_name):  # входное значение: имя кнопки
        self._MARKUP.add(types.KeyboardButton(btn_name))

    def timeclasses(self, message):                                                             # Расписание
        self._CUR.execute(f'SELECT * FROM users_config WHERE userid = {self._USER_ID}')
        record = self._CUR.fetchall()

        tc_time = {'1': '8:30-10:05', '2': '10:20-11:55', '3': '12:10-13:45',
                   '4': '14:45-16:20', '5': '16:35-18:10', '6': '18:25-20:00'}

        try:
            if message in self._WEEKS:
                week_day = message

                message = self._WEEKS_FULL[self._WEEKS.index(message)]
                timeclasses = utils_timeclasses.init(message, record[0][3], record[0][4], record[0][5], record[0][6])

                send_mes = f'Дата: {self.get_weekday_date(week_day)} \n\n'

                if timeclasses:
                    for row in timeclasses:

                        send_mes += f'Пара: {row["Пара"]} ({tc_time[row["Пара"]]}) \n' \
                                    f'Предмет: {row["Предмет"]} \n' \
                                    f'Аудитория: {row["Аудитория"]} \n' \
                                    '\n'

                    self.write_msg(send_mes)

                else:
                    self.write_msg('На этот день нет расписания или оно еще не написано')

        except:
            self.error_data_msg('EXCEPTION def timeclasses')

    def timeclasses_add(self):  # добавляем расписание
        uid = self._USER_ID  # id чата с пользователем

        self._CUR.execute(f'SELECT condition FROM "/tc" WHERE userid = "{uid}"')
        condition = self._CUR.fetchone()[0]

        # проверяем юзера в таблице с уровнем доступа к командам
        self._CUR.execute(f'SELECT userid FROM users_perm_lvl WHERE userid = "{uid}"')
        if self._CUR.fetchone() is None:
            # тут что делать, если у пользователя нет доступа к добавлению/редактированию расписания
            pass

        else:  # добавить inline кнопки вместо клавиатурных
            self._CUR.execute(f'SELECT perm_lvl FROM users_perm_lvl WHERE userid = "{uid}"')
            permission_lvl = self._CUR.fetchone()[0]

            if condition == 'ADD' and permission_lvl == 'dev':
                self._CUR.execute(f'SELECT * FROM "/tc" WHERE userid == "{uid}"')
                rows = self._CUR.fetchall()[0]

                # rows = (userid, condition, faculty, specalization, course, group)
                # выберите факультет
                if rows[2] is None:
                    faculty_list = ['АТиЛХ', 'БТиВМ', 'Мех', 'Пищ', 'ФПС', 'Эконом', 'Энерго']
                    for key in faculty_list:
                        self.add_button('/tc факультет ' + key)
                    self.write_msg('Выберите факультет')
                    return 1

                # введите специальность
                elif rows[3] is None:
                    self._CUR.execute(f'SELECT специальность FROM faculties WHERE факультет = "{rows[2]}"')
                    self.write_msg('Введите специальность: /tc специальность ...')
                    return 1

                # введите курс
                elif rows[4] is None:
                    self._CUR.execute(f'SELECT курс FROM faculties WHERE факультет = "{rows[2]}"')
                    self.write_msg('Введите курс: /tc курс ...')
                    return 1

                # введите группа
                elif rows[5] is None:
                    self._CUR.execute(f'SELECT подгруппы FROM faculties WHERE факультет = "{rows[2]}"')
                    self.write_msg('Введите группу: /tc группа ...')
                    return 1

                else:
                    print('жопа')

    def timeclasses_edit(self):
        uid = self._USER_ID  # id чата с пользователем

        self._CUR.execute(f'SELECT condition FROM "/tc" WHERE userid = "{uid}"')
        condition = self._CUR.fetchone()[0]

        # проверяем юзера в таблице с уровнем доступа к командам
        self._CUR.execute(f'SELECT userid FROM users_perm_lvl WHERE userid = "{uid}"')
        if self._CUR.fetchone() is None:
            # тут что делать, если у пользователя нет доступа к добавлению/редактированию расписания
            pass

        else:  # добавить inline кнопки вместо клавиатурных
            self._CUR.execute(f'SELECT perm_lvl FROM users_perm_lvl WHERE userid = "{uid}"')
            permission_lvl = self._CUR.fetchone()[0]

            if condition == 'EDIT' and permission_lvl == 'dev':
                self._CUR.execute(f'SELECT * FROM "/tc" WHERE userid == "{uid}"')
                rows = self._CUR.fetchall()[0]

                # rows = (userid, condition, faculty, specialization, course, group)
                # выберите факультет
                if rows[2] == '':
                    self._CUR.execute('SELECT факультет FROM faculties')
                    faculty_list = self._CUR.fetchall()[0]
                    for key in faculty_list:
                        self.add_button('/tc факультет ' + key)
                    self.write_msg('Выберите факультет')
                    return 1

                # выберите специальность
                elif rows[3] == '':
                    self._CUR.execute(f'SELECT специальность FROM faculties WHERE факультет = "{rows[2]}"')
                    for spec in self._CUR.fetchall():
                        self.add_button('/tc специальность ' + spec[0])
                    self.write_msg('Выберите специальность')
                    return 1

                # выберите курс
                elif rows[4] == '':
                    self._CUR.execute(f'SELECT курс FROM faculties WHERE факультет = "{rows[2]}"')
                    for course in self._CUR.fetchall():
                        self.add_button('/tc курс ' + course[0])
                    self.write_msg('Выберите курс')
                    return 1

                # выберите группа
                elif rows[5] == '':
                    self._CUR.execute(f'SELECT подгруппы FROM faculties WHERE факультет = "{rows[2]}"')
                    for group in self._CUR.fetchall():
                        self.add_button('/tc группа ' + group[0])
                    self.write_msg('Выберите группу')
                    return 1

                elif rows[5] != '':
                    for weekday in self._WEEKS:
                        self.add_button('/tc ' + weekday)
                    self.add_button('Меню')
                    self.write_msg('Выберите день недели')

    def error_data_msg(self, info):                                # сообщение с ошибкой о неправильно введенных данных
        print(info)
        self.create_keyboard()

    def new_message(self):                                                         # чекаем новые сообщения
        message = self._MESSAGE.text
        self.user_config()

        if message in self._WEEKS:
            self.timeclasses(message)

        elif any(x in message for x in ['Факультет', 'Специальность', 'Курс', 'Группа']):   # меняем место обучения
            self.user_data_writer(message.upper())
            self.create_keyboard()

            if 'Группа' in message:
                self.write_msg('Успех, можете начать пользоваться ботом')

        elif 'Расписание' in message:
            if self._USER_ID == self._DEV_ID:  # dev tools
                commands = ['/tc добавить', '/tc редактировать', 'Команды', 'Меню']
                for key in commands:
                    self.add_button(key)
                self.write_msg('Выберите:')

        elif 'Обновить кнопки' in message:
            if self._USER_ID == self._DEV_ID:  # dev tools
                self.reload_keyboard()

        elif '/tc_add' in message:
            uid = self._USER_ID
            if 'факультет' in message:
                faculty = message.split(' ')[2]
                self._CUR.execute(f'''UPDATE "/tc" SET факультет = "{faculty}" WHERE userid = "{uid}";''')
                self._CONN.commit()
                self.timeclasses_add()

            elif 'специальность' in message:
                specialization = message.split(' ')[2]
                self._CUR.execute(f'''UPDATE "/tc" SET специальность = "{specialization}" WHERE userid = "{uid}";''')
                self._CONN.commit()
                self.timeclasses_add()

            elif 'курс' in message:
                course = message.split(' ')[2]
                self._CUR.execute(f'''UPDATE "/tc" SET курс = "{course}" WHERE userid = "{uid}";''')
                self._CONN.commit()
                self.timeclasses_add()

            elif 'группа' in message:
                group = message.split(' ')[2]
                self._CUR.execute(f'''UPDATE "/tc" SET группа = "{group}" WHERE userid = "{uid}";''')
                self._CONN.commit()
                self.timeclasses_add()
            else:
                self.add_button('Расписание')
                self.write_msg('Выберите команду:')

        elif '/tc_edit' in message:
            pass

        elif '/tc' in message:  # команда выбора группы для записи/редактирования расписания
            if 'добавить' in message:
                # condition = "ADD" для юзера
                self._CUR.execute(f'''UPDATE "/tc"
                                      SET condition = "ADD",
                                      факультет = "",
                                      специальность = "",
                                      курс = "",
                                      группа = ""
                                      WHERE userid = {self._USER_ID};''')
                self._CONN.commit()
                self.timeclasses_add()

            elif 'редактировать' in message:
                self._CUR.execute(f'''UPDATE "/tc"
                                      SET condition = "EDIT",
                                      факультет = "",
                                      специальность = "",
                                      курс = "",
                                      группа = ""
                                      WHERE userid = {self._USER_ID};''')
                self._CONN.commit()
                self.timeclasses_edit()

            elif any(x in message for x in ['факультет', 'специальность', 'курс', 'группа']):
                mes_list = message.split(' ')
                column = mes_list[1]
                row = mes_list[2]
                self._CUR.execute(f'''UPDATE "/tc"
                                      SET "{column}" = "{row}"
                                      WHERE userid = {self._USER_ID}''')
                self._CONN.commit()
                self._CUR.execute(f'SELECT condition FROM "/tc" WHERE userid = {self._USER_ID}')
                condition = self._CUR.fetchone()[0]
                if condition == 'ADD': self.timeclasses_add()
                elif condition == 'EDIT': self.timeclasses_edit()

            elif any(x in message for x in self._WEEKS):
                self._CUR.execute(f'SELECT * FROM "/tc" WHERE userid = {self._USER_ID}')
                record = self._CUR.fetchall()

                tc_time = {'1': '8:30-10:05', '2': '10:20-11:55', '3': '12:10-13:45',
                           '4': '14:45-16:20', '5': '16:35-18:10', '6': '18:25-20:00'}

                message = message.split(' ')[1]
                message = self._WEEKS_FULL[self._WEEKS.index(message)]
                timeclasses = utils_timeclasses.init(message, record[0][2], record[0][3], record[0][4], record[0][5])

                send_mes = ''
                if timeclasses:
                    for row in timeclasses:
                        send_mes += f'Группа: {row["Группа"]} \n' \
                                    f'Пара: {row["Пара"]} \n' \
                                    f'Предмет: {row["Предмет"]} \n' \
                                    f'Недели: {row["Недели"]} \n' \
                                    f'Аудитория: {row["Аудитория"]} \n' \
                                    '\n'

                    self.write_msg(send_mes)

            else:
                self.add_button('Расписание')
                self.write_msg('Расписание')

        elif 'Команды' in message:
            commands = [self.add_button('Поменять группу',),
                        self.add_button('Поменять неделю обучения'),
                        self.add_button('Связь с разработчиком'),
                        self.add_button('Меню')]
            markup = types.ReplyKeyboardRemove()
            self._BOT.send_message(self._USER_ID, 'Меню выкл.', reply_markup=markup, parse_mode='Markdown')
            for key in commands:
                self._MARKUP.add(key)
            if self._USER_ID == self._DEV_ID:
                self.add_button('Обновить кнопки')
                self.add_button('Расписание')
            self.write_msg('Команды:')

        elif 'Меню' in message:
            markup = types.ReplyKeyboardRemove()
            self._BOT.send_message(self._USER_ID, 'Меню выкл.', reply_markup=markup, parse_mode='Markdown')
            self.create_keyboard()

        elif 'Поменять место обучения' in message:                                          # меняем место обучения
            self._CUR.execute(f'DELETE from users_config where userid = {self._USER_ID}')
            self._CONN.commit()
            self.user_config()
            self.create_keyboard()
            self.write_msg('Выберите факультет')

        elif 'Поменять неделю обучения' in message:                                         # меняем неделю обучения
            commands = [self.add_button('Следующая неделя'),
                        self.add_button('Текущая неделя')]

        elif 'Связь с разработчиком' in message:
            text = '[Ссылка](https://vk.com/termot), можете сообщить об ошибке, недочетах или предложить что-то новое'
            self._BOT.send_message(self._MESSAGE.chat.id, text, parse_mode='Markdown')

        else:                                                                               # если нет похожих сооб.
            self.error_data_msg('Ошибка, нет такого сообщения')

    def create_keyboard(self):                                                   # клавиатура (кнопки)
        if not self.invalid_user():
            monday = types.KeyboardButton('ПН')
            tuesday = types.KeyboardButton('ВТ')
            wednesday = types.KeyboardButton('СР')
            thursday = types.KeyboardButton('ЧТ')
            friday = types.KeyboardButton('ПТ')
            saturday = types.KeyboardButton('СБ')

            commands = types.KeyboardButton('Команды')

            self._MARKUP.row(monday, tuesday, wednesday, thursday, friday, saturday)

            self._MARKUP.add(commands)

            self.write_msg('Меню вкл.')

        # сюда нужно принимать значения, сначала запись фака, потом спец., потом группа
        # проверять лучше на наличие папок, т.к. добавление еще одной базы данных хуже
        # можно придумать и другой метод проверки
        elif self.invalid_user():
            if self.invalid_user()[0] == 'Факультет':
                for i in range(0, len(self.invalid_user()[1])):
                    self._MARKUP.row(types.KeyboardButton(f'Факультет {self.invalid_user()[1][i]}'))
                self.write_msg('Выберите факультет')

            elif self.invalid_user()[0] == 'Специальность':
                for i in range(0, len(self.invalid_user()[1])):
                    self._MARKUP.row(types.KeyboardButton(f'Специальность {self.invalid_user()[1][i]}'))
                self.write_msg('Выберите специальность')

            elif self.invalid_user()[0] == 'Курс':
                for i in range(0, len(self.invalid_user()[1])):
                    self._MARKUP.row(types.KeyboardButton(f'Курс {self.invalid_user()[1][i]}'))
                self.write_msg('Выберите курс')

            elif self.invalid_user()[0] == 'Группа':
                for i in range(0, len(self.invalid_user()[1])):
                    self._MARKUP.row(types.KeyboardButton(f'Группа {self.invalid_user()[1][i]}'))
                self.write_msg('Выберите подгруппу')

    def reload_keyboard(self):
        self._CUR.execute('SELECT userid FROM users_config')
        rows = self._CUR.fetchall()

        chat_id_list = []
        for i in range(len(rows)):
            chat_id_list.append(rows[i][0])

        markup = types.ReplyKeyboardRemove()
        for chat_id in chat_id_list:
            self._BOT.send_message(chat_id, 'Меню выкл.', reply_markup=markup, parse_mode='Markdown')
            self.create_keyboard()

    def invalid_user(self):                                          # если пользователь НОВЫЙ или ЗАНОВО ВВОДИТ ДАННЫЕ
        # проверяем, записан ли юзер ПОЛНОСТЬЮ, если да, отчищаем фак, спец, группу
        # проверяем, записан ли юзер ПО ОТДЕЛЬНОСТИ фак, спец, группа

        self._CUR.execute(f'SELECT * FROM users_config WHERE userid = "{self._USER_ID}"')
        rows = self._CUR.fetchall()

        if rows[0][3] is None:
            self._CUR.execute('SELECT факультет FROM faculties')
            faculties = self._CUR.fetchall()
            contents = []
            for i in range(0, len(faculties)):
                if not faculties[i][0] in contents:
                    contents.append(faculties[i][0])

            return 'Факультет', contents

        elif rows[0][4] is None:
            self._CUR.execute(f'SELECT специальность '
                              f'FROM faculties '
                              f'WHERE факультет = "{rows[0][3]}"')
            faculties = self._CUR.fetchall()
            contents = []
            for i in range(0, len(faculties)):
                if not faculties[i][0] in contents:
                    contents.append(faculties[i][0])

            return 'Специальность', contents

        elif rows[0][5] is None:
            self._CUR.execute(f'SELECT курс '
                              f'FROM faculties '
                              f'WHERE факультет = "{rows[0][3]}" '
                              f'AND специальность = "{rows[0][4]}"')
            faculties = self._CUR.fetchall()
            contents = []
            for i in range(0, len(faculties)):
                if not faculties[i][0] in contents:
                    contents.append(faculties[i][0])

            return 'Курс', contents

        elif rows[0][6] is None:
            self._CUR.execute(f'SELECT подгруппы '
                              f'FROM faculties '
                              f'WHERE факультет = "{rows[0][3]}" '
                              f'AND специальность = "{rows[0][4]}" '
                              f'AND курс = "{rows[0][5]}"')
            faculties = self._CUR.fetchall()
            contents = []
            for i in range(0, len(faculties)):
                if not faculties[i][0] in contents:
                    contents = faculties[i][0].split(' и ')

            return 'Группа', contents

        else:
            return False

    def user_data_writer(self, data):                        # записываем данные пользователя в базу данных user_config
        data_list = data.split(' ')

        if data_list[0] == 'ФАКУЛЬТЕТ':
            self._CUR.execute(f'''UPDATE users_config 
            SET факультет = "{data_list[1].upper()}" 
            WHERE userid = {self._USER_ID};''')
            self._CONN.commit()

        elif data_list[0] == 'СПЕЦИАЛЬНОСТЬ':
            self._CUR.execute(f'''UPDATE users_config 
            SET специальность = "{data_list[1].capitalize()}" 
            WHERE userid = {self._USER_ID};''')
            self._CONN.commit()

        elif data_list[0] == 'КУРС':
            self._CUR.execute(f'''UPDATE users_config 
            SET курс = "{data_list[1]}" 
            WHERE userid = {self._USER_ID};''')
            self._CONN.commit()

        elif data_list[0] == 'ГРУППА':
            self._CUR.execute(f'''UPDATE users_config 
            SET группа = "{data_list[1].upper()}" 
            WHERE userid = {self._USER_ID};''')
            self._CONN.commit()

            self._CUR.execute(f'SELECT * FROM users_config WHERE userid = "{self._USER_ID}"')
            rows = self._CUR.fetchall()[0]
            self.write_msg(f'{rows[3]}, {rows[4]}, {rows[5]} курс, {rows[6]} подгруппа')

            print(f'Зарегистрирован в Telegram: "{self._USER_ID}"')

        else: self.error_data_msg('Ошибка')

        self.invalid_user()

    # работа с файлом, содержащего конфигурацию юзеров
    # user_id и дополнительная информация
    def user_config(self):
        uid = self._MESSAGE.chat.id

        self._CUR.execute(f'SELECT userid FROM users_config WHERE userid = "{uid}"')
        if self._CUR.fetchone() is None:
            self._CUR.execute(f'INSERT INTO users_config(userid) VALUES("{uid}");')
            self._CONN.commit()
            print(f'Добавлен новый юзер в Telegram: "{uid}"')

        else:
            pass

    def get_weekday_date(self, week_day):
        dt = date(2022, 8, 29)  # date toda
        ws = dt - timedelta(days=dt.weekday() + 1)  # week start -1 day
        ws = ws + timedelta(weeks=utils_timeclasses.week() - 1)  # текущая неделя

        ws_dict = {'ПН': '', 'ВТ': '', 'СР': '', 'ЧТ': '', 'ПТ': '', 'СБ': ''}

        for key, value in ws_dict.items():
            ws += timedelta(days=1)
            day, month, year = str(ws.day), str(ws.month), str(ws.year)
            converted_date = day + '.' + month + '.' + year

            # добавляем дату для каждого дня недели
            ws_dict.update({key: converted_date})

        return ws_dict[week_day]


def main():
    # создаем экземпляр бота
    bot = telebot.TeleBot(tokens('tg_tc_test_bot'))  # получаем токен из модуля tokens

    # функция, обрабатывающая команду /start
    @bot.message_handler(commands=['start'])
    def start(m, res=False):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('Чел ты')
        markup.add(item1)
        bot.send_message(m.chat.id, 'Чел я', reply_markup=markup)

    # получение сообщений от юзера
    @bot.message_handler(content_types=['text'])
    def handle_text(message):
        tgbot = TgBot(bot, message)
        # tgbot.user_config()
        tgbot.new_message()

    print('Запущен бот Telegram\n')

    # запускаем бота
    bot.polling(none_stop=True, interval=0)


def start_tg_bot():
    import time
    while True:
        try:
            main()
        except Exception as exc:
            print('\nОшибка в tg_bot.py'
                  f'{exc}\n')
            time.sleep(2)
            main()


main()
