import telebot
from search import find_apt, find_in_apt, find_in_apt_num, give_names, med, aptekas as sapt, find_in_apt_num_best
import pytz
from telebot import types
from collections import Counter

est = pytz.timezone('Europe/Moscow')

bot = telebot.TeleBot('341599162:AAGJ8Obr--SqMNRGLn9_D6Vlf9l_scyjNoQ')
condition = {}
search_result = []


class Kor:
    def __init__(self):
        self.apt = -1
        self.tov = Counter()

    def sec_apt(self, apt):
        self.apt = apt

    def add_tov(self, tov, amount):
        self.tov[tov] += amount

    def print_cor(self):
        res = []
        if len(self.tov) > 0:
            res.append('Корзина в аптеке ' + str(self.apt))
            for s in self.tov:
                res.append(str(med[s]['name']) + ' в количестве ' + str(self.tov[s]) + " штук")
            return res
        else:
            res.append("У вас в корзине ничего нет")
            return res


kor = {}


@bot.message_handler(commands=['start'])
def start(message):
    condition[message.from_user.id] = 'base'
    kor[message.from_user.id] = Kor()
    bot.send_message(message.from_user.id, 'Бот создан для заказа лекарств')
    back_to_main(message.from_user.id)


@bot.message_handler(content_types=['text'])
def start(message):
    global condition
    if message.from_user.id not in condition:
        condition[message.from_user.id] = 'base'
        kor[message.from_user.id] = Kor()
    if condition[message.from_user.id] == 'start':
        bot.send_message(message.from_user.id, 'Привет')
        bot.send_message(message.from_user.id, text='Выбирете опцию', reply_markup=create_keyboard())
    elif condition[message.from_user.id] == 'base':
        bot.send_message(message.from_user.id, text='Выбирете опцию', reply_markup=create_keyboard())
    elif condition[message.from_user.id] == 'search':
        search(message)
    elif condition[message.from_user.id] == 'choose_apt':
        pass
    elif condition[message.from_user.id] == 'corsina':
        pass
    elif condition[message.from_user.id] == 'choose':
        pass


def create_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    key_choose_apt = types.InlineKeyboardButton(text='Выбрать аптеку', callback_data='choose_apt')
    keyboard.add(key_choose_apt)
    key_search = types.InlineKeyboardButton(text='Поиск', callback_data='search')
    keyboard.add(key_search)
    key_kor = types.InlineKeyboardButton(text='Посмотреть корзину', callback_data='kor')
    keyboard.add(key_kor)
    return keyboard


def choose_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    for i in search_result:
        keyboard.add(types.InlineKeyboardButton(text='Аптека ' + str(i), callback_data='apt' + str(i)))
    keyboard.add(back_button())
    return keyboard


def search(message):
    global search_mes
    global condition
    global kor
    search_mes = message
    condition[message.from_user.id] = 'choose'
    if kor[message.from_user.id].apt == -1:
        search_in_all_aptekas(message.from_user.id, message.text)
    else:
        search_in_one_apteka(message.from_user.id, message.text, kor[message.from_user.id].apt)


def search_in_all_aptekas(id, search):
    global search_result
    search_result = list(find_apt(search))
    if len(search_result) > 0:
        bot.send_message(id, text='Вот где мы нашли необходимый товар',
                         reply_markup=choose_keyboard())
    else:
        bot.send_message(id, text='К сожалению такого товара нигде не найдено',
                         reply_markup=choose_keyboard())


def search_in_one_apteka(id, search, apt):
    global search_result
    search_result = list(find_in_apt(search, apt))
    if len(search_result) > 0:
        search_in_apt(id, kor[id].apt)
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Ищем', callback_data='find'))
        keyboard.add(back_button())
        bot.send_message(id, text='К сожалению такого товара не найдено. Попробуем поискать в другом месте?',
                         reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global condition
    global kor
    if call.message.chat.id not in condition:
        condition[call.message.chat.id] = 'base'
        kor[call.message.chat.id] = Kor()
    if call.data == "search":
        if kor[call.message.chat.id].apt > -1:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text='Удалить корзину', callback_data='drop_apt'))
            bot.send_message(call.message.chat.id, 'Вы ищите в аптеке ' + str(kor[call.message.chat.id].apt) +
                             '. Если хотите сбросить корзину и искать во всех аптеках, то нажмите ниже'
                             , reply_markup=keyboard)
        bot.send_message(call.message.chat.id, 'Введите поисковой запрос')
        condition[call.message.chat.id] = 'search'
    elif call.data == "choose_apt":
        keyboard = types.InlineKeyboardMarkup()
        for i in range(len(sapt)):
            keyboard.add(types.InlineKeyboardButton(text='Аптека ' + str(i), callback_data='choose_apteka;' + str(i)))
        keyboard.add(types.InlineKeyboardButton(text='Вернуться назад', callback_data='back_to_main'))
        bot.send_message(call.message.chat.id, 'Выберете аптеку', reply_markup=keyboard)
        condition[call.message.chat.id] = 'choose_apt'
    elif call.data == "kor":
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Удалить корзину', callback_data='drop_apt'))
        keyboard.add(types.InlineKeyboardButton(text='Редактировать корзину', callback_data= 'change_corsina'))
        keyboard.add(types.InlineKeyboardButton(text='Оформить заказ', callback_data='send_order'))
        keyboard.add(back_button())
        condition[call.message.chat.id] = 'corsina'
        bot.send_message(call.message.chat.id, '\n'.join(kor[call.message.chat.id].print_cor()), reply_markup=keyboard)
    elif call.data[:3] == 'apt':
        num = int(call.data[3:])
        search_in_apt(call.message.chat.id, num)
    elif call.data[:3] == 'add':
        kor[call.message.chat.id].add_tov(int(call.data.split(';')[1]), 1)
        kor[call.message.chat.id].sec_apt(int(call.data.split(';')[2]))
        bot.answer_callback_query(call.id, text="Добавлено в количестве 1 шт. Всего "
                                                + str(kor[call.message.chat.id].tov[int(call.data.split(';')[1])]) + " шт.")
    elif call.data == 'back_to_main':
        back_to_main(call.message.chat.id)
    elif call.data == 'send_offer':
        bot.send_message(call.message.chat.id, text='Ваш заказ сформирован', reply_markup=base_menu())
    elif call.data == 'drop_apt':
        kor[call.message.chat.id] = Kor()
    elif call.data == 'find':
        global search_mes
        search_in_all_aptekas(call.message.chat.id, search_mes.text)
    elif call.data[:8] == 'drop_kor':
        kor[call.message.chat.id] = Kor()
        search_in_apt(call.message.chat.id, int(call.data.split(';')[1]))
    elif call.data.startswith('choose_apteka'):
        kor[call.message.chat.id].sec_apt(int(call.data.split(';')[1]))
        back_to_main(call.message.chat.id)
    elif call.data == 'change_corsina':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(back_button())
        condition[call.message.chat.id] = 'corsina'
        bot.send_message(call.message.chat.id, kor[call.message.chat.id].print_cor()[0], reply_markup=keyboard)
        for j, i in enumerate(kor[call.message.chat.id].tov):
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text='Удалить 1 шт.', callback_data='change_corsina;' + str(i)))
            bot.send_message(call.message.chat.id, kor[call.message.chat.id].print_cor()[j + 1], reply_markup=keyboard)
    elif call.data.startswith('change_corsina'):
        change_corsina(call.message.chat.id, call.data, call.id)


def base_menu():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(back_button())
    return keyboard


def back_to_main(id):
    global condition
    condition[id] = 'base'
    bot.send_message(id, text='Выбирете опцию', reply_markup=create_keyboard())

def search_in_apt(id, num):
    bot.send_message(id, "Вот что мы нашли в апетке " + str(num) + " по вашему запросу")
    global search_mes
    global kor
    global condition
    condition[id] = 'base'
    p = find_in_apt_num_best(search_mes.text, num)
    if num == kor[id].apt or kor[id].apt == -1:
        for n, i in enumerate(give_names(p)):
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text='Добавить в корзину', callback_data='add;' + str(p[n]) + ';'
                                                                                             + str(num)))
            bot.send_message(id, text=i + '\n' + 'Осталось ' + str(int(sapt[num][p[n]]['amount']))
                             + ' по цене ' + str(sapt[num][p[n]]['price']), reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Удалить корзину', callback_data='drop_kor;' + str(num)))
        bot.send_message(id, text='У нас есть корзина в другой аптеке, поэтому добавлять отсюда вы не можете',
                         reply_markup=keyboard)
        for n, i in enumerate(find_in_apt(search_mes.text, num)[0:5]):
            bot.send_message(id, text=i + '\n' + 'Осталось ' + str(int(sapt[num][p[n]]['amount']))
                             + ' по цене ' + str(sapt[num][p[n]]['price']))
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Искать в других аптеках', callback_data='find'))
    keyboard.add(back_button())
    bot.send_message(id, text='Меню', reply_markup=keyboard)


def change_corsina(id, st, id_c):
    global kor
    if len(st) > len('change_corsina'):
        num = int(st.split(';')[1])
        if kor[id].tov[num] > 0:
            kor[id].tov[num] -= 1
            if kor[id].tov[num] == 0:
                kor[id].tov.pop(num)
            bot.answer_callback_query(id_c, text="Удалено в количестве 1 шт. Осталось " + str(kor[id].tov[num]) + " шт.")
        else:
            bot.answer_callback_query(id_c, text="В корзине ничего не осталось")




def back_button():
    return types.InlineKeyboardButton(text='Вернуться на главную', callback_data='back_to_main')


bot.polling(none_stop=True, interval=0)
