import json
import os

import scraper as s
import pandas as pd

from config import RING_TYPES, STONE_TYPES, STONE_SHAPES, RING_MATERIALS, STONE_COLORS

#

ATTRIBUTES = {'RING_TYPES': RING_TYPES, 'STONE_TYPES': STONE_TYPES, 'STONE_SHAPES': STONE_SHAPES,
              'RING_MATERIALS': RING_MATERIALS, 'COLORS': STONE_COLORS}

URL_TEMPLATE = 'https://www.pinterest.com/{}/'

more_ideas_xpath = '_tf _0 _1 _2 _tg _3c _b'

KEYWORDS = ['wedding', 'ring', 'engagement', 'wife', 'spouse']


def preprocess_board_name(name):
    remove_signs = ['#', '&', ':', "'", '.', ',', ':', "'", '!', '%', '?']
    for sign in remove_signs:
        name = name.replace(sign, '')
    name = name.strip()
    return name.lower().replace(' ', "-").replace('---', '-').replace('--', '-')


def get_board_links(ph, pinterest_account):
    account_template = URL_TEMPLATE.format(pinterest_account)
    boards_url = account_template + 'boards/'
    print('Boards url', boards_url)
    ph.browser.get(boards_url)
    s.randdelay(1, 2)

    all_follows = []
    last_height = ph.browser.execute_script("return document.body.scrollHeight")
    counter = 5

    while True:

        ph.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        s.randdelay(0.5, 1)

        follows = ph.browser.find_elements_by_xpath(
            '//div[contains(@class, "{0}") and contains(@class, "{1}") and contains('
            '@class, "{2}")]'.format('_w7', '_0', '_wc'))
        all_follows.extend(follows)
        new_height = ph.browser.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            if counter != 0:
                counter -= 1
            else:
                break

        last_height = new_height

    print('Out of the loop')
    all_follows = list(set(all_follows))
    print(len(all_follows))
    print(all_follows)

    links_to_return = list(
        map(lambda x: account_template + preprocess_board_name(x.get_attribute('title')) + '/', all_follows))

    print('Links to return', links_to_return)
    relevant_links = []

    for keyword in KEYWORDS:
        word_presense = list(filter(lambda x: keyword in x, links_to_return))

        relevant_links.extend(word_presense)

    return relevant_links


def preprocess_account_name(pinterest_account):
    if 'pinterest.com' in pinterest_account:
        splitted = pinterest_account.split('/')
        splitted = list(filter(lambda x: x != '', splitted))
        return splitted[-1]
    else:
        return pinterest_account


def analyze_account(pinterest_account):

    pinterest_account = preprocess_account_name(pinterest_account)

    print('Analyze pinterest account', pinterest_account)
    ph = s.Pinterest_Helper('bpk@datarootlabs.com', 'MeBiUs72043')

    board_links = get_board_links(ph, pinterest_account)
    data_analyzed = {}
    print('Board links', board_links)
    if len(board_links) > 0:
        images, descriptions, final_info = [], [], []

        for board_link in board_links:
            images_local, descriptions_local, final_info_local = ph.runme(board_link, threshold=50)

            images.extend(images_local)
            descriptions.extend(descriptions_local)
            final_info.extend(final_info_local)

        print('Images are', images)
        print('Descriptions are', descriptions)
        print('Final info is', final_info)

        for attr_name, attr_values in ATTRIBUTES.items():
            attr_analysis = {}

            data_analyzed[attr_name] = attr_analysis
            for attr_value in attr_values:
                counter = 0

                for desc in descriptions:
                    if attr_value in desc:
                        counter += 1

                if counter > 0:
                    attr_analysis[attr_value] = counter

            if len(attr_analysis) > 0:
                attr_analysis = sorted(attr_analysis.items(), key=lambda x: x[1], reverse=True)

                data_analyzed[attr_name] = attr_analysis
    # else:
    #     data_analyzed['error'] = "Sorry, couldn't find any relevant boards"

    ph.browser.quit()
    return data_analyzed

#
# if __name__ == '__main__':
#     analyzed_account = analyze_account('mennha88')
#     print('Analyzed account', analyzed_account)
