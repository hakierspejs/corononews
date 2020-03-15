#!/usr/bin/env python

import flask
import requests
import lxml.html
import logging

app = flask.Flask(__name__)
LOGGER = logging.getLogger(__name__)
HN_BASE_URL = 'https://news.ycombinator.com/'

def has_virus(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        return True
    s = requests.get(url).text.lower()
    for w in ['covid', 'virus']:
        if w in s:
            return True
    return False

@app.route('/')
def main():
    h = lxml.html.fromstring(requests.get(HN_BASE_URL).text)
    ret = '<ol>'
    for n, row in enumerate(h.xpath('//tr [@id]')[1:]):
        story = row.xpath('.//a [@class="storylink"]').pop()
        LOGGER.info('%d: %s', n, story.get('href'))
        c_row = row.getnext()
        comments = c_row.xpath('.//a [contains(@href, "item?id=")]')[-1]
        comments_url = HN_BASE_URL + comments.get('href')
        if has_virus(story.get('href')) or has_virus(comments_url):
            continue
        ret += f'''
            <li>
                <a href="{story.get("href")}">{story.text}</a>
                (<a href="{comments_url}">{comments.text}</a>)
            </li>'''
    return ret


if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    app.run(host='0.0.0.0')
