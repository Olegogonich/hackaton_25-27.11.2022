import telebot
from telebot import types
import json
import os
import config

bot = telebot.TeleBot(config.token)

back_markup = types.InlineKeyboardMarkup()
back_button = types.InlineKeyboardButton(text="Назад", callback_data='back')
back_markup.add(back_button)

new_equips = {}
new_requests = {}
new_rejections = {}
user_messages = {}


def delete_all_messages(user_id):
    print(user_messages[user_id])
    for _ in range(len(user_messages[user_id])):
        try:
            print(f"delete {user_messages[user_id][-1]}")
            bot.delete_message(user_id, user_messages[user_id][-1])
            user_messages[user_id].pop()
        except IndexError:
            pass
        except telebot.apihelper.ApiTelegramException:
            pass


@bot.message_handler(commands=['start'])
def start(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    user_messages[message.from_user.id] = []
    user_id = message.from_user.id
    if user_id in config.admin_ids:
        markup = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton(text="Просмотр доступного оборудования", callback_data='show_equips')
        button2 = types.InlineKeyboardButton(text="Добавить новое оборудование", callback_data='add_equip')
        button3 = types.InlineKeyboardButton(text="Удалить оборудование", callback_data='delete_equip')
        button4 = types.InlineKeyboardButton(text="Посмотреть новые заявки", callback_data='show_requests')
        button5 = types.InlineKeyboardButton(text="Одобренные заявки", callback_data='accepted_requests')
        markup.add(button1, button2, button3, button4, button5)
        bot.send_message(message.chat.id, "Привет! Это - меню администратора бота. Что тебя интересует?",
                         reply_markup=markup)

    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton(text="Просмотреть доступное оборудование", callback_data='show_equips')
        button2 = types.InlineKeyboardButton(text='Мои заявки', callback_data="my_requests")
        markup.add(button1, button2)
        bot.send_message(message.chat.id, "Привет! Я - бот, который поможет тебе забронировать"
                                          "оборудование в лабораториях ИКТИБ. Что тебя интересует?",
                         reply_markup=markup)


def back_to_start(message):
    bot.clear_step_handler_by_chat_id(message)
    user_messages[message] = []
    user_id = message
    if user_id in config.admin_ids:
        markup = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton(text="Просмотр доступного оборудования", callback_data='show_equips')
        button2 = types.InlineKeyboardButton(text="Добавить новое оборудование", callback_data='add_equip')
        button3 = types.InlineKeyboardButton(text="Удалить оборудование", callback_data='delete_equip')
        button4 = types.InlineKeyboardButton(text="Посмотреть новые заявки", callback_data='show_requests')
        button5 = types.InlineKeyboardButton(text="Одобренные заявки", callback_data='accepted_requests')
        markup.add(button1, button2, button3, button4, button5)
        bot.send_message(message, "Привет! Это - меню администратора бота. Что тебя интересует?",
                         reply_markup=markup)

    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton(text="Просмотреть доступное оборудование", callback_data='show_equips')
        button2 = types.InlineKeyboardButton(text='Мои заявки', callback_data="my_requests")
        markup.add(button1, button2)
        bot.send_message(message, "Привет! Я - бот, который поможет тебе забронировать "
                                  "оборудование в лабораториях ИКТИБ. Что тебя интересует?",
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'back')
def back(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    back_to_start(call.from_user.id)


@bot.callback_query_handler(func=lambda call: call.data == 'my_requests')
def my_requests(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    bot.answer_callback_query(call.id)
    is_there_requests = False
    text = "Ваши заявки:\n"
    reqs = os.listdir(config.request_dir)
    username = f"{call.from_user.first_name} {call.from_user.last_name}"
    for req in reqs:
        if req.find(username) == 0:
            text += f"<b>{req[len(username) + 3:-5]}</b>\n"
            is_there_requests = True
    if is_there_requests:
        bot.send_message(call.message.chat.id, text, reply_markup=back_markup, parse_mode='HTML')
    else:
        bot.send_message(call.message.chat.id, "В данный момент у вас нет никаких заявок!", reply_markup=back_markup)


@bot.callback_query_handler(func=lambda call: call.data == 'add_equip')
def add_equip(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    bot.send_message(call.message.chat.id, "Отлично. Введите название оборудования")
    bot.register_next_step_handler(call.message, add_equip_name)


def add_equip_name(message):
    if message.content_type == 'text' and len(message.text) <= 24:
        new_equips[message.from_user.id] = config.Equip(name=message.text)
        bot.send_message(message.chat.id, "Введите описание")
        bot.register_next_step_handler(message, add_equip_text)

    elif len(message.text) > 24:
        bot.send_message(message.chat.id, "Название слишком длинное!")
        bot.register_next_step_handler(message, add_equip_name)

    else:
        bot.send_message(message.chat.id, "Нужно ввести текст!")
        bot.register_next_step_handler(message, add_equip_name)


def add_equip_text(message):
    if message.content_type == 'text':
        new_equips[message.from_user.id].description = message.text
        bot.send_message(message.chat.id, "А теперь пришлите фото оборудования")
        bot.register_next_step_handler(message, add_equip_photo)

    else:
        bot.send_message(message.chat.id, "Нужно ввести текст!")
        bot.register_next_step_handler(message, add_equip_text)


def add_equip_photo(message):
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        curr_equip = new_equips[message.from_user.id]
        src = 'photos/' + curr_equip.name + '_' + str(len(curr_equip.photos)) + '.jpg'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        curr_equip.photos.append(src)
        markup = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton(text='Добавить фото', callback_data='add_more_equip_photo')
        button2 = types.InlineKeyboardButton(text='Завершить заполнение', callback_data='finish_equip')
        markup.add(button1, button2)
        bot.send_message(message.chat.id, "Отлично! Можете добавить еще фото", reply_markup=markup)

    else:
        bot.send_message(message.chat.id, "Нужно прислать фото!")
        bot.register_next_step_handler(message, add_equip_photo)


@bot.callback_query_handler(func=lambda call: call.data == 'add_more_equip_photo')
def add_more_equip_photo(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    bot.send_message(call.message.chat.id, "Пришлите мне фото оборудования")
    bot.register_next_step_handler(call.message, add_equip_photo)


@bot.callback_query_handler(func=lambda call: call.data == 'finish_equip')
def finish_equip(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    new_equip = new_equips[call.from_user.id]
    equip_dict = {
        'name': new_equip.name,
        'description': new_equip.description,
        'photos': new_equip.photos,
        'time': new_equip.time
    }
    with open(config.json_dir + '/' + new_equip.name + '.json', 'w') as new_file:
        new_file.write(json.dumps(equip_dict, indent=4))
    bot.send_message(call.message.chat.id, "Оборудование успешно добавлено в список", reply_markup=back_markup)
    new_equips.pop(call.from_user.id)


@bot.callback_query_handler(func=lambda call: call.data == 'delete_equip')
def delete_equip(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    names_list = os.listdir(config.json_dir)
    if names_list:
        markup = types.InlineKeyboardMarkup()
        for name in names_list:
            button = types.InlineKeyboardButton(text=name[:-5], callback_data='equip_delete_' + name)
            markup.add(button)
        markup.add(back_button)
        bot.send_message(call.message.chat.id, "Как называется оборудование, которое вы хотите удалить?",
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data[:12] == 'equip_delete')
def equip_delete(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    name = call.data[13:]
    markup = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton(text='Да', callback_data='yes_' + name)
    button2 = types.InlineKeyboardButton(text='Нет', callback_data='no_' + name)
    markup.add(button1, button2)
    bot.send_message(call.message.chat.id, f"Вы уверены что хотите удалить <b>{name[:-5]}</b>?",
                     parse_mode='HTML',
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data[:3] == 'yes')
def yes_delete(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    name = call.data[4:]
    with open(config.json_dir + '/' + name) as file:
        curr_equip = json.loads(file.read())
        for photo in curr_equip['photos']:
            os.remove(photo)
    os.remove(config.json_dir + '/' + name)
    bot.send_message(call.message.chat.id, f"Оборудование <b>{name[:-5]}</b> успешно удалено",
                     parse_mode='HTML', reply_markup=back_markup)


@bot.callback_query_handler(func=lambda call: call.data[:2] == 'no')
def no_delete(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    delete_equip(call)


@bot.callback_query_handler(func=lambda call: call.data == 'show_equips')
def show_equips(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    names_list = os.listdir(config.json_dir)
    if names_list:
        markup = types.InlineKeyboardMarkup()
        for name in names_list:
            button = types.InlineKeyboardButton(text=name[:-5], callback_data='equip_' + name)
            markup.add(button)
        back_btn = types.InlineKeyboardButton(text="Назад", callback_data='back')
        markup.add(back_btn)
        bot.send_message(call.message.chat.id, "Список доступного оборудования:", reply_markup=markup)

    else:
        bot.send_message(call.message.chat.id, "В данный момент доступного оборудования нет")


@bot.callback_query_handler(func=lambda call: call.data[:5] == 'equip')
def equip(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    name = call.data[6:]
    with open(config.json_dir + '/' + name) as file:
        curr_equip = json.loads(file.read())
        text = f"<b>{curr_equip['name']}</b>" + '\n' + curr_equip['description']
        photos = []
        medias = []
        for photo in curr_equip['photos']:
            file_photo = open(photo, 'rb')
            photos.append(file_photo)
        for photo in photos:
            medias.append(types.InputMediaPhoto(photo))
        markup = types.InlineKeyboardMarkup(row_width=2)
        button1 = types.InlineKeyboardButton("Да, забронировать", callback_data='make_request_' + name)
        button2 = types.InlineKeyboardButton("Нет, не надо", callback_data='show_equips')
        markup.add(button1, button2)
        bot.send_message(call.message.chat.id, text, parse_mode='HTML')
        bot.send_media_group(call.message.chat.id, medias)
        bot.send_message(call.message.chat.id, "Хотите забронировать это оборудование?", reply_markup=markup)
        for photo in photos:
            photo.close()


@bot.callback_query_handler(func=lambda call: call.data[:12] == 'make_request')
def make_request(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    name = call.data[13:]
    new_requests[call.from_user.id] = config.Request(equip_name=name[:-5])
    with open(config.json_dir + '/' + name) as file:
        curr_equip = json.loads(file.read())
        time = curr_equip['time']
        markup = types.InlineKeyboardMarkup(row_width=3)
        there_is_time = False
        for one_time in time:
            if one_time in config.times:
                button = types.InlineKeyboardButton(text=one_time, callback_data=f"time_{one_time}")
                markup.add(button)
                there_is_time = True
        markup.add(back_button)
        if there_is_time:
            bot.send_message(call.message.chat.id, "Выберите удобное время", reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, "Извините, но свободное время закончилось!",
                             reply_markup=back_markup)


@bot.callback_query_handler(func=lambda call: call.data[:4] == 'time')
def make_request_time(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    new_request = new_requests[call.from_user.id]
    new_request.time = call.data[5:]
    new_request.user_name = call.from_user.first_name + ' ' + call.from_user.last_name
    new_request.user_id = call.from_user.id
    src = f'{config.request_dir}/{new_request.user_name} - {new_request.equip_name} {new_request.time}.json'
    with open(src, 'w') as new_file:
        new_file.write(json.dumps({
            'equip_name': new_request.equip_name,
            'time': new_request.time,
            'user_name': new_request.user_name,
            'user_id': new_request.user_id,
            'accepted': new_request.accepted,
        }, indent=4))
    bot.send_message(call.message.chat.id,
                     text=f"Заявка оформлена на {new_request.time}. Оборудование - {new_request.equip_name}",
                     reply_markup=back_markup)
    for admin_id in config.admin_ids:
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="Посмотреть заявки", callback_data='show_requests')
        markup.add(button)
        bot.send_message(admin_id, "Появилась новая заявка!", reply_markup=markup)
    new_requests.pop(call.from_user.id)


@bot.callback_query_handler(func=lambda call: call.data == 'show_requests')
def show_requests(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    markup = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton(text='Одобрить', callback_data='accept')
    button2 = types.InlineKeyboardButton(text='Отклонить', callback_data='reject')
    markup.add(button1, button2)
    is_there_requests = False
    for request_name in os.listdir(config.request_dir):
        with open(config.request_dir + '/' + request_name) as request_json:
            request = json.loads(request_json.read())
            if request['accepted'] is None:
                is_there_requests = True
                bot.send_message(call.message.chat.id,
                                 text=f"{request['user_name']} - {request['equip_name']} {request['time']}",
                                 reply_markup=markup)
    if not is_there_requests:
        bot.send_message(call.message.chat.id, "В данный момент заявок нет", reply_markup=back_markup)


@bot.callback_query_handler(func=lambda call: call.data == 'accepted_requests')
def accepted_requests(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    is_there_requests = False
    text = f"Одобренные заявки:\n"
    for request_name in os.listdir(config.request_dir):
        with open(config.request_dir + '/' + request_name) as request_json:
            request = json.loads(request_json.read())
            if request['accepted']:
                is_there_requests = True
                text += f"{request['user_name']} - {request['equip_name']} {request['time']}"

    if is_there_requests:
        bot.send_message(call.message.chat.id, text=text, reply_markup=back_markup)
    else:
        bot.send_message(call.message.chat.id, "В данный момент заявок нет", reply_markup=back_markup)


@bot.callback_query_handler(func=lambda call: call.data == 'accept')
def accept(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    with open(config.request_dir + '/' + call.message.text + '.json') as request_json:
        request = json.loads(request_json.read())

        with open(config.json_dir + '/' + request['equip_name'] + '.json', 'r') as file:
            old_file = file.read()
        new_file = old_file.replace(request['time'], f"{request['time']} - {request['user_name']}")
        with open(config.json_dir + '/' + request['equip_name'] + '.json', 'w') as file:
            file.write(new_file)

        request['accepted'] = True

        with open(config.request_dir + '/' + call.message.text + '.json', 'w') as new_request_json:
            new_request_json.write(json.dumps(request, indent=4))

        bot.send_message(chat_id=request['user_id'],
                         text=f"Ваша заявка на <b>{request['equip_name']} в {request['time']}</b> одобрена!",
                         parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data == 'reject')
def reject_comment(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.answer_callback_query(call.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    new_rejections[call.from_user.id] = call.message.text
    bot.send_message(call.message.chat.id, "Укажите причину отклонения заявки")
    bot.register_next_step_handler(call.message, reject)


def reject(message):
    name = new_rejections[message.from_user.id]
    with open(config.request_dir + '/' + name + '.json') as request_json:
        request = json.loads(request_json.read())
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='Связаться с администратором', url='t.me/olegogonich')
        markup.add(button)
        bot.send_message(request['user_id'],
                         f"Ваша заявка на <b>{request['equip_name']} в {request['time']}</b> была отклонена.\n"
                         f"Причина - {message.text}",
                         parse_mode='HTML',
                         reply_markup=markup)
        os.remove(f"{config.request_dir}/{request['user_name']} - {request['equip_name']} {request['time']}.json")
    new_rejections.pop(message.from_user.id)
    bot.send_message(message.chat.id, "Заявка отклонена", reply_markup=back_markup)


if __name__ == '__main__':
    print('bot is running')
    bot.infinity_polling()
