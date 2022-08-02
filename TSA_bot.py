import telebot
from telebot import types
import itertools
import json
from prettytable import PrettyTable

# https://t.me/kafe_demo_test_super_bot
bot = telebot.TeleBot('5484593859:AAHu8GsdsvogFXw7-b6GaQOqIr-hy_uGqug')
# Ниже напиши свой ID группу в телеграмме
GROUP_ID = '428955934'


def get_all_buttons():
    with open('content.json', encoding='utf-8') as config:
        config_data = json.load(config)
    all_buttons = []
    for keyboard in config_data:
        for button in keyboard['buttons']:
            all_buttons.append(button)
    return all_buttons


def get_keyboard(keyboard_type):
    with open('content.json', encoding='utf-8') as config:
        config_data = json.load(config)
    kb_info = list(filter(lambda el: el['keyboard_name'] == keyboard_type, config_data))[0]
    buttons = sorted(kb_info['buttons'], key=lambda el: int(el['position']))
    keyboard = types.InlineKeyboardMarkup()
    chunked = list(itertools.zip_longest(*[iter(buttons)] * 2))
    for chunk in chunked:
        chunked_btn = []
        for button in list(filter(lambda el: el is not None, chunk)):
            chunked_btn.append(
                types.InlineKeyboardButton(button['name'],
                                           callback_data=button['id'])
            )
        if len(chunked_btn) == 1:
            keyboard.row(chunked_btn[0])
        elif len(chunked_btn) == 2:
            keyboard.row(chunked_btn[0], chunked_btn[1])
        elif len(chunked_btn) == 3:
            keyboard.row(chunked_btn[0], chunked_btn[1], chunked_btn[2])
    return keyboard


def generate_message(button):
    msg = ''
    msg += button['to_print'] + button['link']
    return msg


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     'Здравствуйте, %s!\n\nООО «Топливный сервис авто»\n\nНаш сайт:\n\nhttps://tsauto.by/' % message.from_user.full_name,
                     reply_markup=get_keyboard('main')
                     )


@bot.message_handler(content_types=['text'])
def direct_message(msg):
    to_send_message = '<b>Новое сообщени от клиента</b>\n'
    to_send_message += '   Имя клиента: <b>%s</b>\n' % str(msg.from_user.full_name)
    to_send_message += '   Имя ID клиента: https://t.me/<b>%s</b>\n' % str(msg.from_user.username)
    to_send_message += '   Сообщение: <b>%s</b>\n' % str(msg.text)
    bot.send_message(GROUP_ID, to_send_message, parse_mode='html')


@bot.callback_query_handler(func=lambda call: True)
def keyboard_answer(call):
    button = list(filter(lambda btn: call.data == btn['id'], get_all_buttons()))[0]
    bot.send_message(
        chat_id=call.message.chat.id,
        text=generate_message(button),
        reply_markup=get_keyboard(button['next_keyboard']),
        parse_mode='html'
    )

if __name__=='__main__':
    bot.skip_pending = True
    bot.polling()
