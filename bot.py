#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import json
from json.decoder import JSONDecodeError

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
current_dir = os.path.dirname(os.path.realpath(__file__))

def load_config():
    token = ''
    config_path = current_dir + '/config.json'
    assert os.path.isfile(config_path)

    with open(config_path, 'r') as config:
        try:
            data = json.load(json_file)
        except JSONDecodeError:
            assert False

        try:
            token = data['token']
        except:
            assert False

        config.close()
    return token

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def get_num_from_string(string):
    num = ''  
    for i in string:  
        if i in '1234567890':  
            num+=i
        else:
            break
    integer = int(num)  
    return integer

def get_full_name(user):
    name = user.first_name
    if user.last_name is not None:
        name = name + " " + user.last_name
    return name

def get_score(chat_id, uid):
    score = 0
    data = {}
    with open(current_dir + '/score.json', 'r') as json_file:
        try:
            data = json.load(json_file)
        except JSONDecodeError:
            update_score(chat_id, uid, 0, 0)

        str_uid = str(uid)
        str_chatid = str(chat_id)
        try:
            chat_data = data[str_chatid]
            score = chat_data[str_uid]
        except:
            update_score(chat_id, uid, 0, 0)
        json_file.close()
    return str(score)

def update_score(chat_id, uid, current, changes):
    new_score = current

    data = {}
    chat_data = {}
    with open(current_dir + '/score.json', 'r') as json_file:
        try:
            data = json.load(json_file)
        except JSONDecodeError:
            pass
        json_file.close()

    with open(current_dir + '/score.json', 'w') as json_file:
        str_uid = str(uid)
        str_chat = str(chat_id)

        try:
            chat_data = data[str_chat]
        except:
            pass
        
        chat_data[str_uid] = int(current) + int(changes)
        data[str_chat] = chat_data
        new_score = int(current) + int(changes)

        json.dump(data, json_file)
        json_file.close()

    return str(new_score)

def change_score(update, context, index):
    changes = get_num_from_string(update.message.text[index+1:])
    orig_user = update.message.reply_to_message.from_user
    chat_id = update.message.chat.id

    if orig_user.is_bot == False:
        orig_id = orig_user.id

        # 禁止自肥
        if orig_id == update.message.from_user.id and changes > 0 and update.message.text.find("-") < 0:
            update.message.reply_text("想給自己加分？你怎麼不吸自己的懶覺？")
            return

        # 禁止灌水
        if changes > 100 or changes < -100:
            update.message.reply_text("想灌水？你怎麼不先灌好你的腸子給我肛？")
            return
        current_score = get_score(chat_id, orig_id)
        msg = " 被加到了："
        end = "，好棒棒！"

        # 檢查扣分
        if update.message.text.find("-") >= 0:
            changes = changes * (-1)
            msg = " 被扣到："
            end = "，幫哭哭！"

        # 檢查零分
        if changes == 0:
            bot.send_message(chat_id, "你在整我嗎？？？")
            msg = "維持在："
            end = "。加油，好嗎？"

        new_score = update_score(chat_id, orig_id, current_score, changes)
        name = get_full_name(orig_user)
        update.message.reply_text(name + msg + new_score + "分" + end)
    else:
        update.message.reply_text("神聖、莊嚴、公正、無私的機器人是不可以有分數的 🤖️")


def show_score(update, context):
    def show_score_for_user(chat_id, user):
        uid = user.id
        score = get_score(chat_id, uid)
        name = user.first_name
        if user.last_name is not None:
            name = name + " " + user.last_name
        update.message.reply_text(name + " 目前的分數是: " + score + "分")

    chat_id = update.message.chat.id

    if update.message.reply_to_message is not None:
        orig_user = update.message.reply_to_message.from_user
        show_score_for_user(chat_id, orig_user)
    else:
        user = update.message.from_user
        show_score_for_user(chat_id, user)


def show_all_scores(update, context):
    chat_id = update.message.chat.id
    bot.send_message(chat_id, "小精靈正在用神奇魔法計算...")

    # Parse data
    current_dir = os.path.dirname(os.path.realpath(__file__))
    data = {}
    chat_data = {}
    with open(current_dir + '/score.json', 'r') as json_file:
        try:
            data = json.load(json_file)
        except:
            pass

        try:
            chat_data = data[str(chat_id)]
        except:
            pass

        if data == {} or chat_data == {}:
            chat_id = update.message.chat.id
            bot.send_message(chat_id, "哎呀，還沒有紀錄任何分數呢...")
            return
        json_file.close()

    # Sort
    arr = sorted(data[str(chat_id)].items(), key=lambda x: x[1], reverse=True)
    found = False

    # Prepare
    text = '登登登！排名出來了！\n\n'
    count = 0

    # List all
    for (uid, score) in arr:
        try:
            member = bot.getChatMember(chat_id, uid)
        except:
            continue
        user = member.user
        if user.is_bot == False:
            found = True
            name = get_full_name(user)

            # Assign medal
            if count == 0:
                medal = '🥇' + ' '
            elif count == 1:
                medal = '🥈' + ' '
            elif count == 2:
                medal = '🥉' + ' '
            else:
                medal = ''

            text += (medal + name + '：' + get_score(chat_id, user.id) + '分\n')
            count += 1

    if found == False:
        bot.send_message(chat_id, "哎呀，還沒有紀錄任何分數呢...")
    else:
        bot.send_message(chat_id, text)


def handle_text(update, context):
    chat_id = update.message.chat.id
    if update.message.text == '/score':
        show_score(update, context)
    elif update.message.text == '/list_score':
        show_all_scores(update, context)
    elif update.message.reply_to_message is not None:
        # 避免一下可能抓到網址好了
        if update.message.text.find('http') < 0 and update.message.text.find('www') < 0:
            if update.message.text.find('+') >= 0 and update.message.text.find('-') >= 0:
                bot.send_message("你他媽搞我？")
                current_score = get_score(chat_id, update.message.from_user.id)
                new_score = update_score(chat_id, update.message.from_user.id, current_score, -10)
                update.message.reply_text("扣你十分！！")
                return
            if update.message.text.find('+') >= 0:
                change_score(update, context, update.message.text.find('+'))
            elif update.message.text.find('-') >= 0:
                change_score(update, context, update.message.text.find('-'))


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    token = load_config()
    updater = Updater(token, use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    # dp.add_handler(CommandHandler("score", start))

    # on noncommand i.e message
    dp.add_handler(MessageHandler(Filters.text, handle_text))
    global bot
    bot = updater.bot

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()