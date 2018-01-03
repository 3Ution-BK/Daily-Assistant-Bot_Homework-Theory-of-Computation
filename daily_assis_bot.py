""" Basic bot module

    This module implement the bot program.
"""

import sys
import telegram
from flask import Flask, request
from alarm import set_alarm
from weather import get_weather
from news import get_news, get_news_url

# Important token
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_TOKEN'

# Bot webhook url
WEBHOOK_URL = 'YOUR_WEBHOOK_URL'

# Constant
HELLO_MESSAGE = ('I can help you create alarm, checking weather,' +
                 'and checking news for you.\n' +
                 'You can control me by sending these commands:\n' +
                 '/alarm: setting alarm\n' +
                 '/weather: checking weather\n' +
                 '/news: checking news\n')
ARGUMENT_NOT_CORRECT = 'Sorry. Argument is not correct.\n'
ALARM_COMMAND_TIPS = 'Tips: [number] [(sec / s) / (min / m) / (hour / h)]\n'

# Variables
app = Flask(__name__)
daily_assistant_bot = telegram.Bot(token=TELEGRAM_TOKEN)
fsm_dictionary = {}


def _set_webhook():
    """ Setting the webhook

    It will setting the webhook of the bot.

    Args:
        None.

    Returns:
        None.
    Raises:
        None.
    """
    is_success = daily_assistant_bot.set_webhook(WEBHOOK_URL + '/hook')
    if is_success is None:
        print('Error: set_webhook failed')
        sys.exit(1)
    else:
        print('set_webhook success')


def alarm_setting(chat_id, message):
    """ Setting the alarm

    It will setting the alarm according to the fsm.

    Args:
        chat_id: the chat id of the user.
        message: the message of the user.

    Returns:
        A string message for user.
    Raises:
        None.
    """
    step = fsm_dictionary.get(chat_id).get('Step')
    data = fsm_dictionary.get(chat_id).get('Data')
    if data is None:
        data = {}

    # Check the step
    if step == 'time':
        # Check the boundary
        message = message.split(" ")
        if message.__len__() != 2:
            reply = (ARGUMENT_NOT_CORRECT + ALARM_COMMAND_TIPS)
            return reply

        # Find the token
        time_count, time_unit = 0, 'sec'

        # determine the token
        # time_count
        if message[0].isdigit():
            time_count = int(message[0])
        else:
            reply = (ARGUMENT_NOT_CORRECT + ALARM_COMMAND_TIPS)
            return reply

        # time_unit
        time_unit = message[1]
        if time_unit == 'hour' or time_unit == 'h':
            time_count *= 3600
        elif time_unit == 'min' or time_unit == 'm':
            time_count *= 60
        elif time_unit == 'sec' or time_unit == 's':
            pass
        else:
            reply = (ARGUMENT_NOT_CORRECT + ALARM_COMMAND_TIPS)
            return reply

        # State update
        data['Time'] = time_count
        fsm_dictionary[chat_id] = {'State': 'alarm', 'Step': 'msg',
                                   'Data': data}

        # Return message
        return 'What message do you want me to call you when you wake up?'
    elif step == 'msg':
        # data update
        data['Message'] = message

        # State update
        fsm_dictionary[chat_id] = {'State': 'alarm', 'Step': 'done',
                                   'Data': data}

        # Return message
        return 'done'
    else:
        pass


def weather_setting(chat_id, message):
    """ Checking the weather

    It will check the weather according to the fsm.

    Args:
        chat_id: the chat id of the user.
        message: the message of the user.

    Returns:
        A string message for user.
    Raises:
        None.
    """
    # Check the step
    step = fsm_dictionary.get(chat_id).get('Step')
    if step == 'city':
        # State update
        fsm_dictionary[chat_id] = {'State': 'news', 'Step': 'done'}

        return get_weather(message)
    else:
        pass


def news_setting(chat_id, message):
    """ Checking the news

    It will check the news according to the fsm.

    Args:
        chat_id: the chat id of the user.
        message: the message of the user.

    Returns:
        A string message for user.
    Raises:
        None.
    """
    step = fsm_dictionary.get(chat_id).get('Step')
    data = fsm_dictionary.get(chat_id).get('Data')
    if data is None:
        data = {}

    # Check the step
    if step == 'type':
        # State update
        data['Type'] = message
        fsm_dictionary[chat_id] = {'State': 'news', 'Step': 'source',
                                   'Data': data}

        # Return message
        reply = ('What news site do you want to see?\n' +
                 'Any site is welcome? Reply /none to me.')
        return reply
    elif step == 'source':
        # State update
        data['Source'] = message
        fsm_dictionary[chat_id] = {'State': 'news', 'Step': 'find',
                                   'Data': data}

        # Return message
        reply = ('What particular article do you want to see?\n' +
                 'Every thing is fine for you? Reply /none to me.')
        return reply
    elif step == 'find':
        # data update
        data['Message'] = message

        # State update
        fsm_dictionary[chat_id] = {'State': 'news', 'Step': 'done',
                                   'Data': data}

        # Return message
        news_type = fsm_dictionary.get(chat_id).get('Data').get('Type')
        source = fsm_dictionary.get(chat_id).get('Data').get('Source')
        return get_news_url(news_type=news_type, source=source, find=message)
    else:
        pass


@app.route('/hook', methods=['POST'])
def webhook_handler():
    """ Reply user when user send message

    It will receive the message, determine the message, and reply the use.

    Args:
        None.

    Returns:
        ok.
    Raises:
        None.
    """
    if request.method == 'POST':
        incoming_update = telegram.Update.de_json(request.get_json(force=True),
                                                  daily_assistant_bot)

        # Get the string
        message = incoming_update.message.text

        # Find the state of the chat_id
        chat_id = incoming_update.message.chat_id
        is_in_fsm = fsm_dictionary.get(chat_id)
        if is_in_fsm != None:
            # The user is not in the initial state
            # Check the state to determine the reply string
            state = fsm_dictionary.get(chat_id).get('State')
            if state == 'alarm':
                reply = alarm_setting(chat_id=chat_id, message=message)

                # Determine whether this is the result user want to see
                if fsm_dictionary.get(chat_id).get('Step') == 'done':
                    # Set alarm
                    data = fsm_dictionary.get(chat_id).get('Data')
                    time = data.get('Time')
                    alarm_message = data.get('Message')
                    set_alarm(time=time, message=alarm_message,
                              chat_id=chat_id, bot=daily_assistant_bot)

                    # fsm - go back to initial state
                    fsm_dictionary[chat_id]['Data'].clear()
                    fsm_dictionary[chat_id].clear()
                    del fsm_dictionary[chat_id]
                else:
                    incoming_update.message.reply_text(reply)
            elif state == 'weather':
                # Get weather
                reply = weather_setting(chat_id=chat_id, message=message)
                incoming_update.message.reply_text(reply)

                # Determine whether this is the result user want to see
                if fsm_dictionary.get(chat_id).get('Step') == 'done':
                    # fsm - go back to initial state
                    fsm_dictionary[chat_id].clear()
                    del fsm_dictionary[chat_id]
            elif state == 'news':
                reply = news_setting(chat_id=chat_id, message=message)

                # Determine whether this is the result user want to see
                if fsm_dictionary.get(chat_id).get('Step') == 'done':
                    # Get the news
                    get_news(url_string=reply, chat_id=chat_id,
                             bot=daily_assistant_bot)
                    # fsm - go back to initial state
                    fsm_dictionary[chat_id]['Data'].clear()
                    fsm_dictionary[chat_id].clear()
                    del fsm_dictionary[chat_id]
                else:
                    # Reply for more intel
                    incoming_update.message.reply_text(reply)
        else:
            # The user is in the initial state
            if message == '/alarm':
                # Reply message
                reply = 'When will you want me to notify you?'
                incoming_update.message.reply_text(reply)

                # State add
                fsm_dictionary[chat_id] = {'State': 'alarm', 'Step': 'time'}
            elif message == '/weather':
                # Reply message
                reply = 'Which city do you want me to check?'
                incoming_update.message.reply_text(reply)

                # State add
                fsm_dictionary[chat_id] = {'State': 'weather', 'Step': 'city'}
            elif message == '/news':
                # Reply message
                reply = ('What news do you want to see?\n' +
                         'Top headlines or everynews?')
                incoming_update.message.reply_text(reply)

                # State add
                fsm_dictionary[chat_id] = {'State': 'news', 'Step': 'type'}
            else:
                incoming_update.message.reply_text(HELLO_MESSAGE)

    return 'ok'


def main():
    """ Main function

    For running main function

    Args:
        None.

    Returns:
        None.
    Raises:
        None.
    """
    _set_webhook()
    app.run()


if __name__ == "__main__":
    main()
