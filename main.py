import os
import sqlite3
import urllib.request

from telebot import types
import telebot

tovar_id = ''
number = 1
delFlag = False


def all_tovar_id():  # Список всех товаров по id
    category = types.InlineKeyboardMarkup(row_width=1)

    conn = sqlite3.connect('db/date_base.db')
    cursor = conn.cursor()
    cursor.execute('SELECT tovar_id FROM tovars')
    results = cursor.fetchall()
    conn.close()

    return [str(i[0]) for i in results]




def main():
    TOKEN = "1672438859:AAFjoueNYWY2ZwUM1UqNIBC_USPJ2N4hE48"
    bot = telebot.TeleBot(TOKEN)
    all_tov_id = all_tovar_id()



    def categories():    # Выводит кнопки из таблицы category текст=название
        conn = sqlite3.connect('db/date_base.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM category')
        results = cursor.fetchall()
        conn.close()

        markup = types.InlineKeyboardMarkup(row_width=1)
        btns = [types.InlineKeyboardButton(text=f'{i[1]}', callback_data=f'{i[0]}') for i in results]
        markup.add(*btns)

        return markup



    def category_list():    #Список всех категорий по
        conn = sqlite3.connect('db/date_base.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM category')
        results = cursor.fetchall()
        conn.close()

        return [i[0] for i in results]



    def tov_in_category(category): #Выводит товары в кнопки по категории
        conn = sqlite3.connect('db/date_base.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT tovar_id, name_tov, price_tov FROM tovars WHERE cat_id="{category}"')
        results = cursor.fetchall()
        conn.close()

        markup = types.InlineKeyboardMarkup(row_width=1)
        btns = [types.InlineKeyboardButton(text=f'{i[1]} \t{i[2]} рублей', callback_data=f'{i[0]}') for i in results]
        markup.add(*btns, types.InlineKeyboardButton(text=f'Назад', callback_data=f'back_to_cat'))
        return markup



    def card_info(id):  # Выводит инфу по карточке
        global number
        conn = sqlite3.connect('db/date_base.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT name_tov, price_tov, disc_tov, photo_tov FROM tovars WHERE tovar_id="{id}"')
        results = cursor.fetchall()[0]

        if len(results) == 4:
            markup = types.InlineKeyboardMarkup()
            btns = [types.InlineKeyboardButton(text=f'➖', callback_data=f'minus'),
                    types.InlineKeyboardButton(text=f'{number}', callback_data=f'add_to_basket'),
                    types.InlineKeyboardButton(text=f'➕', callback_data=f'plus')]
            markup.add(*btns)
            markup.add(types.InlineKeyboardButton(text=f'Купить', callback_data=f'add_to_basket'))
            markup.add(types.InlineKeyboardButton(text=f'Назад', callback_data=f'back_to_cat'))

            string = ''
            try:
                urllib.request.urlretrieve(f"{results[3]}", "images/photo.png")
                img = open('images/photo.png', 'rb')
            except:
                print(f"Фото {results[0]} не загружено!")
                img = open('images/error.jpg', 'rb')
                string = 'Соощите администратору, что произошла ошибка с загрузкой фото!\n\n\n'

            string += f'{results[0]}\n\nЦена: {results[1]} рублей\n{results[2]}'

            return string, img, markup


    def create_user_bd(user):
        conn = sqlite3.connect('db/users.db')
        cursor = conn.cursor()
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS "{user}" (tov_id text, name_tov text, price_tov text, count_tov text)""")



    def search_in_basket(user, string):
        create_user_bd(user)

        conn = sqlite3.connect('db/users.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM "{user}"')
        results = cursor.fetchall()
        conn.close()

        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(text=f'Оформить заказ', callback_data=f'arrange'),
                   types.InlineKeyboardButton(text=f'Изменить корзину', callback_data=f'edit_basket'))

        summ = 0
        count = 1
        if len(results) > 0:
            for i in results:
                string += f"\n{count}. {i[1]} \t{i[2]} рублей"
                summ += int(i[2])
                count += 1
            string += '\n________________' + '_' * len(str(summ))
        string += f'\nИтого: {summ} рублей'


        return string, markup



    def add_to_basket(user, tov_id): #Добавление в БД юзера
        create_user_bd(user)

        conn = sqlite3.connect('db/date_base.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT tovar_id, name_tov, price_tov FROM tovars WHERE tovar_id="{tov_id}"')
        results = cursor.fetchall()[0]
        conn.close()

        conn = sqlite3.connect('db/users.db')
        cursor = conn.cursor()
        cursor.execute(f'INSERT INTO "{user}" VALUES ("{results[0]}", "{results[1]}", "{results[2]}", 1)')
        conn.commit()
        conn.close()


    def basket_inputs(user):
        create_user_bd(user)

        conn = sqlite3.connect('db/users.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM "{user}"')
        results = cursor.fetchall()
        conn.close()

        markup = types.InlineKeyboardMarkup(row_width=1)
        btns = [types.InlineKeyboardButton(text=f'{i[1]}', callback_data=f'{i[0]}') for i in results]
        markup.add(*btns)

        return markup


    def edit_basket(user, tov_id):
        create_user_bd(user)

        conn = sqlite3.connect('db/users.db')
        cursor = conn.cursor()
        cursor.execute(f'DELETE from "{user}" where tov_id = "{tov_id}"')
        conn.commit()
        conn.close()




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

        if message.text == "📋 Категории" or message.text.lower() == "категории":
            bot.send_message(message.chat.id, 'Выберите категорию товара', reply_markup=categories())

        if message.text == "🛒 Корзина" or message.text.lower() == "корзина":
            user_id = message.from_user.id
            text, markup = search_in_basket(user_id, 'Корзина:\n')
            bot.send_message(message.chat.id, text, reply_markup=markup)


        if message.text == "Оформить заказ  ➡" or message.text.lower() == "оформить заказ":
            pass

        if message.text == "💬 Помощь" or message.text.lower() == "помощь":
            bot.send_message(message.chat.id, 'При возникновении проблем при работе данного telegram-бота '
                                              'обращаться по контактным данным:\nTelegram: @insaf'
                                              '\nПочта: insaf@gmail.com \nТелефон: 2-31-54')



    @bot.callback_query_handler(func=lambda call: True)
    def handler_call(call):
        global tovar_id, delFlag, number

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
            if delFlag:
                delFlag = False
                edit_basket(user_id, call.data)

                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(types.InlineKeyboardButton(text=f'Оформить заказ', callback_data=f'arrange'),
                           types.InlineKeyboardButton(text=f'Изменить корзину', callback_data=f'edit_basket'))

                bot.delete_message(chat_id, message_id)
                bot.send_message(chat_id, search_in_basket(user_id, 'Корзина:\n')[0],
                                 reply_markup=markup)
            else:
                string, img, markup = card_info(call.data)
                tovar_id = call.data

                bot.delete_message(chat_id, message_id)
                bot.send_photo(chat_id, photo=img, caption=string, reply_markup=markup)
                img.close()
                try:
                    os.remove('images/photo.png')
                except:
                    print('Фото не удалено!')


        if call.data == 'add_to_basket':
            bot.delete_message(chat_id, message_id)
            add_to_basket(user_id, tovar_id)
            print('Товар добавлен в корзину!')
            bot.send_message(chat_id, 'Товар добавлен в корзину!')

        if call.data == 'arrange':  # Офтормить заказ
            bot.delete_message(chat_id, message_id)
            bot.send_message(chat_id, 'Нахуй иди! Не продаётся)')


        if call.data == 'edit_basket':
            delFlag = True
            bot.delete_message(chat_id, message_id)
            bot.send_message(chat_id, search_in_basket(user_id, 'Какой товар удалить из корзины?\n')[0],
                             reply_markup=basket_inputs(user_id))

        if call.data == 'minus':
            if number > 1:
                number -= 1

        if call.data == 'plus':
            number += 1


    bot.polling(none_stop=True)


main()