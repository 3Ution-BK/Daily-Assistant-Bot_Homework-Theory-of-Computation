""" Basic alarm module

    This module implement the alarm program.
"""

from multiprocessing import Process
from time import sleep
import telegram


def child_process_alarm(time, message, chat_id, bot):
    """ A child process that will notify after 'time' second

    This functions will be used as the alarm. After 'time' second, it will print
    the message back to user.

    Args:
        time: Seconds.
        message: Message needs to send when alarm awakes.
        chat_id: Telegram user's id.
        bot: Bot which is in the service.

    Returns:
        None.
    Raises:
        None.
    """
    NOTIFY_MESSAGE = 'I will notify you after ' + str(time) + ' seconds'
    try:
        bot.send_message(chat_id=chat_id, text=NOTIFY_MESSAGE)
        sleep(time)
        bot.send_message(chat_id=chat_id, text='Alarm: ' + message)
    except telegram.TelegramError:
        pass



def set_alarm(time, message, chat_id, bot):
    """ Set the alarm after 'time' second

    It will create a child process to set the alarm. After 'time' second it will
    print the message back to user.

    Args:
        time: Seconds.
        message: Message needs to send when alarm awakes
        chat_id: Telegram user's id.
        bot: Bot which is in the service

    Returns:
        None.
    Raises:
        None.
    """
    thread = Process(target=child_process_alarm,
                     args=(time, message, chat_id, bot))
    thread.start()
