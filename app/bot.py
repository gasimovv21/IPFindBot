import json
import logging
import sqlite3
import sys
import os
import requests
import telegram

from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                            MessageHandler, Updater)

from dotenv import load_dotenv
import exceptions
from constants import ENDPOINT_INFO_IP

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def send_message(bot, message):
    """Отправлем сообещние в телеграм чат."""
    try:
        logging.info('Отправляем сообщение.')
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message)
    except telegram.error.TelegramError as e:
        raise SendMessageError(e) from e


def send_link_for_ip(update, context):
    """Отпрвка IP - адреса через сыллку."""
    chat = update.effective_chat
    context.bot.send_message(
        chat.id,
        text=(
            f'Откройте сыллку чтобы бот получил ваш IP - адрес. http://127.0.0.1:8000/ip-adresse/'
            '\n Еслы вы успешно перешли по сыллке нажмите кнопку - /ip'
            )
        )


def get_ip_from_data_base():
    """Делаем запрос на базу данных для получаение IP - адреса."""
    try:
        sqlite_connection = sqlite3.connect('web-site/mysite/db.sqlite3')
        cursor = sqlite_connection.cursor()
        logging.info('Подключен к SQLite.')

        for value in cursor.execute('SELECT * FROM main_userip'):
            ip = value[1]
        cursor.close()
    except sqlite3.Error as error:
        logging.error("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            logging.info("Соединение с SQLite закрыто")
    return ip


def send_ip(update, context):
    """Отправляем IP - адрес."""
    chat = update.effective_chat
    context.bot.send_message(
        chat.id,
        text=(
            f'Ваш общедоступный IP - адрес: {get_ip_from_data_base()}'
            '\nЕсли вы получили свой IP - адрес, нажав кнопку /ipinfo \nможете узнать доп-информацию об IP - адресе. '
        )
    )


def get_ip_info():
    """Делаем запрос на энд-поинт для получение доп-информации IP - адреса."""
    try:
        response = requests.get(ENDPOINT_INFO_IP.format(get_ip_from_data_base()))
    except Exception as error:
        logging.error(f'Ошибка при запросе к API для получение IP: {error}')
    ip_info = response.text
    return ip_info


def send_ip_info(update, context):
    """Отправляем доп-информацию об IP - адреса."""
    chat = update.effective_chat
    ip_info = json.loads(get_ip_info())
    ip = ip_info['ip']
    city = ip_info['city']
    region = ip_info["region"]
    country = ip_info["country"]
    loc = ip_info["loc"]
    org = ip_info["org"]
    postal = ip_info["postal"]
    timezone = ip_info["timezone"]
    context.bot.send_message(
        chat.id,
        text=(
            f'Дополнительная иформация вашего IP - адреса: '
            f'\nIP - адрес: {ip}'
            f'\nГород : {city}'
            f'\nРегион : {region}'
            f'\nСтрана : {country}'
            f'\nМестоположение : {loc}'
            f'\nИнтернет-провайдер : {org}'
            f'\nПочтовый индекс : {postal}'
            f'\nЧасавой пояс : {timezone}'
            ))


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    buttons = ReplyKeyboardMarkup([['/getlink', '/ipinfo'], ['/ip']], resize_keyboard=True)
    context.bot.send_message(
        chat_id = chat.id,
        text=(
            f'Привет, {name}. Я IPFindBot, я помогу вам узнать ваш IP - адрес.'
            '\nЧтобы получить IP - адрес нажмите на кнопу /getlink'
        ),
        reply_markup=buttons
    )


def check_tokens():
    """Проверка доступности переменных из окружений."""
    return all((TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))

def main():
    """Основная логика работы бота."""
    updater = Updater(token=TELEGRAM_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('getlink', send_link_for_ip))
    updater.dispatcher.add_handler(CommandHandler('ipinfo', send_ip_info))
    updater.dispatcher.add_handler(CommandHandler('ip', send_ip))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    file_handler = logging.FileHandler(
        filename=os.path.join('main.log'),
        mode='w',
        encoding='UTF-8')
    stdout_handler = logging.StreamHandler(sys.stdout)
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler, stdout_handler],
        format=(
            '%(asctime)s, Тип лога - %(levelname)s, строка - %(lineno)d, '
            'Фукнция - %(funcName)s, Директория - %(name)s, '
            'Сообшение - %(message)s')
    )
    main()