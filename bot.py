import random
from copy import deepcopy
import telebot
import time
import requests
import json
import re


tones = ["Friendly", "Laxury", "Relaxed", "Professional", "Bold", "Adventurous", "Witty", "Persuasive", "Empathetic"]

level_one_options = ["Instagram Captions", "Hashtags", "Microcopy", "Event Copy", "Question Generator",
                     "Follow Up Email", "Confirmation Emails", "Video Titles", "Carousel Post", "Captions",
                     "Video Intro Hook", "Relatable Experiences", "Brainstorm Topics", "Bullet Points",
                     "Keyword Generator", "Add Emoji to List", "Simplify Sentence", "Verb Booster",
                     "Adjective Accelerator", "Analogy Generator", "Two Sentence Stories", "Hero Story Intro",
                     "Cliffhanger", "Explain In Plain English", "Passive to Active Voice", "Name Generator",
                     "Startup Ideas", "Shower Thoughts", "Clubhouse Bio"]

#
# words = []
# texts = []
# wordind = 0
# words_to_user = []
# text = "Привет лошара, ты гнида псина ебаная"


bot = telebot.TeleBot("2065762700:AAGFhhADZiYuYLfnkyaZzqpPoHgUy37rJro")

win = False

stages = ["_________________",
          "        |        ",
          "        O        ",
          "       /|\       ",
          "       / \       "]


@bot.message_handler(commands=['start', 'help'])
def welcome_message(message):
    keyboard = telebot.types.ReplyKeyboardMarkup()

    key_game = telebot.types.KeyboardButton(text="/game")
    key_rules = telebot.types.KeyboardButton(text="/rules")
    key_leaderboard = telebot.types.KeyboardButton(text="/leaderboard")
    keyboard.add(key_game, key_rules, key_leaderboard)
    bot.send_message(message.from_user.id, "Привет! Чтобы начать игру вводи /game\nПравила: /rules",
                     reply_markup=keyboard)


@bot.message_handler(commands=['leaderboard'])
def leaders(message):
    with open("fake_db.json", "r", encoding='utf-8') as r:
        data = json.load(r)

    data = sorted(data.items(), key=lambda x: int(x[1]['wins']), reverse=True)
    new_data = {}
    for user, values in data:
        new_data[user] = values

    counter = 0
    for user in new_data:
        if counter == 5:
            break
        bot.send_message(message.from_user.id, f"username: {new_data[user]['username']} ------- Score: {new_data[user]['wins']}")
        counter += 1


@bot.message_handler(commands=['rules'])
def rules(message):
    bot.send_message(message.from_user.id, "Игрок вводит тему, на ее основе генерируется случайный текст. Пользователю выводятся случайный из этих текстов, с одним удаленным словом. Задача игрока отгадать это слово. На это дается 5 попыток, после чего либо человечек живет, либо его казнят")
    msg = bot.send_message(message.from_user.id, "Начинаем игру?")
    bot.register_next_step_handler(msg, step_1)


@bot.message_handler(commands=['game'])
def step_1(message):
    if message.text.lower() == "нет":
        bot.send_message(message.from_user.id, "До свидания!")
    else:
        msg = bot.send_message(message.from_user.id, "Введите тему для генерации текста: ")
        bot.register_next_step_handler(msg, callback=step_2)


def step_2(message):
    field_value = message.text
    bot.send_message(message.from_user.id, "Генерируем текст...")
    variables = {"option": random.choice(level_one_options), "field_value": field_value, "tone": random.choice(tones)}
    req = requests.post("http://212.193.50.2:777/one_field_tools", json=variables)
    j_data = req.json()
    texts = j_data.get('texts')
    print('data downloaded')

    with open("fake_db.json", "r", encoding='utf-8') as r_obj:
        data = json.load(r_obj)
    try:
        wins = data[str(message.from_user.id)]['wins']
    except Exception:
        wins = 0
    words = texts[0].split()
    try:
        words.remove("-")
    except Exception:
        print()

    words_clean = []
    for i in words:
        words_clean.append(re.sub("[^A-Za-zА-Яа-я]", "", i))

    words_to_user = deepcopy(words_clean)
    finding_word = random.choice(words_clean)
    wordind = words_clean.index(finding_word)

    board = "_ " * len(finding_word)
    words[wordind] = board
    words_clean[wordind] = board

    with open("fake_db.json", "r", encoding="utf-8") as r_obj:
        data = json.load(r_obj)
        if not (message.from_user.id in data):
            data[message.from_user.id] = {}
            data[message.from_user.id]['wins'] = 0

    with open("fake_db.json", 'w', encoding="utf-8") as w_obj:
        data[message.from_user.id]['username'] = message.from_user.username
        data[message.from_user.id]['wins'] = wins
        data[message.from_user.id]['wrong'] = 0
        data[message.from_user.id]['word'] = finding_word
        data[message.from_user.id]['text'] = texts[0]
        json.dump(data, w_obj)

    bot.send_message(message.from_user.id, "Добро пожаловать на казни!")
    bot.send_message(message.from_user.id, " ".join(words))
    try_word = bot.send_message(message.from_user.id, "Ваше слово: ")
    bot.register_next_step_handler(try_word, callback=try_1)
    # Создаем кнопки


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "about":
        bot.send_message(call.from_user.id,
                         text="Это игровой бот. За основу взята игра виселица. Этот бот использует технологию генерации текстов от компании HaClever, для генерации текстов",)

    elif call.data == "start":
        msg = bot.send_message(call.from_user.id, "Начинаем сначала?")
        bot.register_next_step_handler(message=msg, callback=step_1)


def try_1(message):
    with open("fake_db.json", "r", encoding="utf-8") as r:
        data = json.load(r)

    word = data[str(message.from_user.id)]['word']
    text = data[str(message.from_user.id)]['text']

    if message.text.lower() == word.lower():
        data[str(message.from_user.id)]['wins'] = int(data[str(message.from_user.id)]['wins']) + 1
        with open("fake_db.json", "w", encoding="utf-8") as w_obj:
            json.dump(data, w_obj)

        keyboard = telebot.types.InlineKeyboardMarkup()
        key_1 = telebot.types.InlineKeyboardButton(text="Сыграть ещё раз", callback_data="start")
        key_2 = telebot.types.InlineKeyboardButton(text="О генерации текстов", callback_data="about")
        keyboard.add(key_1, key_2)
        bot.send_message(message.from_user.id, f"Правильно! Вы выйграли!!!\nТекст {text}", reply_markup=keyboard)
        return
    else:
        with open("fake_db.json", "r", encoding="utf-8") as r_obj:
            data = json.load(r_obj)
            wrong = data[str(message.from_user.id)]['wrong']
        wrong = int(wrong) + 1
        data[str(message.from_user.id)]['wrong'] = wrong
        print(data)
        with open("fake_db.json", "w", encoding="utf-8") as w_obj:
            json.dump(data, w_obj)
        if wrong > 5:
            keyboard = telebot.types.InlineKeyboardMarkup()
            key_1 = telebot.types.InlineKeyboardButton(text="Сыграть ещё раз", callback_data="start")
            key_2 = telebot.types.InlineKeyboardButton(text="О генерации текстов", callback_data="about")
            keyboard.add(key_1, key_2)
            bot.send_message(message.from_user.id, f"Вы проиграли! Хи-Хи-Хи.\nТекст: {text}", reply_markup=keyboard)
            return
    bot.send_message(message.from_user.id, "\n".join(stages[0: wrong+1]))
    try_word = bot.send_message(message.from_user.id, "Ваше слово: ")
    bot.register_next_step_handler(try_word, callback=try_1)


while True:
    try:
        bot.infinity_polling()
    except Exception as e:
        time.sleep(3)
        print(e)
