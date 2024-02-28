import requests, os
import json
import dataBaseNames as DB
from difflib import SequenceMatcher # схожести строк

#для работы с гугл таблицами(3)
import httplib2
from googleapiclient.discovery import build 
from oauth2client.service_account import ServiceAccountCredentials


headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62"}
url_XHR = 'https://crossoutdb.com/data/search?l=undefined&_=1670609044331'
url_recipe = 'https://crossoutdb.com/api/v1/recipe/'
url_Salvager = 'https://crossoutdb.com/tools/salvage'

#ищет совпадения названий предметов по ключу 
def finder(name):
	#ДЛЯ УДОБСТВА НЕПОЛНОГО ВВОДА - ИЩЕМ СОВПАДЕНИЯ ПО КЛЮЧАМ
	_minSeq = 0.2
	_name = ''
	#алгоритм поиска большего совпадения названий
	for key in DB.MegaDict.keys():
		seq = SequenceMatcher(None, name, key).ratio()
		if (name.lower() in key.lower()) or (name.count(' ') > 0 and name.split(' ')[1].lower() in key.lower()) or (seq > 0.65):
			if seq > _minSeq:
				_minSeq = seq
				_name = key
	if _name == '':
		return (-1)
	else:
		return(_name)

async def CheckCharacteristic(itemNameKey, session):
	# ВОЗРАЩАЕТ ТТХ ОРУЖИЯ (parser javaScript)

	if itemNameKey not in DB.MiniDict: itemNameKey = finder(itemNameKey)
	if itemNameKey == -1: return(-1)

	########################## ЗОНА ПОДКЛЮЧЕНИЯ И ПАРСИНГА crossout db JSON ==> LIST ##########################
	response = requests.get(url_XHR, headers=headers)
	json_data = json.loads(response.text)  # сложная структура: {"data":[{"id":1,"name":...}]}
	list_items = []  # список словарей с инфой о предмете # {'id': 1, 'name': 'Thunderbolt',...} {}
	for item in json_data['data']:
		list_items.append(item)
	########################## ЗОНА ОТПРАВКИ ОТВЕТА ##########################
	item_info = {}
	for i in list_items:
		if i['name'] == DB.MegaDict[itemNameKey]:
			item_info = i
			break
	########################## ЗОНА РЕНДЕРА ДЖАВА СКРИПТА ##########################

	name = itemNameKey.replace(' ', '_').replace('(пов.)', 'ST')

	r = await session.get(f'https://crossout.fandom.com/ru/wiki/{name}', headers=headers)
	t = r.html.find('.mw-parser-output')
	l = t[0].text.split('\n')
	#print(l)
	# важный фикс ###################
	if len(l) == 0:
		return (-2)

	d = {}

	d['rare'] = item_info['rarityName']
	d['name'] = '꧁ ' + itemNameKey + ' ꧂'
	d['image'] = 'https://crossoutdb.com' + str(item_info['imagePath'])
	d['Категория'] = item_info['categoryName']

	if  len(r.html.find('.wiki_gold')) > 0:
		d['★ Перк'] = r.html.find('.wiki_gold')[0].text

	#ОБЩАЯ ИНФА ДЛЯ ВСЕХ ПРЕДМЕТОВ
	for i in range(0, len(l)-1):
		if 'Очков мощи' in l[i]: d['Очки мощи'] = l[i].split(' ')[0]
		if l[i] == 'Масса': d['Масса'] = l[i+1]
		if l[i] == 'Прочность': d['Прочность'] = l[i+1]
		if l[i] == 'Описание':
			#d['Описание'] = l[i+1] #люди решили убрать лор игры
			d['Описание'] = ''
			for j in range(i+2, len(l) - 1):
				if l[j] in ['Получение', 'Производство', 'Улучшения', 'См. также', 'История', 'Внешний вид', 'Примечания', 'Примечание', 'Галерея', 'Получение на других серверах', 'Галарея', 'Видео']:
					i = len(l)-1 #покидаем цикл по ттх с вики 999IQ =)
					break
				else:
					d['Описание'] += '\n' + '◆ ' + l[j]


	if d['Категория'] == 'Movement' or d['Категория'] == None:
		#MOVEMENT
		for i in range(0, len(l) - 1):
			if l[i] == 'Макс. скорость': d['Макс. скорость'] = l[i + 1]
			if l[i] == 'Грузоподъемность': d['Грузоподъемность'] = l[i + 1]
			if l[i] == 'Штраф на мощность': d['Штраф на мощность'] = l[i + 1]
			if l[i] == 'Тяга': d['Тяга'] = l[i + 1]

	elif d['Категория'] == 'Cabins' or d['Категория'] == None:
		#CABINS
		for i in range(0, len(l) - 1):
			if l[i] == 'Макс. скорость': d['Макс. скорость'] = l[i + 1]
			if l[i] == 'Грузоподъемность': d['Грузоподъемность'] = l[i + 1]
			if l[i] == 'Предельная масса': d['Предельная масса'] = l[i + 1]
			if l[i] == 'Дает энергии': d['Дает энергии'] = l[i + 1]
			if l[i] == 'Мощность': d['Мощность'] = l[i + 1]

	elif d['Категория'] == 'Weapons' or d['Категория'] == None:
		# WEAPONS
		for i in range(0, len(l) - 1):
			if l[i] == 'Расход энергии': d['Расход энергии'] = l[i + 1]

	elif d['Категория'] == 'Hardware' or d['Категория'] == None:
		# HARDWARE
		for i in range(0, len(l) - 1):
			if l[i] == 'Расход энергии': d['Расход энергии'] = l[i + 1]
			if l[i] == 'Дает энергии': d['Дает энергии'] = l[i + 1]
			if l[i] == 'Урон взрывом': d['Урон взрывом'] = l[i + 1]
			if l[i] == 'Радиус взрыва': d['Радиус взрыва'] = str(int(l[i + 1][:1]) * 3) + ' пинов'
			if l[i] == 'Макс. скорость': d['Макс. скорость'] = l[i + 1]
			if l[i] == 'Мощность': d['Мощность'] = l[i + 1]
			if l[i] == 'Предельная масса': d['Предельная масса'] = l[i + 1]
			if l[i] == 'Грузоподъемность': d['Грузоподъемность'] = l[i + 1]


	#"Cabins Weapons Hardware Movement"

	#print(d['Описание'])

	if d.get('Очки мощи') == None:
		return (-2)
	elif len(item_info) == 0:
		return (-1)
	else:
		return (d)


async def CheckBadgesProfit(session):
	#ЧЕКАЕМ ПРОФИТ С ОБМЕНА ЗНАЧКОВ
	r = await session.get('https://crossoutdb.com/tools/badgeexchange', headers=headers)
	t = r.html.find('.card.my-1')
	l = t[0].text.split('\n')

	d = {}
	for i in range(0, len(l)):
		if l[i] == 'True':
			d[l[i-1]] = l[i+5]

	d = dict(sorted(d.items(), key=lambda item: item[1], reverse=True)) #сортировка по убыванию 0_о =)

	if len(d) == 0:
		return (-1)
	else:
		return (d)

async def CheckUp(itemNameKey, session):
	# ВОЗРАЩАЕТ АПЫ ПРЕДМЕТА (parser javaScript)

	itemNameKey = finder(itemNameKey)
	if itemNameKey == -1: return(-1)

	########################## ЗОНА ПОДКЛЮЧЕНИЯ И ПАРСИНГА JSON ==> LIST ##########################
	response = requests.get(url_XHR, headers=headers)
	json_data = json.loads(response.text)  # сложная структура: {"data":[{"id":1,"name":...}]}
	list_items = []  # список словарей с инфой о предмете # {'id': 1, 'name': 'Thunderbolt',...} {}
	for item in json_data['data']:
		list_items.append(item)
	########################## ЗОНА ОТПРАВКИ ОТВЕТА ##########################
	item_info = {}
	for i in list_items:
		if i['name'] == DB.MegaDict[itemNameKey]:
			item_info = i
			break
	########################## ЗОНА РЕНДЕРА ДЖАВА СКРИПТА ##########################

	d = {}

	d['rare'] = item_info['rarityName']

	if d['rare'] == 'Common':
		return (-1)

	d['name'] = '꧁ ' + itemNameKey + ' ꧂'

	d['image'] = 'https://crossoutdb.com' + str(item_info['imagePath'])
	d['Категория'] = item_info['categoryName']

	name = itemNameKey.replace(' ', '_').replace('(пов.)', 'ST')
	r = await session.get(f"https://crossout.fandom.com/ru/wiki/{name}", headers=headers)

	t = r.html.find('.mw-parser-output')

	# важный фикс ###################
	if len(t) == 0:
		return (-2)

	l = t[0].text.split('\n')


	upList = []
	for i in range(0, len(l)):
		if l[i] == 'Улучшение':
			if 'незавершенная статья' in l[i+1]:
				return (-2)
				break
			else:
				for j in range(1,13):
					# БЫВАЕТ МЕНЬШЕ 3-ЁХ АПОВ У ПРЕДМЕТА (2,1)
					if l[i+j] in ['См. также', 'История', 'Внешний вид', 'Примечания', 'Примечание', 'Галерея', 'Получение на других серверах', 'Галарея', 'Видео' ]:
						break
					upList.append(l[i+j][2:])
				break

	if len(upList) == 0:
		return (-1)

	upList.insert(0, d) #вернём словарь в списке 

	return (upList)



async def CheckPriceAndRecipe(itemNameKey):

	if itemNameKey not in DB.MegaDict:
		itemNameKey = finder(itemNameKey)
	if itemNameKey == -1: return(-1)

	#print(itemNameKey)

	########################## ЗОНА ПОДКЛЮЧЕНИЯ И ПАРСИНГА JSON ==> LIST ##########################
	response = requests.get(url_XHR, headers=headers)
	json_data = json.loads(response.text)  # сложная структура: {"data":[{"id":1,"name":...}]}
	list_items = []  # список словарей с инфой о предмете # {'id': 1, 'name': 'Thunderbolt',...} {}
	for item in json_data['data']:
		list_items.append(item)
	########################## ЗОНА ОТПРАВКИ ОТВЕТА ##########################
	item_info = {}
	for i in list_items:
		if i['name'] == DB.MegaDict[itemNameKey]:
			item_info = i
			break
	########################## ЗОНА ПОДКЛЮЧЕНИЯ И ПАРСИНГА JSON ==> LIST ##########################.

	if len(item_info) == 0:
		return (-1)

	############### ЗАПОЛНЕНИЕ ИНФОЙ ПРО РЫНОК #############
	megaList = []
	# основная инфа о самом предмете: [0]

	megaList.append({'name': '꧁ ' + itemNameKey + ' ꧂', 'rare': item_info['rarityName'],
					'image': 'https://crossoutdb.com'+item_info['imagePath'],
					'categoryName': item_info['categoryName']})

	if 'Wheel' in item_info['typeName'] or 'wheel' in item_info['typeName']:
		megaList[0]['sellPrice'] = str(float(item_info['formatSellPrice']) * 2)
		megaList[0]['buyPrice'] = str(float(item_info['formatBuyPrice']) * 2)
	else:
		megaList[0]['sellPrice'] = item_info['formatSellPrice']
		megaList[0]['buyPrice'] = item_info['formatBuyPrice']


	if item_info['craftingMargin'] == 0:
		return (megaList)

	######################## ВТОРAЯ ЗОНА РЕЦЕПТА: #########################

	_url_recipe = url_recipe + str(item_info['id'])
	response = requests.get(_url_recipe, headers=headers)
	json_data = json.loads(response.text)  # сложная структура: {"recipe":{"id":1,"name":...}}

	#for k,v in json_data['recipe'].items():

	# стоимость крафта по вышке и по нижней [1,2]
	# megaList.append(json_data['recipe']['sumSellFormat'])
	# megaList.append(json_data['recipe']['sumBuyFormat'])


	sumCraftSellPrice = 0
	sumCraftBuyPrice = 0
	#смотрим стоимость ингредиентов
	for i in json_data['recipe']['ingredients']:
		d = {}
		d['название'] = i['item']['availableName']

		if i['number'] < 100:
			d['количество'] = ' — ' + str(i['number'])     
		else:
			d['количество'] = ' — ' + str(i['number'] / 100) #для ресов делим на 100

		if 'Engraved casings' in d['название']: #фикс цены ГИЛЬЗ в 100 раз большей
			d['цены'] = f"{i['item']['formatSellPrice']} / {i['item']['formatBuyPrice']}"
			sumCraftSellPrice += float(i['item']['formatSellPrice'])
			sumCraftBuyPrice += float(i['item']['formatBuyPrice'])
		else:
			d['цены'] = i['formatSellPriceTimesNumber'] + ' / ' + i['formatBuyPriceTimesNumber']
			sumCraftSellPrice += float(i['formatSellPriceTimesNumber'])
			sumCraftBuyPrice += float(i['formatBuyPriceTimesNumber'])

		megaList.append(d)

	megaList.insert(1, "%.2f" % sumCraftSellPrice)
	megaList.insert(2, "%.2f" % sumCraftBuyPrice)

	return (megaList)


###################################################################
##########################ПРЕМИУМ КОМАНДЫ##########################
###################################################################
async def PremiumCharacteristic(itemNameKey):

	if itemNameKey not in DB.MiniDict: itemNameKey = finder(itemNameKey)
	if itemNameKey == -1: return(-1)

	#ЗАПРОС В ТАБЛИЦУ
	def get_service_sacc():
		#################################
		# JSON GOOGLEAPI В СЕКРЕТКЕ
		creds_json = json.loads(os.environ['googleJson'])
		#####################
		scopes = ['https://www.googleapis.com/auth/spreadsheets']
		creds_service= ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scopes).authorize(httplib2.Http())

		DISCOVERY_SERVICE_URL = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
		return build('sheets', 'v4', http=creds_service,  discoveryServiceUrl=DISCOVERY_SERVICE_URL)

	service = get_service_sacc()
	sheet = service.spreadsheets()
	# АДРЕСС ТАБЛИЦЫ ИЗ АДРЕССНОЙ СТРОКИ
	sheet_id = '1YuXuHZQ2cFyapbvl90WZjlA6JAjTBIrx3ltMm2a_k4c'
	response = sheet.values().get(spreadsheetId=sheet_id, range='ТТХ оружия').execute()

	# парсер таблицы
	all = response['values'][1:] #список списков всех ячеек *** {name:'',values:[[]]}
	columns = all[0] #названия столбиков
	dt = {} #{'Ом':'123',}


	_item = None
	_maxRatio = 0.25
	for i in all:
		if len(i) > 5: #поиск названия предмета в столбике
			if i[1].lower() in itemNameKey.lower():
				if SequenceMatcher(None, i[1].lower(), itemNameKey.lower()).ratio() > _maxRatio:
					_item = i
					_maxRatio = SequenceMatcher(None, i[1].lower(), itemNameKey.lower()).ratio()

	for i in range(0, len(_item)):
		dt[columns[i]] = str(_item[i])

	#print(dt)
	if len(dt) < 5: #примерно (не нашел предмета)
		return (-1)
	else:
		return (dt)


###################################################################
##########################РАЗБОР ДЕКОРА############################
###################################################################
async def Salvager(session):
	r = await session.get(url_Salvager, cookies={'language': 'ru'})
	# await r.html.arender(reload=False) # render нужен только для пк

	t = r.html.find('tbody')  # НАЗВАНИЯ на русском #

	items = [] #кортежи
	l = str(t[6].text).split('\n')
	for i in range(len(l)):
		if i % 10 == 0:
			# print(l[i], l[i+3], l[i+4], l[i+7]) # Теплообмен 49.82 57.42 1.86
			items.append((l[i], l[i+3], l[i+4], float(l[i+7])))

	#сортируем по выгоде c разбора декора
	sorted_items = sorted(items, key=lambda x: x[3], reverse=True)

	if len(sorted_items) < 15:
		return (-1)
	else:
		return (sorted_items[:15])
