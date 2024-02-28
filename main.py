import os, time, datetime, random
import disnake
from disnake.ext import commands
from disnake import TextInputStyle
from googletrans import Translator
translator = Translator()

from replit import db
import dataBaseNames
import CrossDBot
import keep_alive

from requests_html import AsyncHTMLSession
session = AsyncHTMLSession()

client = commands.Bot(intents=None) #подключение всех интентов --> disnake.Intents.all() ) #, test_guilds=[739987305934356520]) гильдии - это Id сервера на котором можно юзать бота*
LOGOTYPE = 'https://media.discordapp.net/attachments/1060658288523477032/1089806782471360644/my_choise_HDR_zoom.png'
HELP_IMAGE = 'https://media.discordapp.net/attachments/1060658288523477032/1089809768639627326/HELP.jpg'

AD_message = f'https://media.discordapp.net/attachments/1053950932662112279/1142788855125258280/ad.png' # МОЯ РЕКЛАМКА

# чел BiKend_2.0#3693 купил рекламу на 2 недели (31 марта до 14 апреля| 18апр-2мая| 16mai-30mai| 21-28авг)
# 300 + 420 + 250 + 200rub.

# декоратор (события) у функций определнные названия

@client.event
async def on_ready():
	############################################################################################################

	print(f'Bot {client.user} is ready to work!')
	await client.change_presence(activity=disnake.Game(name=f'/помощь | {len(client.guilds)} серверов!'))


@commands.guild_only()
@client.slash_command(description='Сравнение ТТХ орудий от 2 до 5 шт.')
async def сравнить(inter: disnake.ApplicationCommandInteraction,
						name1: str = commands.Param(autocomplete=dataBaseNames.weaponsAutocomplet, description='Название 1 орудия', name='предмет1'),
						name2: str = commands.Param(autocomplete=dataBaseNames.weaponsAutocomplet, description='Название 2 орудия', name='предмет2'),
						name3: str = commands.Param(autocomplete=dataBaseNames.weaponsAutocomplet, description='Название 3 орудия', name='предмет3', default=''),
						name4: str = commands.Param(autocomplete=dataBaseNames.weaponsAutocomplet, description='Название 4 орудия', name='предмет4', default=''),
						name5: str = commands.Param(autocomplete=dataBaseNames.weaponsAutocomplet, description='Название 5 орудия', name='предмет5', default='')):
	await inter.response.defer() # БОТ ДУМАЕТ ...
	names = [name1, name2, name3, name4, name5]
	list_names = [str(i) for i in names if i != '']

	print('list_names: ', list_names, inter.author)
	#получили список словарей ттх о предметах 
	items_info = []
	for i in list_names:
		x = await CrossDBot.PremiumCharacteristic(i)
		if x != -1: 
			items_info.append(x)


	######## ОСНОВНОЙ БЛОК ########
	embed = disnake.Embed(
		title=f'꧁ Сравнение ТТХ ꧂',
		description= 
		f"**{' | '.join(list_names)}**\n\n",
		color=0xA52A2A)

	dt = {}
	for i in items_info: #ОБЪЕДЕНЯЕМ ЗНАЧЕНИЯ СЛОВАРЕЙ С ОДИНАКОВЫМИ КЛЮЧАМИ В ОДИН
		for k, v in i.items():
			#if k in ['ОМ', 'Прочность', 'Энергопотребление', 'Масса',
			#		 'ДПС', 'Урон / доп урон', 'Сплеш', 'Перезарядка', 'Боезапас',
			#		 'Отдача', 'Импульс', 'Максимальная дальность', 'Оптимальная дальность',
			#		 'Скорость снаряда', 'Время до нагрева', 'Разброс MIN', 'Разброс MAX',]:
			if k not in ['', 'Название']:
				if k in dt:
					dt[k] += ' | ' + v
				else:
					if v not in ['- / -', '-']:
						dt[k] = v

	#print(dt)
	info = ''
	for k, v in dt.items():
		info += f"**{k}** \n ㅤ{v} \n" 

	#print('\n\n', len(info), '\n\n', info)

	# ТТХ предмета:
	embed.add_field(
		name='__Результаты:__ \n',
		value=info,
		inline=False
	)

	#картинка в правом углу (gid sravnenie)
	embed.set_thumbnail('https://media.discordapp.net/attachments/1060658288523477032/1089813726288433182/sravnenie.gif') 
	setAuthor(embed)
	await inter.edit_original_response(
		embed=embed,
		components=[
			disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
			disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
		])

	if random.randint(1,3) == 1: #вер-ть рекламы 33%
		await inter.followup.send(AD_message) #отправляет второй ответ (рекламу)



@commands.guild_only()
@client.slash_command(description='ПОДРОБНЫЕ ТТХ орудия.')
async def ттх(inter: disnake.ApplicationCommandInteraction, name: str = commands.Param(autocomplete=dataBaseNames.weaponsAutocomplet, description='Название предмета в игре', name='название')):

	await inter.response.defer() # БОТ ДУМАЕТ ...

	print(f'[ТТХ +] {inter.author}')

	item_info = await CrossDBot.PremiumCharacteristic(name) #словарь с ттх

	if item_info == -1:
		embed = disnake.Embed(
			title='Выберите подходящий предмет из выпадающего списка.',
			description=f'(Если вы выбрали и не нашли, то у {name} нет характеристик).',
			color=0xFF00FF)
		# справка как выбрать предмет
	else:
		######## ОСНОВНОЙ БЛОК ########
		embed = disnake.Embed(
			title=f'꧁ {name} ꧂',
			description= 
			f"**Подробные ТТХ:**\n\n",
			color=0x7FFF00)

		info = ''
		for key, value in item_info.items():
			if key != '' and value != '' and value != ' ' and value != '-':
				info += f"• **{key} — ** {value} \n"

		# ТТХ предмета:
		embed.add_field(
			name='__Описание:__ \n',
			value=info,
			inline=False
		)

	#картинка в правом углу
	embed.set_thumbnail(LOGOTYPE) 
	setAuthor(embed)

	await inter.edit_original_response(
		embed=embed,
		components=[
			disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
			disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
		])

	if random.randint(1,3) == 1: #вер-ть рекламы 33%
		await inter.followup.send(AD_message) #отправляет второй ответ (рекламу)


@client.slash_command(description='Информация о боте и командах')
@commands.guild_only()
async def помощь(inter: disnake.ApplicationCommandInteraction):

	await inter.response.defer() # БОТ ДУМАЕТ ...

	print(f'[Помощь] {inter.author}')

	embed = disnake.Embed(
		title='Информация о боте',
		description= 
		f"**Привет!** Мы рады, что вы выбрали нас! \n Это рыночный бот для игры Crossout. \n" + \
		f"Прежде чем отправить команду боту, убедитесь, что вы выбрали название предмета из выпадающего списка. \n\n" + \
		f"__**Описание команд бота:**__ \n " + \
		f"```/р``` — стоимость и крафт предмета. \n" + \
		f"```/ттх``` — характеристики предмета. \n" + \
		f"```/ап``` — улучшения предмета. \n" + \
		f"```/разбор_декора``` — список выгодного декора для разбора. \n" + \
		f"```/сравнить``` — сравнить ТТХ предметов (от 2 до 5 шт.) \n" + \
		f"```/значки``` — узнать выгодность обмена значков. \n" + \
		f"```/репорт``` — отправить баг-репорт в поддержку. \n\n" + \
		f"__**Чтобы добавить бота на свой сервер нажмите выше '[Добавить бота на свой сервер]'**__ \n\n" + \
		f"__**Дискорд сервер бота:**__ \n" + \
		f"https://discord.gg/H6Ep8AeSDs ",
		color=0x7FFF00)

	embed.set_image(HELP_IMAGE)
	#картинка в правом углу
	embed.set_thumbnail('https://media.discordapp.net/attachments/1053653369715171409/1058352742650884106/download.gif') 

	setAuthor(embed)

	#await inter.response.send_message(embed=embed)

	await inter.edit_original_response(
		embed=embed,
		# КНОПКИ
		components=[
			disnake.ui.Button(label="👉Добавить бота", style=disnake.ButtonStyle.link, url='https://discord.com/api/oauth2/authorize?client_id=1051367559481544707&permissions=2148059136&scope=applications.commands%20bot'),
			disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
			disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
		]
	)


@client.slash_command(description='Выгодность обмена значков.')
@commands.guild_only()
async def значки(inter, _name: str = ''):

	await inter.response.defer() # БОТ ДУМАЕТ ...

	#print('test',_name)

	print(f'[Значки] {inter.author}')
	item_info = await CrossDBot.CheckBadgesProfit(session)

	#ИСКЛЮЧЕНИЕ, ЕСЛИ НЕ УДАЛОСЬ НАЙТИ
	if item_info == -1:
		embed = disnake.Embed(
			title='Ошибка.',
			description='(Повторите попытку позже).',
			color=0xFF00FF)
	else:
		_color = 0x00FF7F

		embed = disnake.Embed(
			title='Выгода обмена значков',
			description=str('Расчёт монет на 1 значок:'),
			color=_color)

		setAuthor(embed)
		#картинка значка
		embed.set_thumbnail('https://sun9-65.userapi.com/impg/FcViCFKTkQXjgSeor1f0qbvsbSvwKHwRC0xpHQ/gwr-0qm44hI.jpg?size=430x430&quality=96&sign=96d9a7be7d5b084ea6e81d99fa458590&type=album')

		######## ОСНОВНОЙ БЛОК ########
		info = ''
		for key, value in item_info.items():
			name = translator.translate(str(key), dest='ru').text
			if 'Batteries' in key: name = 'Аккумуляторы ' + key.split()[1]
			info += f"▸ **{name} — ** {value} :coin: \n"


		# резы
		embed.add_field(
			name='__Результаты по убыванию:__ \n',
			value=info,
			inline=False
		)


	if _name != '' and CrossDBot.finder(_name.split('@')[0]) != -1:
		# КНОПКА НАЗАД
		_history = ''

		if len(_name.split('@')) > 0:
			for i in range(0, len(_name.split('@'))):
				_history += _name.split('@')[i] + '@'

		await inter.edit_original_response(
			embed=embed,
			# КНОПКИ
			components=[
				disnake.ui.Button(label="⏪", style=disnake.ButtonStyle.blurple, custom_id=f"market {_name.replace(' ','#')}"),
				disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
				disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
			]
		)
	elif '@' not in _name and _name != '':
		await inter.edit_original_response(
			embed=embed,
			# КНОПКИ
			components=[
				disnake.ui.Button(label="⏪", style=disnake.ButtonStyle.blurple, custom_id=f"market {_name.replace(' ', '#')}"),
				disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
				disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
			]
		)
	else:
		await inter.edit_original_response(
			embed=embed,
			# КНОПКИ
			components=[
				disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
				disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
			]
		)

	if random.randint(1,3) == 1: #вер-ть рекламы 33%
		await inter.followup.send(AD_message) #отправляет второй ответ (рекламу)

'''
#
# 	Временно убрал из бота (18 нояб 2023), т.к. апы убрали в крос вики, следовательно их негде брать.
#

@client.slash_command(description='Улучшения предмета.')
@commands.guild_only()
async def ап(inter: disnake.ApplicationCommandInteraction, name: str = commands.Param(autocomplete=dataBaseNames.miniAutocomplet, description='Название предмета в игре', name='название')):

	await inter.response.defer() # БОТ ДУМАЕТ ...

	# РОДИТЕЛЬ БУДЕТ ЕСЛИ ИДЁМ ПО ДЕРЕВУ КРАФТА Гром@Молотобой@Крушитель
	history = ''
	# история родителей
	if '@' in name:
		a = name.split('@')[0]
		if a == name.split('@')[-1]: history = name.split('@')[1:] #исключение когда батя уже есть в истории (круш@молотобой@круш)
		else: history = name
		name = a



	# ВАЖНО* ПЕРВЫЙ ЭЛЕМЕНТ СПИСКА ЭТО СЛОВАРЬ
	name = name[:1].title() + name[1:]
	print(f'[Апы] {inter.author} {name}')

	item_info = await CrossDBot.CheckUp(name, session)

	#ИСКЛЮЧЕНИЕ, ЕСЛИ НЕ УДАЛОСЬ НАЙТИ
	if item_info == -1:
		embed = disnake.Embed(
			title='Ошибка',
			description=f'(Возможно у {name} нет улучшений или повторите попытку позже).',
			color=0xFF00FF)

	elif item_info == -2:
		embed = disnake.Embed(
			title='Информацию не завезли =(',
			description='(Если хотите чтобы она появилась быстрее, отправте репорт).',
			color=0xFF00FF)
	else:
		# ВЫБОР ЦВЕТА ОТ РЕДКОСТИ ПРЕДМЕТА:
		_color = setColor(item_info[0]['rare'])

		embed = disnake.Embed(
			title=item_info[0]['name'],
			#description= translator.translate(item_info[0]['Категория'], dest='ru').text,
			description=' ',
			color=_color)

		setAuthor(embed)

		embed.set_thumbnail(item_info[0]['image'])

		######## ОСНОВНОЙ БЛОК ########
		info = ''
		for i in range(1, len(item_info)):
			if item_info[i] in ['Надежность', 'Мощь', 'Удобство']:
				info += f"■ **{item_info[i]}** \n"
			else:
				info += f"• {item_info[i]} \n"

		# резы
		embed.add_field(
			name='__Описание вариантов улучшений:__ \n',
			value=info,
			inline=False
		)

	################# ВЫЗОВ ЧЕРЕЗ КНОПКУ И ЕСТЬ РОДИТЕЛЬ ##################################
	if history != '':
		# Булава@Гром@Молотобой@Крушитель

		await inter.edit_original_response(
		embed=embed,
		# КНОПКИ
		components=[
			disnake.ui.Button(label="🛒Рынок", style=disnake.ButtonStyle.green, custom_id=f"market {history.replace(' ', '#')}"),
			disnake.ui.Button(label="📏ТТХ", style=disnake.ButtonStyle.green, custom_id=f"options {history.replace(' ', '#')}"),
			disnake.ui.Button(label="🍪Значки", style=disnake.ButtonStyle.blurple, custom_id=f"badges {name.replace(' ', '#')}"),
			disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
			disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
		]
	)
	else:
		await inter.edit_original_response(
			embed=embed,
			# КНОПКИ
			components=[
				# КП-18 Тайфун ---> КП-18#Тайфун - запихиваем в кнопку для удобной работы =)
				disnake.ui.Button(label="🛒Рынок", style=disnake.ButtonStyle.green, custom_id=f"market {name.replace(' ', '#')}"),
				disnake.ui.Button(label="📏ТТХ", style=disnake.ButtonStyle.green, custom_id=f"options {name.replace(' ', '#')}"),
				disnake.ui.Button(label="🍪Значки", style=disnake.ButtonStyle.blurple, custom_id=f"badges {name.replace(' ', '#')}"),
				disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
				disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
			]
		)

	if random.randint(1,3) == 1: #вер-ть рекламы 33%
		await inter.followup.send(AD_message) #отправляет второй ответ (рекламу)
'''

@client.slash_command(description='Цена и крафт предмета.')
@commands.guild_only()
async def р(inter: disnake.ApplicationCommandInteraction, name: str = commands.Param(autocomplete=dataBaseNames.autocomplet, description='Название предмета в игре', name='название')):

	await inter.response.defer() # БОТ ДУМАЕТ ...
	# РОДИТЕЛЬ БУДЕТ ЕСЛИ ИДЁМ ПО ДЕРЕВУ КРАФТА Гром@Молотобой@Крушитель
	history = ''
	# история родителей
	if '@' in name:
		a = name.split('@')[0]
		if a == name.split('@')[-1]: history = name.split('@')[1:] #исключение когда батя уже есть в истории (круш@молотобой@круш)
		else: history = name
		name = a

	#print('***test***', history)
	name = name[:1].title() + name[1:] # фикс когда КП-18 Тайфун ---> Кп-18 ...
	print(f'[КрафтРынок] {inter.author} {name}')

	item_info = await CrossDBot.CheckPriceAndRecipe(name)  # инфа о предмете dict{}

	#print(item_info)

	#ИСКЛЮЧЕНИЕ, ЕСЛИ НЕ УДАЛОСЬ НАЙТИ ТАКОЙ ПРЕДМЕТ
	if item_info == -1:
		embed = disnake.Embed(
			title='Выберите подходящий предмет из выпадающего списка.',
			description=f'(Если вы выбрали и не нашли, то {name} нет на рынке).',
			color=0xFF00FF)
		# справка как выбрать предмет

		await inter.edit_original_response(embed=embed)

	else:
		# ВЫБОР ЦВЕТА ОТ РЕДКОСТИ ПРЕДМЕТА:
		_color = setColor(item_info[0]['rare'])

		embed = disnake.Embed(
			title=item_info[0]['name'],
			description=str('Цены и крафт предмета:'),
			color=_color)

		setAuthor(embed)

		embed.set_thumbnail(item_info[0]['image'])

		######## ОСНОВНОЙ БЛОК ########
		Coin = ' :coin:'
		info = ''

		info += f"• Стоимость — **{item_info[0]['sellPrice']}{Coin} / {item_info[0]['buyPrice']}{Coin}**\n\n"
		info += f"• Перепродажа с комиссией 10% — **{'%.2f' % (float(item_info[0]['sellPrice']) * 0.9 - float(item_info[0]['buyPrice']))}{Coin}**\n"

		list_craft_items = [] #список оружий из списка крафта этого, чтобы смотреть их крафт
		# ИФ ЕСЛИ ПРЕДМЕТ КРАФТИТЬСЯ

		if len(item_info) > 1:

			info += f"• Купить ингредиенты для крафта — **{item_info[1]}{Coin} / {item_info[2]}{Coin}**\n"
			raznica = '%.2f' % (float(item_info[0]['sellPrice']) * 0.9 - float(item_info[2]))
			info += f"• Прибыль с крафта по __нижней__ и продажи по __верхней__ с комиссией 10% — **{raznica}{Coin}**\n\n"


			if float(item_info[2]) > float(item_info[0]['buyPrice']): #крафт по нижней дороже чем покупка по нижней
				info += f"• Крафт по нижней или покупать? — **ПОКУПАТЬ** экономия — **{'%.2f' % (float(item_info[2]) - float(item_info[0]['buyPrice']))}{Coin}**"
			else:
				info += f"• Крафт по нижней или покупать? — **КРАФТИТЬ** экономия — **{'%.2f' % (float(item_info[0]['buyPrice']) - float(item_info[2]))}{Coin}**"

			info += f"\n\n __**Ингредиенты**__ (продажа / покупка)\n"

			for i in range(3, len(item_info)):
				# иф если это НЕ "минимальная" цена аренды станка
				if 'Minimum' not in item_info[i]['название']:
					_name = ''

					for k,v in dataBaseNames.MeadleDict.items():
						if v == item_info[i]['название']: 
							_name = k #нашли русское название ингредиента по англ. значению
							if _name not in dataBaseNames.RESOURS:
								list_craft_items.append(_name)


					info += f"• *{_name}* **{item_info[i]['количество']}**\n"
					info += f"ㅤ**{item_info[i]['цены']}** {Coin}\n\n"

				else:
					info += f"◆ ***Аренда станка на 1 деталь***\n"
					info += f"ㅤ**{item_info[i]['цены'].split('/')[0]}** {Coin} \n"

			embed.add_field(
				name=' __Подсчёты:__\n',
				value= info,
				inline=False
			)
		else:
			info += f"• **{name}** сейчас нельзя скрафтить.\n"
			embed.add_field(
				name=' __**Цены:**__ \n',
				value= info,
				inline=False
			)

		#######################################  КНОПКИ  ######################################

		# предмет крафтиться из 3 разных / из 2 / из 1 / только из ресурсов (наоборот) ИЛИ ЭТО ДЕКОР/РЕСУРС/НАКЛЕЙКА/КРАСКА
		if item_info[0]['categoryName'] not in ['Cabins', 'Hardware', 'Movement', 'Weapons', None]:

			await inter.edit_original_response(
				embed=embed,
				components=[
					# КП-18 Тайфун ---> КП-18#Тайфун - запихиваем в кнопку для удобной работы =)
					disnake.ui.Button(label="🍪Значки", style=disnake.ButtonStyle.blurple, custom_id=f"badges {name.replace(' ', '#')}"),
					disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
					disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
				]
			)
		################# ВЫЗОВ ЧЕРЕЗ КНОПКУ И ЕСТЬ РОДИТЕЛЬ ##################################
		elif history != '' and CrossDBot.finder(history.split('@')[1]) != -1:
			# Булава@Гром@Молотобой@Крушитель
			_history = ''

			if len(history.split('@')) > 1:
				for i in range(1, len(history.split('@'))):
					_history += history.split('@')[i] + '@'

			print('line 451: history: ', history)

			if len(list_craft_items) == 0 :
				await inter.edit_original_response(
					embed=embed,
					components=[
						# КП-18 Тайфун ---> КП-18#Тайфун - запихиваем в кнопку для удобной работы =)
						disnake.ui.Button(label="⏪", style=disnake.ButtonStyle.blurple, custom_id=f"market {_history.replace(' ', '#')}"),
						disnake.ui.Button(label="🆙Апы", style=disnake.ButtonStyle.green, custom_id=f"ups {history.replace(' ', '#')}"),
						disnake.ui.Button(label="📏ТТХ", style=disnake.ButtonStyle.green, custom_id=f"options {history.replace(' ', '#')}"),
						disnake.ui.Button(label="🍪Значки", style=disnake.ButtonStyle.blurple, custom_id=f"badges {history.replace(' ', '#')}"),
						disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
						disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
					]
				)
			elif len(list_craft_items) == 1:
				await inter.edit_original_response(
					embed=embed,
					components=[
						disnake.ui.Button(label="⏪", style=disnake.ButtonStyle.blurple, custom_id=f"market {_history.replace(' ', '#')}"),
						disnake.ui.Button(label="🆙Апы", style=disnake.ButtonStyle.green, custom_id=f"ups {history.replace(' ', '#')}"),
						disnake.ui.Button(label="📏ТТХ", style=disnake.ButtonStyle.green, custom_id=f"options {history.replace(' ', '#')}"),
						disnake.ui.Button(label=f"🔽Крафт: {list_craft_items[0]}", style=disnake.ButtonStyle.green, custom_id=f"market {list_craft_items[0].replace(' ', '#')}@{history.replace(' ', '#')}"),

						disnake.ui.Button(label="🍪Значки", style=disnake.ButtonStyle.blurple, custom_id=f"badges {history.replace(' ', '#')}"),
						disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
						disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
					]
				)
			elif len(list_craft_items) == 2:
				await inter.edit_original_response(
					embed=embed,
					components=[
						disnake.ui.Button(label="⏪", style=disnake.ButtonStyle.blurple, custom_id=f"market {_history.replace(' ', '#')}"),
						disnake.ui.Button(label="🆙Апы", style=disnake.ButtonStyle.green, custom_id=f"ups {history.replace(' ', '#')}"),
						disnake.ui.Button(label="📏ТТХ", style=disnake.ButtonStyle.green, custom_id=f"options {history.replace(' ', '#')}"),
						disnake.ui.Button(label=f"🔽Крафт: {list_craft_items[0]}", style=disnake.ButtonStyle.green, custom_id=f"market {list_craft_items[0].replace(' ', '#')}@{history.replace(' ', '#')}"),
						disnake.ui.Button(label=f"🔽Крафт: {list_craft_items[1]}", style=disnake.ButtonStyle.green, custom_id=f"market {list_craft_items[1].replace(' ', '#')}@{history.replace(' ', '#')}"),

						disnake.ui.Button(label="🍪Значки", style=disnake.ButtonStyle.blurple, custom_id=f"badges {history.replace(' ', '#')}"),
						disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
						disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
					]
				)
			elif len(list_craft_items) == 3:
				await inter.edit_original_response(
					embed=embed,
					components=[
						disnake.ui.Button(label="⏪", style=disnake.ButtonStyle.blurple, custom_id=f"market {_history.replace(' ', '#')}"),
						disnake.ui.Button(label="🆙Апы", style=disnake.ButtonStyle.green, custom_id=f"ups {history.replace(' ', '#')}"),
						disnake.ui.Button(label="📏ТТХ", style=disnake.ButtonStyle.green, custom_id=f"options {history.replace(' ', '#')}"),
						disnake.ui.Button(label=f"🔽Крафт: {list_craft_items[0]}", style=disnake.ButtonStyle.green, custom_id=f"market {list_craft_items[0].replace(' ', '#')}@{history.replace(' ', '#')}"),
						disnake.ui.Button(label=f"🔽Крафт: {list_craft_items[1]}", style=disnake.ButtonStyle.green, custom_id=f"market {list_craft_items[1].replace(' ', '#')}@{history.replace(' ', '#')}"),
						disnake.ui.Button(label=f"🔽Крафт: {list_craft_items[2]}", style=disnake.ButtonStyle.green, custom_id=f"market {list_craft_items[2].replace(' ', '#')}@{history.replace(' ', '#')}"),

						disnake.ui.Button(label="🍪Значки", style=disnake.ButtonStyle.blurple, custom_id=f"badges {history.replace(' ', '#')}"),
						disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
						disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
					]
				)
		###################### ЕСЛИ НЕТ РОДИТЕЛЯ (ДЕФОЛТ ВЫЗОВ ЧЕРЕЗ КОМАНДУ) ###########
		else:
			if len(list_craft_items) == 0 :
				await inter.edit_original_response(
					embed=embed,
					components=[
						# КП-18 Тайфун ---> КП-18#Тайфун - запихиваем в кнопку для удобной работы =)
						disnake.ui.Button(label="🆙Апы", style=disnake.ButtonStyle.green, custom_id=f"ups {name.replace(' ', '#')}"),
						disnake.ui.Button(label="📏ТТХ", style=disnake.ButtonStyle.green, custom_id=f"options {name.replace(' ', '#')}"),
						disnake.ui.Button(label="🍪Значки", style=disnake.ButtonStyle.blurple, custom_id=f"badges {name.replace(' ', '#')}"),
						disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
						disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
					]
				)
			elif len(list_craft_items) == 1:
				await inter.edit_original_response(
					embed=embed,
					components=[
						disnake.ui.Button(label="🆙Апы", style=disnake.ButtonStyle.green, custom_id=f"ups {name.replace(' ', '#')}"),
						disnake.ui.Button(label="📏ТТХ", style=disnake.ButtonStyle.green, custom_id=f"options {name.replace(' ', '#')}"),
						disnake.ui.Button(label=f"🔽Крафт: {list_craft_items[0]}", style=disnake.ButtonStyle.green, custom_id=f"market {list_craft_items[0].replace(' ', '#')}@{name.replace(' ', '#')}"),

						disnake.ui.Button(label="🍪Значки", style=disnake.ButtonStyle.blurple, custom_id=f"badges {name.replace(' ', '#')}"),
						disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
						disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
					]
				)
			elif len(list_craft_items) == 2:
				await inter.edit_original_response(
					embed=embed,
					components=[
						disnake.ui.Button(label="🆙Апы", style=disnake.ButtonStyle.green, custom_id=f"ups {name.replace(' ', '#')}"),
						disnake.ui.Button(label="📏ТТХ", style=disnake.ButtonStyle.green, custom_id=f"options {name.replace(' ', '#')}"),
						disnake.ui.Button(label=f"🔽Крафт: {list_craft_items[0]}", style=disnake.ButtonStyle.green, custom_id=f"market {list_craft_items[0].replace(' ', '#')}@{name.replace(' ', '#')}"),
						disnake.ui.Button(label=f"🔽Крафт: {list_craft_items[1]}", style=disnake.ButtonStyle.green, custom_id=f"market {list_craft_items[1].replace(' ', '#')}@{name.replace(' ', '#')}"),

						disnake.ui.Button(label="🍪Значки", style=disnake.ButtonStyle.blurple, custom_id=f"badges {name.replace(' ', '#')}"),
						disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
						disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
					]
				)
			elif len(list_craft_items) == 3:
				await inter.edit_original_response(
					embed=embed,
					components=[
						disnake.ui.Button(label="🆙Апы", style=disnake.ButtonStyle.green, custom_id=f"ups {name.replace(' ', '#')}"),
						disnake.ui.Button(label="📏ТТХ", style=disnake.ButtonStyle.green, custom_id=f"options {name.replace(' ', '#')}"),
						disnake.ui.Button(label=f"🔽Крафт: {list_craft_items[0]}", style=disnake.ButtonStyle.green, custom_id=f"market {list_craft_items[0].replace(' ', '#')}@{name.replace(' ', '#')}"),
						disnake.ui.Button(label=f"🔽Крафт: {list_craft_items[1]}", style=disnake.ButtonStyle.green, custom_id=f"market {list_craft_items[1].replace(' ', '#')}@{name.replace(' ', '#')}"),
						disnake.ui.Button(label=f"🔽Крафт: {list_craft_items[2]}", style=disnake.ButtonStyle.green, custom_id=f"market {list_craft_items[2].replace(' ', '#')}@{name.replace(' ', '#')}"),

						disnake.ui.Button(label="🍪Значки", style=disnake.ButtonStyle.blurple, custom_id=f"badges {name.replace(' ', '#')}"),
						disnake.ui.Button(label="👉Наш сервер", style=disnake.ButtonStyle.link, url='https://discord.gg/H6Ep8AeSDs'),
						disnake.ui.Button(label="Репорт✉️", style=disnake.ButtonStyle.danger, custom_id="report"),
					]
				)

	if random.randint(1,3) == 1: #вер-ть рекламы 33%
		await inter.followup.send(AD_message) #отправляет второй ответ (рекламу)

#####################################################################################################
@client.slash_command(description='Список декора для разбора на ресурсы.')
@commands.guild_only()
async def разбор_декора(inter):
	await inter.response.defer() # БОТ ДУМАЕТ ...
	print(f'[Разбор_декора] {inter.author}')
	sorted_items = await CrossDBot.Salvager(session)

	#ИСКЛЮЧЕНИЕ, ЕСЛИ НЕ УДАЛОСЬ НАЙТИ
	if sorted_items == -1:
		embed = disnake.Embed(
			title='Ошибка.',
			description='(Повторите попытку позже).',
			color=0xFF00FF)
	else:
		embed = disnake.Embed(
			title='Выгода разбора декора',
			description=str('Цена декора / цена ресурсов / выгода'),
			color=0x6A5ACD)

		setAuthor(embed)
		embed.set_thumbnail("https://media.discordapp.net/attachments/1060658288523477032/1089814946809905292/razbor_dekora.gif")

		######## ОСНОВНОЙ БЛОК ########
		info = ''
		for i in sorted_items:
			info += f"● **{i[0]}**:\n ㅤㅤ{i[1]} / {i[2]} — **{i[3]}** :coin: \n"

		# резы
		embed.add_field(
			name='__Результаты по убыванию:__ \n',
			value=info,
			inline=False
		)
	await inter.edit_original_response(embed=embed)

	if random.randint(1,3) == 1: #вер-ть рекламы 33%
		await inter.followup.send(AD_message) #отправляет второй ответ (рекламу)
#####################################################################################################



#ОТПРАВИТЬ РЕПОРТ 
@client.slash_command(description='Отправить сообщение об ошибке разработчику')
async def репорт(inter: disnake.AppCmdInter):
	#СОЗДАНИЕ МОДАЛЬНОГО ОКНА РЕПОРТА 
	await inter.response.send_modal(modal=MyModal())


def setColor(rarity):
	# ВЫБОР ЦВЕТА ОТ РЕДКОСТИ ПРЕДМЕТА:
	_color = 0x000000
	if rarity == 'Common': _color = 0xFFFFFF
	elif rarity == 'Rare': _color = 0x1E90FF
	elif rarity == 'Special': _color = 0x00FFFF
	elif rarity == 'Epic': _color = 0x8A2BE2
	elif rarity == 'Legendary': _color = 0xFF8C00
	elif rarity == 'Relic': _color = 0xFF4500
	return (_color)

def setAuthor(embed):
	# устанавливает верхний и нижний колонтитул (ссылка на бота и авторство - я)
	embed.set_author(
			url='https://discord.com/api/oauth2/authorize?client_id=1051367559481544707&permissions=2148059136&scope=applications.commands%20bot',
			name='[ Добавить бота на свой сервер ]',
			icon_url=LOGOTYPE
			)
	embed.set_footer(  # колонтитул
		text=f"[ Разработчик: RomanUnreal#1221 ]",
		icon_url='https://sun9-49.userapi.com/impg/5Ad2sYkcoOWt-z01YdHBqVamaWCbyXpnW-v1rw/UCmp4DvQtgU.jpg?size=1024x1024&quality=95&sign=97410f34069d852a13833f6303dd0ebe&type=album'
		)



#ОТСЛЕЖИВАНИЕ НАЖАТИЙ КНОПОК
@client.listen("on_button_click")
async def help_listener(inter: disnake.MessageInteraction):
	#ЕСЛИ ЭТО СТОРОННИЙ ВЫЗОВ, РЕТЁРНЕМ ::: [0] - command ::: [1] - item name#format
	if inter.component.custom_id.split()[0] not in ['report', 'market', 'options', 'ups', 'badges']:
		return
	#НАЖАЛИ НА КНОПКУ РЕПОРТА ВЕРНУЛИ СЛЕШ КОМАНДУ /РЕПОРТ
	#print(inter.component.custom_id.split())

	if inter.component.custom_id == "report":
		await client.get_slash_command('репорт').callback(inter)
	elif inter.component.custom_id.split()[0] == "market": # КП-18#Тайфун ---> КП-18 Тайфун
		await client.get_slash_command('р').callback(inter, inter.component.custom_id.split()[1].replace('#', ' '))
	elif inter.component.custom_id.split()[0] == "options":
		await client.get_slash_command('ттх').callback(inter, inter.component.custom_id.split()[1].replace('#', ' '))
	elif inter.component.custom_id.split()[0] == "ups":
		await client.get_slash_command('ап').callback(inter, inter.component.custom_id.split()[1].replace('#', ' '))
	elif inter.component.custom_id.split()[0] == "badges":
		await client.get_slash_command('значки').callback(inter, inter.component.custom_id.split()[1].replace('#', ' '))


# СОЗДАНИЕ МОДАЛЬНОГО ОКНА (Embed) ДЛЯ ОТПРАВКИ РЕПОРТА 
class MyModal(disnake.ui.Modal):
	def __init__(self):
		# The details of the modal, and its components
		components = [
			disnake.ui.TextInput(
				label="Тема репорта",
				placeholder="Введите тему",
				custom_id="name",
				style=TextInputStyle.short,
				max_length=40,
			),
			disnake.ui.TextInput(
				label="Описание репорта",
				placeholder="Опишите вашу проблему связанную с работой бота.",
				custom_id="description",
				style=TextInputStyle.paragraph,
			),
		]
		super().__init__(
			title="Создание репорта",
			custom_id="create_tag",
			components=components,
		)

	# The callback received when the user input is completed.
	# Сборка ембеда из введённой юзером инфы:
	async def callback(self, inter: disnake.ModalInteraction):
		embed = disnake.Embed(
			title="Ваш репорт",
			color=0x00FF00
		)

		for key, value in inter.text_values.items():
			embed.add_field(
				name=key.capitalize(),
				value=value[:1024],
				inline=False
			)

		embed.set_author(
			url='https://discord.gg/UGdSdAwt4G',
			name='[Отправлено на сервер Crossout Bot]',
			icon_url=LOGOTYPE
			)

		embed.set_footer(
			text=inter.author,
			icon_url=inter.author.avatar
		)
		await inter.response.send_message(embed=embed)

		# мой канал на сервере бота для репортов
		await client.get_channel(1053643503030239232).send(embed=embed)
		await inter.send('Ваш репорт отправлен на сервер https://discord.gg/UGdSdAwt4G')



# запуск
client.run(os.environ['TOKEN'], reconnect=True)
