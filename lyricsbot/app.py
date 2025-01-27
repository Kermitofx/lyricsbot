"""
Custom implementation of Telegram Bot.
"""
import os

from flask import Flask, request
import telebot
from telebot import types
from telebot.apihelper import ApiException

try:
    from config import TOKEN  # pylint: disable=relative-import
    from database_settings import (  # pylint: disable=relative-import
        create_song_data_table,
        create_user_state_table,
        get_author_song,
        get_title_song,
        get_user_state,
        insert_chat_id_to_user_state,
        insert_data_to_sd_table,
        update_author_song,
        update_title_song,
        update_user_state,
    )
    from domains.genius.genius import get_song_text_from_genius  # pylint: disable=relative-import
# pylint:disable=bare-except
except:  # noqa: E722 # Python 3.5 does not contain `ModuleNotFoundError`
    from lyricsbot.config import TOKEN
    from lyricsbot.database_settings import (
        create_song_data_table,
        create_user_state_table,
        get_author_song,
        get_title_song,
        get_user_state,
        insert_chat_id_to_user_state,
        insert_data_to_sd_table,
        update_author_song,
        update_title_song,
        update_user_state,
    )
    from lyricsbot.domains.genius.genius import get_song_text_from_genius
# pylint: disable=invalid-name
server = Flask(__name__)

bot = telebot.TeleBot(TOKEN)  # pylint: disable=C0103


@bot.message_handler(commands=['start'])
def msg(message):
    """
    Ações iniciais na primeira mensagem.
    """
    create_user_state_table()
    insert_chat_id_to_user_state(message.chat.id)

    create_song_data_table()
    insert_data_to_sd_table(message.chat.id)

    render_initial_keyboard(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """
    Obter a primeira mensagem, alterar o estado do usuário para 1.
    """
    if call.data == "author":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Escreva a música do autor!"
        )

        update_user_state(call.message.chat.id, 1)


@bot.message_handler(func=lambda message: True)
def handle_request_text(message):
    """
    Obtenha a segunda mensagem, altere o estado do usuário para 2.

    Retorne a música completa do usuário.
    """
    if get_user_state(message.chat.id) == 1:
        get_user_state(message.chat.id)

        bot.send_message(
            message.chat.id, "Escreva o nome da música!"
        )

        update_user_state(message.chat.id, 2)

        author_song = message.text
        update_author_song(author_song, message.chat.id)

    else:
        title_song = message.text
        update_title_song(title_song, message.chat.id)

        author = get_author_song(message.chat.id)
        title = get_title_song(message.chat.id)

        update_user_state(message.chat.id, 0)

        try:
            bot.send_message(
                message.chat.id, get_song_text_from_genius(author, title)
            )
        # Message was too long. Current maximum length is 4096 UTF8 characters
        except ApiException:
            bot.send_message(
                message.chat.id, "A música não está disponível, desculpe."
            )

        render_initial_keyboard(message)


def render_initial_keyboard(message):
    """
    Cria o teclado inline inicial.
    """
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(
        types.InlineKeyboardButton("Letra!", callback_data="author")
    )

    bot.send_message(
        message.chat.id,
        "Se pretender receber letras, prima o botão e siga as instruções: ",
        reply_markup=keyboard
    )


@server.route("/" + TOKEN, methods=['POST'])
def getMessage():  # pylint: disable=C0103
    """
    Update for webhook.
    """
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))]
    )

    return "!", 200


@server.route("/")
def webhook():
    """
    Webhook.
    """
    bot.remove_webhook()
    bot.set_webhook(url="https://intense-harbor-47746.herokuapp.com/" + TOKEN)

    return "!", 200


if __name__ == '__main__':
    if os.environ['ENVIRONMENT'] == 'production':
        server.run(
            host="0.0.0.0",
            port=int(os.environ.get('PORT', 5000))
        )

    if os.environ['ENVIRONMENT'] == 'local':
        bot.polling()
