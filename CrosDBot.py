import requests
import json
from bs4 import BeautifulSoup
from time import sleep
import re
from difflib import SequenceMatcher # схожести строк
from googletrans import Translator
trans = Translator()

def CheckPrice(text):
    ########################## ЗОНА ПОДКЛЮЧЕНИЯ И ПАРСИНГА JSON ==> LIST ##########################

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62"}
    url = f'https://crossoutdb.com'

    url_XHR = f'https://crossoutdb.com/data/search?l=undefined&_=1670609044331'
    # sleep(2)
    response = requests.get(url_XHR, headers=headers)
    json_data = json.loads(response.text) # сложная структура: {"data":[{"id":1,"name":...}]}
    list_items = [] # список словарей с инфой о предмете # {'id': 1, 'name': 'Thunderbolt',...} {}
    for item in json_data['data']:
        list_items.append(item)

    ########################## ЗОНА ПЕРЕВОДА ##########################

    default_name_item = text #запрос человека без '!р '

    if not(re.search(r'[^0-9a-zA-Z]', default_name_item.replace(' ', ''))): #проверка на ТОЛЬКО ЛАТИНИЦУ И ЦИФРЫ
        name_item = default_name_item # en = en
    else:   # есть русские символы ==> переводим
        name_item = trans.translate(default_name_item).text  # en -> run

    ########################## ЗОНА РАЗБИЕНИЯ ЗАПРОСА НА СЛОВА ##########################

    x = y = z = 'XXXXXXXXX'
    if name_item.find(' ') != -1: # ЕСЛИ ЗАПРОС БЕЗ ПРОБЕЛОВ СПЛИТ ЛОМАЕТСЯ =)
        if len(name_item.split()) > 0: x = name_item.split()[0]
        if len(name_item.split()) > 1: y = name_item.split()[1]
        if len(name_item.split()) > 2: z = name_item.split()[2]

    ########################## ЗОНА ПОИСКА ПРЕДМЕТА В XHR ЗАПРОСЕ ##########################

    item_info = {} # словарь* инфы найденного предмета
    max_coincidence = 0.33

    for i in list_items:

        coincidence = SequenceMatcher(None, str(i['name']).lower(), name_item.lower()).ratio() # схожесть названий в одном регистре

        if str(i['name']).lower().find(x.lower()) != -1: # если нашел слово целиком
             coincidence += 0.35 # ПЕРВОЕ СЛОВО ДОРОЖЕ ВТОРОГО =)
        if str(i['name']).lower().find(y.lower()) != -1: # если нашел слово целиком
             coincidence += 0.15
        if str(i['name']).lower().find(z.lower()) != -1:  # если нашел слово целиком
             coincidence += 0.15

        if coincidence > max_coincidence: # сортировка предметов на наибольшую схожесть
            max_coincidence = coincidence
            item_info.clear()
            item_info = i

    print(max_coincidence)

    if len(item_info) == 0:
        return (-1)
    else:
        dict_info = {'name': item_info['name'], 'type': item_info['typeName'],
                 'rare': item_info['rarityName'], 'buyPrice': item_info['formatBuyPrice'],
                 'sellPrice': item_info['formatSellPrice'], 'orders': item_info['buyOrders'],
                 'offers': item_info['sellOffers'], 'image': 'https://crossoutdb.com' + str(item_info['imagePath'])}

        return (dict_info)



