from requests import get
from lxml import html
from lxml import etree
from time import sleep
from random import randrange
import re
import pandas as pd


def pars_page(number_page, timeout):
    sleep(timeout)

    url = 'https://rateyourmusic.com/customchart?page=' + str(number_page) \
          + '&chart_type=top&type=album&year=alltime&genre_include=' + \
          '1&include_child_genres=1&genres=&include_child_genres_chk=' + \
          '1&include=both&origin_countries=&limit=none&countries='

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                      + '(KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    }

    r = get(url, headers=headers)


    with open('customchart.html', 'w', encoding='utf-8') as output_file:
        text_ = r.text
        output_file.write(text_.encode().decode('utf-8', 'ignore'))


def sort(page_text, n):
    tree = html.fromstring(page_text)

    try:
        table_mbgen_xml = tree.xpath('//table[@class="mbgen"]')[0]
    except:
        print("\nОшибка запроса к серверу\n")
    else:
        chart_main_xml = table_mbgen_xml.xpath('//div[@class="chart_main"]')[n]
        chart_stats_xml = table_mbgen_xml.xpath('//div[@class="chart_stats"]')[n]

        chart_main_xml = etree.tostring(chart_main_xml)
        chart_stats_xml = etree.tostring(chart_stats_xml)

        stats = re.findall(r'(?<=<b>).*?(?=</b>)', str(chart_stats_xml))
        artist = re.findall(r'(?<=\ class="artist">).*?(?=</a>)', str(chart_main_xml))

        # В значених "rating", "reviews" удаляем запятые и приводим к типу int
        result = {
            'artist': artist[0],
            'rim_rating': float(stats[0]),
            'rating': int(re.sub(',', '', stats[1])),
            'reviews': int(re.sub(',', '', stats[2]))
        }

        return result


if __name__ == '__main__':
    # Создаем пустой DataFrame
    frame = pd.DataFrame(columns=['artist',
                                  'rim_rating',
                                  'rating', 'reviews'],
                         index=[0])
    # Парсим страницу
    print("\n")
    for i in range(1, 25):
        print("Парсим страницу номер: ", i, " ...")
        pars_page(i, randrange(60, 85))

        with open('customchart.html', 'r', encoding='utf-8') as input_file:
            text = input_file.read()

        # Собираем исполнителей в DataFrame с одной  страницы
        for j in range(40):
                text_page = sort(text, j)

                frame = frame.append(text_page, ignore_index=True)

    print("\nПарсинг завершен\n")

    # Удаляем пустую строку
    frame = frame.drop([0], axis=0)

    # Сохраняем DataFrame
    frame.to_csv('data.csv', sep=',', header=True, index=['#'])
    print(frame)
