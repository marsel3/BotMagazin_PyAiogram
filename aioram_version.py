import os
import sqlite3
import urllib.request

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def all_tovar_id():  # Список всех товаров по id

    conn = sqlite3.connect('db/date_base.db')
    cursor = conn.cursor()
    cursor.execute('SELECT tovar_id FROM tovars')
    results = cursor.fetchall()
    conn.close()

    return [str(i[0]) for i in results]



bot = Bot(token="1672438859:AAFjoueNYWY2ZwUM1UqNIBC_USPJ2N4hE48")
dp = Dispatcher(bot)

number = 1
tovar_id = ''
delFlag = False
all_tov_id = all_tovar_id()



@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btns = [KeyboardButton('📋 Категории'),
            KeyboardButton('🛒 Корзина'),
            KeyboardButton('Оформить заказ  ➡'),
            KeyboardButton('💬 Помощь')]
    markup.add(*btns)

    await message.answer(str(message.from_user.first_name) + ', добро пожаловать в наш интернет-магазин электроники!')
    await message.answer('Чтобы посмотреть каталог товаров нажмите на кнопку \n"📋 Категории"', reply_markup=markup)


@dp.message_handler()
async def echo_message(message: types.Message):
    global number

    if message.text == "📋 Категории" or message.text.lower() == "категории":
        number = 1
        await bot.send_message(message.from_user.id, 'Выберите категорию товара:\n', reply_markup=category())

    if message.text == "🛒 Корзина" or message.text.lower() == "корзина":
        user_id = message.from_user.id
        text, markup = search_in_basket(user_id, 'Корзина:\n')
        await bot.send_message(message.chat.id, text, reply_markup=markup)

    if message.text == "Оформить заказ  ➡" or message.text.lower() == "оформить заказ":
        inline_kb_full = InlineKeyboardMarkup(row_width=3)
        btns = [InlineKeyboardButton('➖', callback_data='minus'),
                InlineKeyboardButton(f'{number}', callback_data='call_number'),
                InlineKeyboardButton('➕', callback_data='plus')]
        inline_kb_full.add(*btns)
        await message.reply("Первая инлайн кнопка", reply_markup=inline_kb_full)

    if message.text == "💬 Помощь" or message.text.lower() == "помощь":
        await bot.send_message(message.chat.id, 'При возникновении проблем при работе данного telegram-бота '
                                          'обращаться по контактным данным:\nTelegram: @insaf'
                                          '\nПочта: insaf@gmail.com \nТелефон: 2-31-54')




@dp.callback_query_handler(lambda c: c.data and c.data.startswith('edit_'))
async def process_callback_kb1btn1(call: types.CallbackQuery):
    global number

    code = call.data[5:]
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.message.chat.id

    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT count_tov FROM "{user_id}" WHERE tov_id="{code}"')
    results = cursor.fetchall()
    conn.close()

    number = int(results[0][0])

    markup = types.InlineKeyboardMarkup()
    btns = [InlineKeyboardButton(text=f'➖', callback_data=f'minus'),
            InlineKeyboardButton(text=f'{number}', callback_data=f'call_number'),
            InlineKeyboardButton(text=f'➕', callback_data=f'plus')]

    markup.add(*btns)
    markup.add(InlineKeyboardButton(text=f'✔', callback_data=f'confirm'))
    markup.add(InlineKeyboardButton(text=f'Удалить', callback_data=f'del_cat_basket'))

    string = card_info(code)[0]

    await bot.delete_message(chat_id, message_id)
    await bot.send_message(chat_id, string, reply_markup=markup)




@dp.callback_query_handler(lambda c: c.data)
# async def answer(call: types.CallbackQuery, message: types.Message):
async def answer(call: types.CallbackQuery):
    global number, delFlag, tovar_id

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.message.chat.id

    if call.data == 'back_to_cat':
        await bot.delete_message(chat_id, message_id)
        await bot.send_message(chat_id, 'Выберите категорию товара',  reply_markup=category())


    if call.data in category_list():
        number = 1
        await bot.edit_message_reply_markup(chat_id, message_id,
                                            'Выберите нужный товар',
                                            reply_markup=tov_in_category(call.data))

    if call.data in all_tov_id:
        if delFlag:
            delFlag = False
            edit_basket(user_id, call.data)

            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton(text=f'Оформить заказ', callback_data=f'arrange'),
                       types.InlineKeyboardButton(text=f'Изменить корзину', callback_data=f'edit_basket'))

            await bot.edit_message_text(chat_id, message_id,
                                        search_in_basket(user_id, 'Корзина:\n')[0],
                                        reply_markup=markup)
        else:
            string, img, markup = card_info(call.data)
            tovar_id = call.data


            await bot.delete_message(chat_id, message_id)
            await bot.send_photo(chat_id, photo=img, caption=string, reply_markup=markup)

            img.close()
            try:
                os.remove('images/photo.png')
            except:
                print('Фото не удалено!')


    if call.data == 'add_to_basket':
        add_to_basket(user_id, tovar_id, number)
        await bot.delete_message(chat_id, message_id)
        await bot.send_message(chat_id, 'Товар добавлен в корзину!\nВыберете что-то ещё?', reply_markup=category())
        number = 1
        print('Товар добавлен в корзину!')


    if call.data == 'arrange':  # Офтормить заказ
        await bot.edit_message_text(chat_id, message_id,
                                    'Нахуй иди! Не продаётся)')



    if call.data == 'minus':
        if number > 0:
            number -= 1
            call.message.reply_markup.inline_keyboard[0][1].text = number
            await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=call.message.reply_markup)

    if call.data == 'plus':
        number += 1
        call.message.reply_markup.inline_keyboard[0][1].text = number
        await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=call.message.reply_markup)

    if call.data == 'confirm':
        edit_confirm(user_id, number, tovar_id)

        text, markup = search_in_basket(user_id, 'Корзина:\n')
        await bot.send_message(chat_id, text, reply_markup=markup)


    if call.data == 'del_cat_basket':
        del_cat_basket(user_id, tovar_id)
        text, markup = search_in_basket(user_id, 'Корзина:\n')
        await bot.send_message(chat_id, text, reply_markup=markup)





# Функции

def category():  # Выводит кнопки из таблицы category текст=название
    conn = sqlite3.connect('db/date_base.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM category')
    results = cursor.fetchall()
    conn.close()

    markup = types.InlineKeyboardMarkup(row_width=1)
    btns = [InlineKeyboardButton(text=f'{i[1]}', callback_data=f'{i[0]}') for i in results]
    markup.add(*btns)

    return markup




def category_list():  # Список всех категорий по
    conn = sqlite3.connect('db/date_base.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM category')
    results = cursor.fetchall()
    conn.close()
    return [i[0] for i in results]


def tov_in_category(category):  # Выводит товары в кнопки по категории
    conn = sqlite3.connect('db/date_base.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT tovar_id, name_tov, price_tov FROM tovars WHERE cat_id="{category}"')
    results = cursor.fetchall()
    conn.close()

    markup = types.InlineKeyboardMarkup(row_width=1)
    btns = [InlineKeyboardButton(text=f'{i[1]} \t{i[2]} рублей', callback_data=f'{i[0]}') for i in results]
    markup.add(*btns, InlineKeyboardButton(text=f'Назад', callback_data=f'back_to_cat'))
    return markup


def card_info(id):  # Выводит инфу по карточке
    global number
    conn = sqlite3.connect('db/date_base.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT name_tov, price_tov, disc_tov, photo_tov FROM tovars WHERE tovar_id="{id}"')

    results = cursor.fetchall()[0]

    if len(results) > 0:
        markup = types.InlineKeyboardMarkup()
        btns = [InlineKeyboardButton(text=f'➖', callback_data=f'minus'),
                InlineKeyboardButton(text=f'{number}', callback_data=f'call_number'),
                InlineKeyboardButton(text=f'➕', callback_data=f'plus')]
        markup.add(*btns)
        markup.add(InlineKeyboardButton(text=f'Купить', callback_data=f'add_to_basket'))
        markup.add(InlineKeyboardButton(text=f'Назад', callback_data=f'back_to_cat'))

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
    cursor.execute(
        f"""CREATE TABLE IF NOT EXISTS "{user}" (tov_id text, name_tov text, price_tov text, count_tov text)""")



def search_in_basket(user, string):
    create_user_bd(user)

    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM "{user}"')
    results = cursor.fetchall()
    conn.close()
    print(results)
    markup = types.InlineKeyboardMarkup(resize_button=True)
    for i in results:
        btns = [InlineKeyboardButton(text=f'{i[1]}', callback_data=f'{i[0]}'),
              InlineKeyboardButton(text=f'{i[3]} шт.', callback_data=f'edit_{i[0]}'),
              InlineKeyboardButton(text=f'✏', callback_data=f'edit_{i[0]}')]
        markup.add(*btns)

    markup.add(InlineKeyboardButton(text=f'Оформить заказ', callback_data=f'arrange'))

    summ = 0
    count = 1
    if len(results) > 0:
        for i in results:
            string += f"\n{count}.  {i[1]} \n{i[2]} *{i[3]}  =  {int(i[2]) * int(i[3])} рублей"
            summ += (int(i[2]) * int(i[3]))
            count += 1
        string += '\n________________' + '_' * len(str(summ))
    string += f'\nИтого: {summ} рублей'

    return string, markup


def add_to_basket(user, tov_id, count):  # Добавление в БД юзера
    create_user_bd(user)

    conn = sqlite3.connect('db/date_base.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT tovar_id, name_tov, price_tov FROM tovars WHERE tovar_id="{tov_id}"')
    results = cursor.fetchall()[0]
    conn.close()


    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT count_tov FROM "{user}" WHERE tov_id="{tov_id}"')
    results_2 = cursor.fetchall()
    if len(results_2) > 0:
        count = str(int(count) + int(results_2[0][0]))
        cursor.execute(f'DELETE FROM "{user}" where tov_id="{tov_id}"')
    cursor.execute(f'INSERT INTO "{user}" VALUES ("{results[0]}", "{results[1]}", "{results[2]}", {count})')
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


def del_cat_basket(user, tov_id):
    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM "{user}" WHERE tov_id="{tov_id}"')
    conn.commit()
    conn.close()



def edit_confirm(user, number, tov_id):
    if number == 0:
        del_cat_basket(user, tov_id)
    else:
        conn = sqlite3.connect('db/users.db')
        cursor = conn.cursor()
        cursor.execute(f'UPDATE "{user}" SET count_tov="{number}" WHERE tov_id="{tov_id}"')
        conn.commit()
        conn.close()




if __name__ == '__main__':
    executor.start_polling(dp)