import os
import sqlite3
import urllib.request

from telebot import types
import telebot



flag1, flag2, flag3 = False, False, False


def all_tovar_id():  # Список всех товаров по id
    category = types.InlineKeyboardMarkup(row_width=1)

    conn = sqlite3.connect('db/date_base.db')
    cursor = conn.cursor()
    cursor.execute('SELECT tovar_id FROM tovars')
    results = cursor.fetchall()

    return [str(i[0]) for i in results]



def main():
    TOKEN = "1672438859:AAFjoueNYWY2ZwUM1UqNIBC_USPJ2N4hE48"
    bot = telebot.TeleBot(TOKEN)
    all_tov_id = all_tovar_id()

    def categories():  #Выводит кнопки из таблицы category текст=название
        category = types.InlineKeyboardMarkup(row_width=1)

        conn = sqlite3.connect('db/date_base.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM category')
        results = cursor.fetchall()

        btns = [types.InlineKeyboardButton(text=f'{i[1]}', callback_data=f'{i[0]}') for i in results]
        category.add(*btns)

        return category


    def category_list():    #Список всех категорий по
        category = types.InlineKeyboardMarkup(row_width=1)

        conn = sqlite3.connect('db/date_base.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM category')
        results = cursor.fetchall()

        return [i[0] for i in results]



    def tov_in_category(category): #Выводит товары в кнопки по категории
        conn = sqlite3.connect('db/date_base.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT tovar_id, name_tov, price_tov FROM tovars WHERE cat_id="{category}"')
        results = cursor.fetchall()
        markup = types.InlineKeyboardMarkup(row_width=1)
        btns = [types.InlineKeyboardButton(text=f'{i[1]} \t{i[2]} рублей', callback_data=f'{i[0]}') for i in results]
        markup.add(*btns, types.InlineKeyboardButton(text=f'Назад', callback_data=f'back_to_cat'))

        return markup


    def card_info(id):  # Выводит инфу по карточке
        conn = sqlite3.connect('db/date_base.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT name_tov, price_tov, disc_tov, photo_tov FROM tovars WHERE tovar_id="{id}"')
        results = cursor.fetchall()[0]

        if len(results) == 4:
            markup = types.InlineKeyboardMarkup(row_width=1)
            btns = [types.InlineKeyboardButton(text=f'Назад', callback_data=f'back_to_cat'),
                    types.InlineKeyboardButton(text=f'Купить', callback_data=f'add_to_basket')]
            markup.add(*btns)

            string = f'{results[0]}\n\nЦена: {results[1]} рублей\n{results[2]}'
            # img = open(f"images/{results[3]}", "rb").close()
            urllib.request.urlretrieve(f"{results[3]}", "images/photo.png")
            img = open('images/photo.png', 'rb')

            return string, img, markup


    def search_in_basket(user):
        conn = sqlite3.connect('db/users.db')
        cursor = conn.cursor()
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS "{user}"(tov_id text, name_tov text, price_tov text)""")

        cursor.execute(f'SELECT * FROM "{user}"')
        results = cursor.fetchall()

        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text=f'Оформить заказ', callback_data=f'arrange'))

        string = 'Корзина:\n'
        summ = 0
        if len(results) > 0:
            for i in results:
                string += f"\n{i[1]} \t{i[2]} рублей"
                summ += int(i[2])
            string += '\n________________' + '_' * len(str(summ))
        string += f'\nИтого: {summ} рублей'

        return string, markup


    @bot.message_handler(commands=['start'])  # /start главная страница бота
    def start_message(message):
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

        btns = [types.KeyboardButton('📋 Категории'),
                types.KeyboardButton('🛒 Корзина'),
                types.KeyboardButton('Оформить заказ  ➡'),
                types.KeyboardButton('💬 Помощь')]

        markup.add(*btns)
        bot.send_message(message.chat.id,
                         message.from_user.first_name + ', добро пожаловать в наш интернет-магазин электроники!',
                         reply_markup=markup)
        bot.send_message(message.chat.id, 'Чтобы посмотреть каталог товаров нажмите на кнопку "Категории"',
                         reply_markup=markup)



    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        global flag1, flag2, flag3

        if message.text == "📋 Категории" or message.text.lower() == "категории":
            bot.send_message(message.chat.id, 'Выберите категорию товара', reply_markup=categories())

        if message.text == "🛒 Корзина" or message.text.lower() == "корзина":
            user_id = message.from_user.id
            text, markup = search_in_basket(user_id)
            bot.send_message(message.chat.id, text, reply_markup=markup)


        if message.text == "Оформить заказ  ➡" or message.text.lower() == "оформить заказ":
            pass

        if message.text == "💬 Помощь" or message.text.lower() == "помощь":
            bot.send_message(message.chat.id, 'При возникновении проблем при работе данного telegram-бота '
                                              'обращаться по контактным данным:\nTelegram: @insaf'
                                              '\nПочта: insaf@gmail.com \nТелефон: 2-31-54')



    @bot.callback_query_handler(func=lambda call: True)
    def handler_call(call):
        global flag1, flag2, flag3
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        user_id = call.message.chat.id

        if call.data == 'back_to_cat':
            bot.delete_message(chat_id, message_id)
            bot.send_message(chat_id, 'Выберите категорию товара', reply_markup=categories())

        if call.data in category_list():
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Выберите нужный товар',
                reply_markup=tov_in_category(call.data))

        if call.data in all_tov_id:
            string, img, markup = card_info(call.data)
            bot.delete_message(chat_id, message_id)
            bot.send_photo(chat_id, photo=img, caption=string, reply_markup=markup)
            try:
                img.close()
                os.remove('images/photo.png')
            except:
                print('Фото не удалено!')

        if call.data == 'add_to_basket':
            bot.delete_message(chat_id, message_id)
            bot.send_message(chat_id, 'Нахуй иди! Не продаётся)')

        if call.data == 'arrange':
            bot.delete_message(chat_id, message_id)
            bot.send_message(chat_id, 'Нахуй иди! Не продаётся)')

    bot.polling(none_stop=True)

main()