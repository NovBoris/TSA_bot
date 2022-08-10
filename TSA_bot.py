import telebot
from telebot import types
import itertools
import json
import os

# https://t.me/kafe_demo_test_super_bot
bot = telebot.TeleBot('5460762801:AAF3s7OaQppOF9GjfmNW2Y4IzjIq3MVGIa4')
# Ниже напиши свой ID группу в телеграмме
GROUP_ID = 428955934


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
            if 'Сайт' in button['name']:
                chunked_btn.append(
                    types.InlineKeyboardButton(button['name'],
                                               callback_data=button['id'], url=button['link'])
                )
            else:
                chunked_btn.append(
                    types.InlineKeyboardButton(button['name'],
                                               callback_data=button['id'])
                )
        if len(chunked_btn) == 1:
            keyboard.row(chunked_btn[0])
        elif len(chunked_btn) == 2:
            keyboard.row(chunked_btn[0], chunked_btn[1])
    return keyboard


def generate_message(button):
    msg = ''
    msg += button['to_print']
    return msg


def generate_button_with_photo(button, call, keyboard):
    bot.send_photo(
        chat_id=call.message.chat.id,
        photo=button['photo'],
        caption=generate_message(button),
        reply_markup=keyboard,
        parse_mode='html'
    )


def generate_button_with_link(button, call):
    bot.send_message(
        chat_id=call.message.chat.id,
        text='Дальше',
        reply_markup=get_keyboard(button['next_keyboard']),
        parse_mode='html'
    )


def generate_button(button, call, keyboard):
    bot.send_message(
        chat_id=call.message.chat.id,
        text=generate_message(button),
        reply_markup=keyboard,
        parse_mode='html'
    )


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_photo(message.chat.id,
                   'https://avatars.mds.yandex.net/get-altay/2752367/2a000001719c1fa9a14d22828ab54486364c/XXXL',
                   caption='Здравствуйте, %s!\n\nООО «Топливный сервис авто»'
                           % message.from_user.full_name, reply_markup=get_keyboard('main')
                   )


@bot.message_handler(content_types=['text'])
def direct_message(msg):
    to_send_message = '<b>Новое сообщени от клиента</b>\n'
    to_send_message += '   Имя клиента: <b>%s</b>\n' % str(msg.from_user.full_name)
    to_send_message += '   Имя ID клиента: ' + str(msg.from_user.id)
    to_send_message += '\n   Сообщение: <b>%s</b>\n' % str(msg.text)
    markup = telebot.types.InlineKeyboardMarkup()
    url_client = telebot.types.InlineKeyboardButton(text='Ссылка на клиента',
                                                    url='https://t.me/' + str(msg.from_user.username))
    markup.add(url_client)
    bot.send_message(GROUP_ID, to_send_message, parse_mode='html', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def keyboard_answer(call):
    button = list(filter(lambda btn: call.data == btn['id'], get_all_buttons()))[0]
    keyboard = types.InlineKeyboardMarkup()
    if 'link_name' in button:
        but = types.InlineKeyboardButton(button['link_name'], callback_data=button['id'], url=button['link'])
    else:
        but = types.InlineKeyboardButton('Сайт', callback_data=button['id'], url=button['link'])
    keyboard.add(but)
    if button['link'] != "":
        if 'photo' in button:
            generate_button_with_photo(button, call, keyboard)
            generate_button_with_link(button, call)
        else:
            generate_button(button, call, keyboard)
            generate_button_with_link(button, call)
    elif button['link'] == "":
        if 'photo' in button:
            generate_button_with_photo(button, call, get_keyboard(button['next_keyboard']))
        else:
            generate_button(button, call, get_keyboard(button['next_keyboard']))


if __name__ == '__main__':
    bot.skip_pending = True
    bot.polling(none_stop=True, interval=0)
