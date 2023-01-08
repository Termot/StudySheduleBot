import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import sqlite3
import utils_timeclasses
from tokens import tokens

from utils_func import timer

token = tokens('vk_tc_bgau')  # API-ключ с доступом к сообщениям сообщества

vk = vk_api.VkApi(token=token)  # Авторизуемся как сообщество

longpoll = VkLongPoll(vk)  # Работа с сообщениями

conn = sqlite3.connect('user_config.db', check_same_thread=False)  # подключаемся к базе данных
cur = conn.cursor()  # наводим курсор в базу данных


@timer
class VkBot:
    def __init__(self, user_id):
        self._USER_ID = user_id

        self._WEEKS = ['ПОНЕДЕЛЬНИК', 'ВТОРНИК', 'СРЕДА', 'ЧЕТВЕРГ', 'ПЯТНИЦА', 'СУББОТА']

    def write_msg(self, message):                                                               # пишем сообщение
        vk.method('messages.send', {'user_id': self._USER_ID,
                                    'random_id': get_random_id(),
                                    'message': message,
                                    'keyboard': self.create_keyboard()})

    def timeclasses(self, message):                                                             # Расписание
        cur.execute(f'SELECT * FROM users_config WHERE userid = {self._USER_ID}')
        record = cur.fetchall()

        tc_time = {'1': '8:30-10:05', '2': '10:20-11:55', '3': '12:10-13:45',
                   '4': '14:45-16:20', '5': '16:35-18:10', '6': '18:25-20:00'}

        try:
            if message in self._WEEKS:
                timeclasses = utils_timeclasses.init(message, record[0][3], record[0][4], record[0][5], record[0][6])

                send_mes = ''
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
            self.error_data_msg(record)

    def error_data_msg(self, info):                                # сообщение с ошибкой о неправильно введенных данных
        print(self._USER_ID, info)
        self.write_msg('''Введите:
        ФАКУЛЬТЕТ, СПЕЦИАЛЬНОСТЬ, КУРС, НОМЕР ПОДГРУППЫ''')

    # проверяем правильность введенных данных
    def check_valid_data(self, message_list):
        if cur.execute('SELECT userid FROM users_config WHERE факультет is NULL'):
            pass
        else:
            self.error_data_msg(message_list)

    def new_message(self, message):                                                         # чекаем новые сообщения
        if message.upper() in self._WEEKS:
            self.timeclasses(message.upper())

        elif any(x in message for x in ['Факультет', 'Специальность', 'Курс', 'Группа']):   # меняем место обучения
            self.user_data_writer(message.upper())

            if 'Факультет' in message:       self.write_msg('Выберите специальность')
            elif 'Специальность' in message: self.write_msg('Выберите курс')
            elif 'Курс' in message:          self.write_msg('Выберите группу')
            elif 'Группа' in message:        self.write_msg('Успех, можете начать пользоваться ботом')

        elif 'Поменять место обучения' in message:                                          # меняем место обучения
            cur.execute(f'DELETE from users_config where userid = {self._USER_ID}')
            conn.commit()
            self.user_config()
            self.write_msg('Выберите факультет')

        elif 'Поменять неделю обучения' in message:                                         # меняем неделю обучения
            pass

        elif 'Связь с разработчиком' in message:
            self.write_msg('[termot|Ссылка на страницу], можете сообщить об ошибке, \
                           недочетах или предложить что-то новое')

        else:                                                                               # если нет похожих сооб.
            self.error_data_msg('Ошибка, нет такого сообщения')

    def create_keyboard(self):                                                   # клавиатура (кнопки)
        keyboard = VkKeyboard(one_time=True)

        if not self.invalid_user():
            keyboard.add_button('Понедельник', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('Вторник', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('Среда', color=VkKeyboardColor.PRIMARY)

            keyboard.add_line()
            keyboard.add_button('Четверг', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('Пятница', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('Суббота', color=VkKeyboardColor.PRIMARY)

            keyboard.add_line()
            keyboard.add_button('Поменять место обучения', color=VkKeyboardColor.SECONDARY)

            keyboard.add_line()
            keyboard.add_button('Связь с разработчиком', color=VkKeyboardColor.SECONDARY)

            # keyboard.add_line()
            # keyboard.add_button('Поменять неделю обучения')

        # сюда нужно принимать значения, сначала запись фака, потом спец., потом группа
        # проверять лучше на наличие папок, т.к. добавление еще одной базы данных хуже
        # можно придумать и другой метод проверки
        elif self.invalid_user():
            if self.invalid_user()[0] == 'Факультет':
                for i in range(0, len(self.invalid_user()[1])):
                    keyboard.add_button(f'Факультет {self.invalid_user()[1][i]}', color=VkKeyboardColor.POSITIVE)

            elif self.invalid_user()[0] == 'Специальность':
                for i in range(0, len(self.invalid_user()[1])):
                    keyboard.add_button(f'Специальность {self.invalid_user()[1][i]}', color=VkKeyboardColor.POSITIVE)

            elif self.invalid_user()[0] == 'Курс':
                for i in range(0, len(self.invalid_user()[1])):
                    keyboard.add_button(f'Курс {self.invalid_user()[1][i]}', color=VkKeyboardColor.POSITIVE)

            elif self.invalid_user()[0] == 'Группа':
                for i in range(0, len(self.invalid_user()[1])):
                    keyboard.add_button(f'Группа {self.invalid_user()[1][i]}', color=VkKeyboardColor.POSITIVE)

        return keyboard.get_keyboard()

    def invalid_user(self):                                          # если пользователь НОВЫЙ или ЗАНОВО ВВОДИТ ДАННЫЕ
        # проверяем, записан ли юзер ПОЛНОСТЬЮ, если да, отчищаем фак, спец, группу
        # проверяем, записан ли юзер ПО ОТДЕЛЬНОСТИ фак, спец, группа

        cur.execute(f'SELECT * FROM users_config WHERE userid = "{self._USER_ID}"')
        rows = cur.fetchall()

        if rows[0][3] is None:
            cur.execute('SELECT факультет FROM faculties')
            faculties = cur.fetchall()
            contents = []
            for i in range(0, len(faculties)):
                if not faculties[i][0] in contents:
                    contents.append(faculties[i][0])

            return 'Факультет', contents

        elif rows[0][4] is None:
            cur.execute(f'SELECT специальность '
                        f'FROM faculties '
                        f'WHERE факультет = "{rows[0][3]}"')
            faculties = cur.fetchall()
            contents = []
            for i in range(0, len(faculties)):
                if not faculties[i][0] in contents:
                    contents.append(faculties[i][0])

            return 'Специальность', contents

        elif rows[0][5] is None:
            cur.execute(f'SELECT курс '
                        f'FROM faculties '
                        f'WHERE факультет = "{rows[0][3]}" '
                        f'AND специальность = "{rows[0][4]}"')
            faculties = cur.fetchall()
            contents = []
            for i in range(0, len(faculties)):
                if not faculties[i][0] in contents:
                    contents.append(faculties[i][0])

            return 'Курс', contents

        elif rows[0][6] is None:
            cur.execute(f'SELECT подгруппы '
                        f'FROM faculties '
                        f'WHERE факультет = "{rows[0][3]}" '
                        f'AND специальность = "{rows[0][4]}" '
                        f'AND курс = "{rows[0][5]}"')
            faculties = cur.fetchall()
            contents = []
            for i in range(0, len(faculties)):
                if not faculties[i][0] in contents:
                    contents = faculties[i][0].split(', ')

            return 'Группа', contents

        else:
            return False

    def user_data_writer(self, data):                        # записываем данные пользователя в базу данных user_config
        data_list = data.split(' ')

        if data_list[0] == 'ФАКУЛЬТЕТ':
            cur.execute(f'''UPDATE users_config 
            SET факультет = "{data_list[1].upper()}" 
            WHERE userid = {self._USER_ID};''')
            conn.commit()

        elif data_list[0] == 'СПЕЦИАЛЬНОСТЬ':
            cur.execute(f'''UPDATE users_config 
            SET специальность = "{data_list[1].capitalize()}" 
            WHERE userid = {self._USER_ID};''')
            conn.commit()

        elif data_list[0] == 'КУРС':
            cur.execute(f'''UPDATE users_config 
            SET курс = "{data_list[1]}" 
            WHERE userid = {self._USER_ID};''')
            conn.commit()

        elif data_list[0] == 'ГРУППА':
            cur.execute(f'''UPDATE users_config 
            SET группа = "{data_list[1].upper()}" 
            WHERE userid = {self._USER_ID};''')
            conn.commit()
            ud = vk.method('users.get', {'user_id': self._USER_ID})[0]
            ufname = ud['first_name']
            ulname = ud['last_name']

            cur.execute(f'SELECT * FROM users_config WHERE userid = "{self._USER_ID}"')
            rows = cur.fetchall()[0]
            self.write_msg(f'''Факультет:     {rows[3]}
Специальность: {rows[4]}
Курс:          {rows[5]}
Группа:        {rows[6]}''')

            print(f'Зарегистрирован "{ulname} {ufname}"')

        else: self.error_data_msg('Ошибка')

        self.invalid_user()

    # работа с файлом, содержащего конфигурацию юзеров
    # user_id и дополнительная информация
    def user_config(self):
        ud = vk.method('users.get', {'user_id': self._USER_ID})[0]
        uid = ud['id']
        ufname = ud['first_name']
        ulname = ud['last_name']

        cur.execute(f'SELECT userid FROM users_config WHERE userid = "{uid}"')
        if cur.fetchone() is None:
            cur.execute('''INSERT INTO users_config(userid, фамилия, имя)
                        VALUES(?, ?, ?);''', (f'{uid}', f'{ulname}', f'{ufname}'))
            conn.commit()
            print(f'Добавлен новый юзер "{ulname} {ufname}"')

        else:
            pass


def init():                                                                                 # Основной цикл
    print('Запущен бот ВК\n')

    for event in longpoll.listen():

        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:

            # Если оно имеет метку для меня (то есть бота)
            if event.to_me:
                # передаем в __init__ класса VkBot айди юзера
                vk_bot = VkBot(event.user_id)

                # Сообщение от пользователя
                request = event.text

                # users data
                vk_bot.user_config()

                # команды бота
                # user_id - user_id, message - request
                vk_bot.new_message(request)


def start_vk_bot():
    while True:
        try:
            init()

        except Exception as exc:
            print('\nОшибка в vk_bot.py'
                  f'{exc}\n')
