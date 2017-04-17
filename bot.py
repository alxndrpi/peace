# -*- coding: utf-8 -*-

import telebot
from telebot import types
from financial_db_worker import helpers
import financial_db_worker.db_worker as fdbw

"""АРТЕМА КУСОК"""

bot = telebot.TeleBot(helpers.token)
conn = fdbw.FDBWorker()
categories = fdbw.CategoriesWorker(conn, 'test_user')
sours = categories.get_categories()
parentButtons = set([x['Parent'] for x in sours])
childButtons = [x['Name'] for x in sours]
type_id = None
conn.close()


# print(dataCategories)
# [print(x['Parent']) for x in dataCategories]
# a = set([x["Parent"] for x in a])
# buttons = {x['Name']: x['Parent'] for x in dataCategories}
# print(buttons)
# [print(x) for x in buttons if x["Parent"] == 'Расчеты за услуги и другие операции']

def first_keyboard(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
    markup.add('Занесение информации о финансовой операции', 'Проверить состояние счета', 'Финансовая отчетность')
    bot.send_message(message.chat.id,
                     'Привет, ' + message.chat.first_name + '\n \n Выберите пункт менюв зависимости от того, что вы хотите получить или сделать',
                     reply_markup=markup)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    conn = fdbw.FDBWorker()
    if not (conn.user_exist(str(message.chat.id))):
        firstSum = bot.send_message(message.chat.id, 'Введите первоначальную сумму перед регистрацией')
        bot.register_next_step_handler(firstSum, regist)
    else:
        first_keyboard(message)
    conn.close()


def regist(message):
    conn = fdbw.FDBWorker()
    conn.create_user(str(message.chat.id), int(message.text))
    first_keyboard(message)


def operation_send(message):
    conn = fdbw.FDBWorker()
    global type_id
    ops = fdbw.OperationsWorker(conn, message.chat.id)
    ops.add_operation(total=message.text, category_id=type_id)
    conn.close()


@bot.message_handler(content_types=["text"])
def keyboard(message):

    if message.text == 'Главное меню':
        first_keyboard(message)

    if message.text == 'Занесение информации о финансовой операции':
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
        markup.add(*[types.KeyboardButton(text=x) for x in parentButtons], 'Главное меню')
        bot.send_message(message.chat.id, 'Выберите вид операции', reply_markup=markup)
        # msg = bot.reply_to(message, 'ну поехали', reply_markup=markup)
        # bot.register_next_step_handler(msg, process_step)  # TODO: погуглить это говно и это bot.set_update_listener()

    if message.text in parentButtons:
        markup = types.ReplyKeyboardMarkup(row_width=1)
        markup.add(*[x['Name'] for x in sours if x['Parent'] == message.text], 'Главное меню')
        bot.send_message(message.chat.id, 'Выберите тип операции', reply_markup=markup)
        # bot.register_next_step_handler(info, hyi)

    if message.text in childButtons:
        global type_id
        for x in sours:
            if x['Name'] == message.text:
                type_id = x['@Categories']
                break
        infoText = bot.send_message(message.chat.id, 'введите сумму')
        bot.register_next_step_handler(infoText, operation_send)

    if message.text == 'Проверить состояние счета':
        conn = fdbw.FDBWorker()
        balance = fdbw.AssetsWorker(conn, message.chat.id)
        balance = balance.get_balance(ids=[5])[0]['CurrentTotal']
        bot.send_message(message.chat.id, "На вашем счете: " + str(balance))
        conn.close()


# print('asdsad')
# bot.send_message()
##ИНТЕРЕЕЕЕЕЕСНО!
# mark = types.ReplyKeyboardMarkup(one_time_keyboard=True)
# a = types.KeyboardButton(text='asdasd',request_location=True)
# mark.add(a)
# bot.send_message(chat_id,text='asdas', reply_markup=mark)
#
# elif message.text == 'Приобретение материалов и товаров':
#     markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
#     markup.add(*[x for x in buttons.keys() if buttons.values() == message.chat.id])
# elif message.text == 'Кредиты и другие долги':
#     markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
#     markup.add(*[x for x in buttons.keys() if buttons.values() == message.chat.id])
# elif message.text == 'Оплаты от дебиторов/покупателей':
#     markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
#     markup.add(*[x for x in buttons.keys() if buttons.values() == message.chat.id])
#     # f = open('m.ogg', 'rb')
#     # bot.send_audio(message.chat.id, f, """this place isn't yours anymore""")


# @bot.message_handler(content_types=["text"])
# def trak(message):
#     # for file in os.listdir("music"):
#     #     if file.split(".")[-1] == "ogg":
#     #         f = open('music/' + file, 'rb')
#     #         res = bot.send_voice(message.chat.id, f, None)
#     # time.sleep(3)
#
#     # bot.send_message(message.chat.id, text="Однако ты пидор")
#     print(message.text)
#     print(message)
#     # print(message.last_name)
if __name__ == '__main__':
    bot.polling(none_stop=True)