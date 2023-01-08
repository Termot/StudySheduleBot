import sys, os
from datetime import date, datetime, timedelta


# парсим недели обучения
# 3-11н/н,12
# 4-8ч/н
# 5-8
# 2,3
class StudyWeek:
    def __init__(self, week_num):
        self.week_num = week_num
        self.week_list = []

    # запятая ','
    def comma(self):
        week_list_temp = self.week_num.split(',')

        for string in week_list_temp:
            self.week_list.append(int(string))

        return self.week_list

    # дефис '-'
    def dash(self):
        week_list_temp = self.week_num.split('-')

        for i in range(int(week_list_temp[0]), int(week_list_temp[1]) + 1):
            self.week_list.append(i)

        return self.week_list

    # четность недели 'н/н' 'ч/н'
    def parity_weeks(self):
        # парсинг четных недель
        if 'ч/н' in self.week_num:

            self.week_num = self.week_num.replace('ч/н', '')  # убираем 'н/н' из строки

            if ',' in self.week_num:
                week_list_temp = self.week_num.split(',')  # в список добавляем строки разделенные запятой
            else:
                week_list_temp = [self.week_num]

            # для каждого элемента в списке
            for string in week_list_temp:
                # в списке может быть более одного элемента
                # проверяем наличие дефиса в них

                # если в элементе есть дефис
                if '-' in string:
                    week_list_temp_2 = string.split('-')  # в список добавляем строки разделенные запятой

                    # создаем последовательность чисел с первого элементо по второй (1-3 -> 1, 2, 3)
                    for i in range(int(week_list_temp_2[0]), int(week_list_temp_2[1]) + 1):
                        self.week_list.append(i)  # добавляем число в основной список недель

                    list_pop = []  # список для индекса четных недель

                    # узнаем индекс четных недель
                    for i in range(0, len(self.week_list)):
                        if self.week_list[i] % 2 != 0:
                            list_pop.append(i)

                    # удаляем нечетные недели по индексу
                    for i in list_pop[::-1]:  # удаляем с конца, чтобы не было ошибки
                        self.week_list.pop(i)

                # если в элементе нет дефиса
                elif '-' not in string:
                    # добавляем его в основной список
                    self.week_list.append(int(string))

        # парсинг нечетных недель
        if 'н/н' in self.week_num:

            self.week_num = self.week_num.replace('н/н', '')  # убираем 'н/н' из строки

            if ',' in self.week_num:
                week_list_temp = self.week_num.split(',')  # в список добавляем строки разделенные запятой
            else:
                week_list_temp = [self.week_num]

            # для каждого элемента в списке
            for string in week_list_temp:
                # так как в списке может быть более одного элемента
                # проверяем наличие дефиса в них

                # если в элементе есть дефис
                if '-' in string:
                    week_list_temp_2 = string.split('-')  # в список добавляем строки разделенные запятой

                    # создаем последовательность чисел с первого элементо по второй (1-3 -> 1, 2, 3)
                    for i in range(int(week_list_temp_2[0]), int(week_list_temp_2[1]) + 1):
                        self.week_list.append(i)  # добавляем число в основной список недель

                    list_pop = []  # список для индекса четных недель

                    # узнаем индекс четных недель
                    for i in range(0, len(self.week_list)):
                        if self.week_list[i] % 2 == 0:
                            list_pop.append(i)

                    # удаляем четные недели по индексу
                    for i in list_pop[::-1]:  # удаляем с конца, чтобы не было ошибки
                        self.week_list.pop(i)

                # если в элементе нет дефиса
                elif '-' not in string:
                    # добавляем его в основной список
                    self.week_list.append(int(string))

        return self.week_list  # возвращаем основной список


# парсим недели используя класс StudyWeek
def pars_weeks(week_num):
    # если нечетные или четные недели
    if 'н/н' in week_num or 'ч/н' in week_num:
        return StudyWeek(week_num).parity_weeks()

    # если с какую-то по какую-то недели
    elif '-' in week_num:
        return StudyWeek(week_num).dash()

    # если отдельные недели
    elif ',' in week_num:
        return StudyWeek(week_num).comma()

    else:
        return [int(week_num)]


def ru2en(row):
    ru = ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и',
          'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т',
          'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь',
          'э', 'ю', 'я']

    en = ['a', 'b', 'v', 'g', 'd', 'e', 'e', 'zh', 'z', 'i',
          'i', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't',
          'u', 'f', 'kh', 'ts', 'ch', 'sh', 'shch', 'ie', 'y', '',
          'e', 'iu', 'ia']

    row_new = ''

    for i in range(len(row)):
        if row[i] in ru:
            row_new += en[ru.index(row[i])]

        elif row[i].isupper():
            letter = row[i].lower()
            row_new += en[ru.index(letter)].upper()

        else:
            row_new += row[i]

    return row_new


def check_path(path):
    weeks = ['Понедельник', 'Вторник', 'Среда',
             'Четверг', 'Пятница', 'Суббота']

    folder_path = os.path.dirname(path)  # Путь к папке с файлом

    if not os.path.exists(folder_path):  # Если пути не существует - создаем его
        os.makedirs(folder_path)

    for i in range(0, len(weeks)):
        with open(folder_path + '/' + ru2en(weeks[i]) + '.txt', 'w') as file:  # Открываем файл и записываем дни недели
            file.write("")


# берем предметы за эту неделю
# path (директория файла с расписанием),
# 1 - первая группа, 2 - вторая, '1 и 2' - все группы
def subject(path, group):
    file = open(path, 'r', encoding='utf-8')
    line = file.readline()

    timeclasses_list = []

    print(line.strip())

    while True:
        timeclasses = {}

        line = file.readline()

        if 'Группа' in line.strip() and (str(group) in line.strip() or 'все' in group):
            timeclasses['Группа'] = line.strip()[8:]
            print(line)
            line = file.readline()

            if 'Пара' in line.strip():
                timeclasses.update({'Пара': line.strip()[6:]})
                print(line)
                line = file.readline()

            if 'Предмет' in line.strip():
                timeclasses.update({'Предмет': line.strip()[9:]})
                print(line)
                line = file.readline()

            if 'Недели' in line.strip():
                if 'все' in group:
                    timeclasses.update({'Недели': str(line.strip()[8:])})
                else:
                    timeclasses.update({'Недели': pars_weeks(line.strip()[8:])})
                print(line)
                line = file.readline()

            if 'Аудитория' in line.strip():
                timeclasses.update({'Аудитория': line.strip()[11:]})
                print(line)

            timeclasses_list.append(timeclasses)

        if not line:
            break

    return timeclasses_list


# отключить отладку print()
def blockPrint():
    sys.stdout = open(os.devnull, 'w')


# включить отладку print()
def enablePrint():
    sys.stdout = sys.__stdout__


def tc4edit(weekday, faculty, specialization, course, group):
    pass


def week():
    date_first = '2022-08-29'  # дата первого дня первой недели

    # нынешняя дата
    # +5 часов - переводим часовой пояс 'UTC' на '+5GMT'
    # +4 часа - после 20:00 показывается расписание на следующую неделю
    date_now = datetime.now() + timedelta(hours=9)
    date_now = date_now.strftime('%Y-%m-%d')  # конвертируем дату в строку

    def conv2date(string):  # конвертируем 'year-month-day' в числа
        year = int(string[:4])
        month = int(string[5:7])
        day = int(string[8:10])

        return date(year, month, day)

    # конвертируем даты
    date_first = conv2date(date_first)
    date_now = conv2date(date_now)

    diff = date_now - date_first  # разница между df и dn

    saturday_is_real = False  # есть обучение по субботам
    days_plus = 0

    if saturday_is_real:
        days_plus = 8  # плюс 8 дней для показа расписания на следующую неделю в воскресенье
    else:
        days_plus = 9  # плюс 9 дней для показа расписания на следующую неделю в субботу

    return int((diff.days + days_plus) / 7)


def init(weekday, faculty, specialization, course, group):
    faculty = ru2en(faculty.upper())  # факультет
    specialization = ru2en(specialization.capitalize())  # специальность
    weekday = ru2en(weekday.capitalize()) + '.txt'  # день недели
    root = ru2en('Факультеты')

    # папка с текстовыми файлами + день недели + .txt
    path = f'{root}/{faculty}/{specialization}/{course}/{weekday}'

    if 'и' in group:
        group = 'все'

    blockPrint()
    timeclasses = subject(path, group)
    enablePrint()

    timeclasses_list = []

    if 'все' in group:
        for tc_dict in timeclasses:
            timeclasses_list.append(tc_dict)
        return timeclasses_list

    for tc_dict in timeclasses:
        if week() in tc_dict['Недели']:
            # {'Группа': '1 и 2', 'Пара': '1', 'Предмет': 'Физ-ра', 'Недели': [2, 3, ...], 'Аудитория': 'с/зал'}
            timeclasses_list.append(tc_dict)

    return timeclasses_list

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# всегда

# weekday = 'ПОНЕДЕЛЬНИК'
#
# timeclass_date(weekday)
