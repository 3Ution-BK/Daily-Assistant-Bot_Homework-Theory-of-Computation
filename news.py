""" Basic weather module

    This module implement the weather program.
"""

import urllib.request
import json

# Important token
API_KEY = 'apiKey=' + 'YOUR_API_KEY'

# Constant
NEWS_URL = 'https://newsapi.org/v2/'
TOP_HEADLINE = 'top-headlines?'
EVERYNEWS = 'everything?'
FIND = 'q='
SOURCE = 'sources='
POWERED_BY = 'powered by NewsAPI'


def get_news(chat_id, bot, url_string, max_news_display=3):
    """ Get the news

    It will check the news in NEWSAPI, and return result.

    Args:
        chat_id: Telegram user's id.
        bot: Bot which is in the service
        url_string: url which is used for communication
        max_news_display: total news displayed in telegram bot

    Returns:
        None.
    Raises:
        None.
    """
    try:
        with urllib.request.urlopen(url_string) as url:
            news_data = json.loads(url.read().decode())

            # Get the news info
            status = news_data.get('status')
            if status == 'ok' and news_data.get('totalResults') > 0:
                counter = 0
                size = max_news_display if max_news_display <= 3 else 3
                for article in news_data.get('articles'):
                    # Check the boundary
                    if counter >= size:
                        break

                    # Get the news
                    title = article.get('title')
                    source = article.get('source').get('name')
                    description = article.get('description')
                    link = article.get('url')
                    published_at = article.get('publishedAt')

                    # Put the result into result string
                    result_string = (str(title) + '\n' +
                                     'by ' + str(source) + '\n' +
                                     'time: ' + str(published_at) + '\n' +
                                     str(description) + '\n' +
                                     'link: ' + str(link) + '\n' +
                                     POWERED_BY)

                    bot.send_message(chat_id=chat_id, text=result_string)

                    counter += 1
            else:
                result_string = 'Sorry. I cannot find any news.\n'
                bot.send_message(chat_id=chat_id, text=result_string)

    except urllib.error.HTTPError:
        # news no found
        result_string = 'Sorry. I cannot find any news.\n' + POWERED_BY
        bot.send_message(chat_id=chat_id, text=result_string)


def get_news_url(news_type, source, find):
    """ Get the news url

    Combine the url string which is used for communicate with NewsAPI.

    Args:
        news_type: news type.
        source: news website source.
        find: particular things user want to check.

    Returns:
        A string of url
    Raises:
        None.
    """
    # Combine the url
    url_string = NEWS_URL

    # News type
    news_type = news_type.replace(' ', '-')
    if news_type == 'top-headlines' or news_type == 'top' or news_type == 't':
        url_string += TOP_HEADLINE
    elif news_type == 'everynews' or news_type == 'every' or news_type == 'e':
        url_string += EVERYNEWS

    # Find
    if find != '' and find != '/none':
        url_string += (FIND + find.replace(' ', '-') + '&')

    # Source
    if source != '' and source != '/none':
        url_string += (SOURCE + source.replace(' ', '-') + '&')

    # API key
    url_string += API_KEY

    return url_string
