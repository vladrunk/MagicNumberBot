from os import environ

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = TeleBot(environ['BOT_TOKEN'])
CARDS_TOTAL_NUMBERS = 5


def generate_cards(degree: int) -> list:
    limit = sum([2 ** _ for _ in range(0, degree)])
    cards = [[] for _ in range(0, degree)]
    for _ in range(1, limit + 1):
        for index, value in enumerate(bin(_)[2:][::-1]):
            if int(value):
                cards[index].append(_)
    for index, card in enumerate(cards):
        i, j = 0, 4
        temp = []
        while j <= len(card):
            temp.append(
                ' '.join([str(_) for _ in card[i:j]])
            )
            i, j = j, j + 4
        cards[index] = '\n'.join([_ for _ in temp])

    return cards


CARDS = generate_cards(CARDS_TOTAL_NUMBERS)


def kbrd_start() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton('Я загадал', callback_data='cb_start'))
    return markup


def kbrd_answer(next_card: int, answer: str = '') -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('Да', callback_data=f'cb_ans_yes|{answer}|{next_card}'),
               InlineKeyboardButton('Нет', callback_data=f'cb_ans_no|{answer}|{next_card}'))
    return markup


def send_card_to_chat(m, cur_card: int, answer: str = ''):
    card = CARDS[cur_card]
    bot.edit_message_text(
        chat_id=m.chat.id,
        message_id=m.message_id,
        text=f'В списке ниже есть твоё число?\n\nСписок №{cur_card + 1}\n`{card}`',
        parse_mode='Markdown',
        reply_markup=kbrd_answer(next_card=cur_card + 1, answer=answer),
    )


def calc_result(m, answer: str):
    answer = sum([2 ** i for i, v in enumerate(answer) if v == '1'])
    bot.edit_message_text(
        chat_id=m.chat.id,
        message_id=m.message_id,
        text=f'Твоё число: **{answer}**\n\nЗагадай число от 1 до 31',
        parse_mode='Markdown',
        reply_markup=kbrd_start(),
    )


@bot.callback_query_handler(func=lambda call: 'cb_ans' in call.data)
def cb_next_card(call):
    _, answer, next_card = call.data.split('|')
    next_card = int(next_card)
    answer += '1' if _.split('_')[2] == 'yes' else '0'
    if next_card < CARDS_TOTAL_NUMBERS:
        send_card_to_chat(call.message, next_card, answer)
    else:
        calc_result(call.message, answer)


@bot.callback_query_handler(func=lambda call: call.data == 'cb_start')
def cb_start(call):
    send_card_to_chat(call.message, 0)


@bot.message_handler(commands=['start'])
def cmd_start(m):
    bot.send_message(
        chat_id=m.chat.id,
        text='Загадай число от 1 до 31',
        reply_markup=kbrd_start(),
    )


if __name__ == '__main__':
    bot.polling(none_stop=True)
