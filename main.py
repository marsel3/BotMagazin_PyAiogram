import datetime
import random
import sqlite3
from telebot import types
import telebot



flag1, flag2, flag3 = False, False, False

def main():
    TOKEN = "1672438859:AAFjoueNYWY2ZwUM1UqNIBC_USPJ2N4hE48"
    bot = telebot.TeleBot(TOKEN)


    def clients():
        conn = sqlite3.connect('db/demo_base.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM client')
        results = cursor.fetchall()

        m1=[[i[1] for i in results] + [i[2] for i in results]]

        return m1[0]
    def infclients(name):
        conn = sqlite3.connect('db/demo_base.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM client where fio="{name}" or passport="{name}"')
        results = cursor.fetchall()
        string=(f'Клиент с введёнными данными найден. Информация о нём представлена ниже:  \n\nФИО: {results[0][1]} '
                f'\nПаспортные данные: {results[0][2]} \nИспользуемые авиалинии: '
                f'{results[0][3]} \nСтрана вылета: {results[0][4]} \nСтрана прилета: {results[0][5]}')
        return string

    def hotel():
        conn = sqlite3.connect('db/demo_base.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Hotel')
        results = cursor.fetchall()

        m1=[[i[1] for i in results] + [i[2] for i in results]]

        return m1[0]

    def infhotel(name):
        conn = sqlite3.connect('db/demo_base.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM Hotel where Nick="{name}"')
        results = cursor.fetchall()
        string=(f'Отель с введенными данными найден. Информация о данном отеле представлена ниже: \n\nНазвание отеля: '
                f'{results[0][1]} \nПрестижность отеля(Количество звёзд): {results[0][2]}')
        return string

    def avia():
        conn = sqlite3.connect('db/demo_base.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM avia')
        results = cursor.fetchall()

        m1=[[i[1] for i in results] + [i[2] for i in results]]

        return m1[0]
    def infavia(name):
        conn = sqlite3.connect('db/demo_base.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM avia where Plane="{name}" or Nick="{name}"')
        results = cursor.fetchall()
        string=(f'Авиалиния с введенными данными найдена. Информация о данной авиалинии представлена ниже: '
                f'\n\nНазвание авиалинии: {results[0][2]} \nМодель самолёта: {results[0][1]}')
        return string

    @bot.message_handler(commands=['start']) # /start главная страница бота
    def start_message(message):
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

        markup.add(types.KeyboardButton('Главная страница'))
        bot.send_message(message.chat.id, 'Добро пожаловать, ' + message.from_user.first_name, reply_markup=markup)
        bot.send_message(message.chat.id, 'Какая информация вас интересует?', reply_markup=markup)
        bot.send_message(message.chat.id, 'Для начала нажмите кнопку "Главная страница"', reply_markup=markup)

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        global flag1, flag2, flag3
        main_menu = types.InlineKeyboardMarkup(row_width=1)
        if message.text == "Главная страница":
            main_menu.add(
            types.InlineKeyboardButton(text='Информация о нас', callback_data='info'),
            types.InlineKeyboardButton(text='Помощь', callback_data='help'),
            types.InlineKeyboardButton(text='Поиск информации о Клиенте', callback_data='client'),
            types.InlineKeyboardButton(text='Поиск информации об Авиалинии', callback_data='avia'),
            types.InlineKeyboardButton(text='Поиск информации об Отеле', callback_data='hotel'),
            )
            bot.send_message(message.chat.id, 'Выберите искомый вариант', reply_markup=main_menu)
        if (message.text in clients()) and flag1:
            bot.send_message(message.chat.id, infclients(message.text))
            flag1 = False
        if not (message.text in clients()) and flag1:
            bot.send_message(message.chat.id, 'Человек с введенными данными не найден. Проверьте правильность ввода ' 
                                              'и попробуйте еще раз')
            flag1 = False
        if (message.text in avia()) and flag2:
            bot.send_message(message.chat.id, infavia(message.text))
            flag2 = False
        if not (message.text in avia()) and flag2:
            bot.send_message(message.chat.id, 'Данная авиалинии не является партнером турфирмы или её не существует. '
                                              'Проверьте правильность ввода и попробуйте еще раз')
            flag2 = False
        if (message.text in hotel()) and flag3:
            bot.send_message(message.chat.id, infhotel(message.text))
            flag3 = False
        if not (message.text in hotel()) and flag3:
            bot.send_message(message.chat.id, 'Данный отель не является партнером турфирмы или её не существует. '
                                              'Проверьте правильность ввода и попробуйте еще раз')
            flag3 = False

    @bot.callback_query_handler(func=lambda call: True)
    def handler_call(call):
        global flag1, flag2, flag3
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        user_id = call.message.chat.id

        if call.data == 'info': # Инфа
            bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text='Информация о туристической фирме "ANEX Tour" \n\nКонтактный центр: \n\nДля туристов: '
            '8 (800) 775-50-00 (бесплатно, с 07:00 до 22:00 ) \n\nОперационные отделы:'
            '\nДля журналистов: pr@anextour.com \nПо вопросам работы сайта: getsupport@anextour.com'
            '\nПо вопросам трудоустройства: personal@anextour.com \nСлужба поддержки (для туристов): '
            'cc@anextour.com \nФранчайзинг: fta@anextour.com'
            '\n\nКонтакты центрального офиса: '
            '\n\n127018, г. Москва, ул. Двинцев, д. 12, к. 1, эт. 8, ком. 8 (часть)'
            '\n\n График работы: \n\nПн-Пт: 10:00 - 19:00 \n\nСб, Вс: Закрыто'
            )
        if call.data == 'help': # хелпа
            bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text='При возникновении проблем при работе данного \ntelegram-бота обращаться по контактным данным'
            '\nTelegram: @zarex4555 \nПочта: dinar.yamaletdinov@mgmail.com \nТелефон: 8-937-317-51-43'
            '\nВконтакте: https://vk.com/zarex007'
            )

        if call.data == 'client':
            bot.send_message(chat_id, 'Введите ФИО клиента или его паспортные данные: ')
            flag1 = True
        if call.data == 'avia':
            bot.send_message(chat_id, 'Список авиалиний-партнеров: S7airlines, Победа.'
                                      '\n\nВведите название требуемой авиалинии или название их самолёта: ')
            flag2 = True
        if call.data == 'hotel':
            bot.send_message(chat_id, 'Список отелей-партнеров: Holiday, Huyat.'
                                      '\n\nВведите название требуемого отеля: ')
            flag3 = True

    bot.polling(none_stop=True)

main()