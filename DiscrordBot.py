import disnake
from disnake.ext import commands
import CrosDBot
from time import sleep
bot = commands.Bot(command_prefix='!', intents=disnake.Intents.all())

# декоратор (события) у функций определнные названия
@bot.event
async def on_ready():
    print(f'Bot {bot.user} is ready to work!')

@bot.event
async def on_message(message):
    if message.content.find('!р') != -1 or message.content.find('!p') != -1:
        text = message.content[3:]
        item_info = CrosDBot.CheckPrice(text) # инфа о предмете dict{}

        # ИСКЛЮЧЕНИЕ, ЕСЛИ НЕ УДАЛОСЬ НАЙТИ ТАКОЙ ПРЕДМЕТ
        if item_info == -1:
            embed = disnake.Embed(
                title='ERROR',
                description='Не удалось найти предмет с таким названием. Повторите попытку.',
                color=disnake.Colour.red()
            )
        else:
            # ВЫБОР ЦВЕТА ОТ РЕДКОСТИ ПРЕДМЕТА:
            _color = 0xFFFF00
            if item_info['rare'] == 'Common': _color = 0xFFFFFF
            if item_info['rare'] == 'Rare': _color = 0x4169E1
            if item_info['rare'] == 'Special': _color = 0x40E0D0
            if item_info['rare'] == 'Epic': _color = 0x8A2BE2
            if item_info['rare'] == 'Legendary': _color = 0xFFD700
            if item_info['rare'] == 'Relic': _color = 0xFF4500

            embed = disnake.Embed(
                title=item_info['name'],
                description=item_info['rare'] + ' ' + item_info['type'],
                color=_color
            )

            embed.set_author(
                name='RomanUnreal #1221',
                icon_url='https://sun9-49.userapi.com/impg/5Ad2sYkcoOWt-z01YdHBqVamaWCbyXpnW-v1rw/UCmp4DvQtgU.jpg?size=1024x1024&quality=95&sign=97410f34069d852a13833f6303dd0ebe&type=album'
            )
            embed.set_footer( # колонтитул
                text='Ранний доступ.',
                icon_url='https://sun9-49.userapi.com/impg/5Ad2sYkcoOWt-z01YdHBqVamaWCbyXpnW-v1rw/UCmp4DvQtgU.jpg?size=1024x1024&quality=95&sign=97410f34069d852a13833f6303dd0ebe&type=album'
            )
            embed.set_image(item_info['image'])
            #embed.set_thumbnail('https://sun9-49.userapi.com/impg/5Ad2sYkcoOWt-z01YdHBqVamaWCbyXpnW-v1rw/UCmp4DvQtgU.jpg?size=1024x1024&quality=95&sign=97410f34069d852a13833f6303dd0ebe&type=album')
            embed.set_thumbnail('https://otkritkis.com/wp-content/uploads/2022/07/mvtgw.gif')

            # ИНФОРМАЦИЯ О ЦЕНАХ:

            embed.add_field(name='Цена покупки: ', value=item_info['buyPrice'], inline=True)
            embed.add_field(name='Цена продажи: ', value=item_info['sellPrice'], inline=True)
            embed.add_field(name='Заказов: ', value=item_info['orders'], inline=True)
            embed.add_field(name='Предложений: ', value=item_info['offers'], inline=True)

        sleep(1)
        await message.channel.send(embed=embed)

bot.run('MTA1MTM2NzU1OTQ4MTU0NDcwNw.Gb_pNP.cq1gRtQSY5kv254TXLgRd_fvpmIvuK7srjk_Fg')