import threading
def web():#定义网页服务
    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def index():
        return f'请在这里改自己的网页服务以用于KOOK图片的上传↓↓（需要有公网ip或者内网穿透）'

    app.run(debug=False, host='0.0.0.0', port=12138)

from khl import Bot, Message, EventTypes, Event
from khl.card import CardMessage, Card, Module, Element, Types
import random,os
from PIL import Image, ImageDraw, ImageFont

import pandas as pd #读取词典数据
words=pd.read_csv('words.csv',encoding='GBK')

import logging #输出日志
logging.basicConfig(level='INFO')

whetherstart=False #变量：是否启动游戏
choice=[] #变量：选择的单词和意思
cnt=-1 #变量：猜词的次数
imgrand=0 #变量：防止KOOK不多次加载图片

def creatgameimg(): #创建游戏空图片
    global imgrand
    imgrand = random.randint(10001, 99999)
    wordleimg=Image.new(mode='RGB', size=[700, 800], color='white') #创建主画面
    title_area=Image.new(mode='RGB', size=[600, 100], color='white') #创建标题区画面
    answer_area=Image.new(mode='RGB', size=[600, 600], color='white') #创建回答区画面
    square = Image.new(mode='RGB', size=[120, 120], color='white') #创建回答区单框
    squared = ImageDraw.Draw(square) #创建单框绘图实例
    squared.rectangle([10,10,110,110], fill=None,outline='black',width=5) #单框绘图
    for i in range(1,601,120):  #合并答题区
        for j in range(1,601,120):
            answer_area.paste(square,[i,j])
    wordleimg.paste(answer_area,[50,150]) #答题区合并于主画面内
    title_aread = ImageDraw.Draw(title_area) #创建标题区绘图实例
    title_aread.text([150,0], text='Wordle', fill='black', font=ImageFont.truetype('fonts/zhankukuaile2016.ttf', 100),align='center') #绘制标题区
    wordleimg.paste(title_area,[50,25]) #标题区合并于主画面内
    wordleimg.save(f'static/wordle-{imgrand}.png')

def start():#启动游戏
    global choice,whetherstart,cnt
    cnt=-1
    whetherstart=True
    number = random.randint(0, len(words))
    word=words.at[number,'words']
    meaning=words.at[number,'meanings']
    choice=[word,meaning]
    creatgameimg()

def whether_msg_is_legal(playerguess):#判断玩家猜词是否符合规范
    if len(playerguess)!=5:
        return False
    for i in playerguess:
        if (not 'a'<=i<='z') and (not 'A'<=i<='Z'):
            return False
    return True

def rightletter(place):#该字母正确
    global cnt,choice,imgrand
    gameimg = Image.open(f'static/wordle-{imgrand}.png')  # 打开文件
    gameimgd = ImageDraw.Draw(gameimg)  # 创建绘图实例
    startx, starty = 66 + place * 120, 166 + cnt * 120  # 填充开始位置
    endx, endy = 156 + place * 120, 256 + cnt * 120  # 填充结束位置
    textx,texty=85+place*120,160+cnt*120 #文字开始位置
    gameimgd.rectangle([startx, starty, endx, endy], fill='#00c91e', outline=None, width=0)  # 颜色填充
    gameimgd.text([textx, texty], text=choice[0][place].upper(), fill='#eeeeee',font=ImageFont.truetype('fonts/ElmerFont.ttf', 100), align='left')  # 文字填充
    gameimg.save(f'static/wordle-{imgrand}.png')

def rightletter_wrongplace(place,playerguess):
    global cnt, choice, imgrand
    gameimg = Image.open(f'static/wordle-{imgrand}.png')  # 打开文件
    gameimgd = ImageDraw.Draw(gameimg)  # 创建绘图实例
    startx, starty = 66 + place * 120, 166 + cnt * 120  # 填充开始位置
    endx, endy = 156 + place * 120, 256 + cnt * 120  # 填充结束位置
    textx, texty = 85 + place * 120, 160 + cnt * 120  # 文字开始位置
    gameimgd.rectangle([startx, starty, endx, endy], fill='#323232', outline=None, width=0)  # 颜色填充
    gameimgd.text([textx, texty], text=playerguess[place].upper(), fill='#eeeeee',font=ImageFont.truetype('fonts/ElmerFont.ttf', 100), align='left')  # 文字填充
    gameimg.save(f'static/wordle-{imgrand}.png')

def wrongletter(place,playerguess):
    global cnt, choice, imgrand
    gameimg = Image.open(f'static/wordle-{imgrand}.png')  # 打开文件
    gameimgd = ImageDraw.Draw(gameimg)  # 创建绘图实例
    startx, starty = 66 + place * 120, 166 + cnt * 120  # 填充开始位置
    endx, endy = 156 + place * 120, 256 + cnt * 120  # 填充结束位置
    textx, texty = 85 + place * 120, 160 + cnt * 120  # 文字开始位置
    gameimgd.rectangle([startx, starty, endx, endy], fill='#c90000', outline=None, width=0)  # 颜色填充
    gameimgd.text([textx, texty], text=playerguess[place].upper(), fill='#eeeeee',font=ImageFont.truetype('fonts/ElmerFont.ttf', 100), align='left')  # 文字填充
    gameimg.save(f'static/wordle-{imgrand}.png')

def del_files(dir_path):
    if os.path.isfile(dir_path):
        try:
            os.remove(dir_path) # 这个可以删除单个文件，不能删除文件夹
        except BaseException as e:
            print(e)
    elif os.path.isdir(dir_path):
        file_lis = os.listdir(dir_path)
        for file_name in file_lis:
            # if file_name != 'wibot.log':
            tf = os.path.join(dir_path, file_name)
            del_files(tf)
    print(f'已删除 {dir_path}')

bot = Bot(token='请在这里替换你机器人的秘钥')#设置机器人秘钥

@bot.command(name='wordle')#主命令执行
async def maincommand(msg: Message):
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    if not whetherstart :
        start()
        cm = CardMessage(Card(
                Module.Header('游戏已开始，快来猜词吧！'),
                Module.ImageGroup(
                    Element.Image(f"http://请将这里替换为你对外开放的ip（用于图片的上传，共五处）/static/wordle-{imgrand}.png")
                )
            ))
        await msg.ctx.channel.send(cm)
    else:
        cm = CardMessage(Card(
            Module.Header('游戏已开始，快来猜词吧！'),
            Module.ImageGroup(
                Element.Image(f"http://请将这里替换为你对外开放的ip（用于图片的上传，共五处）/static/wordle-{imgrand}.png")
            )
        ))
        await msg.ctx.channel.send(cm)

@bot.command(name='guess')#玩家猜词
async def guess(msg: Message,playerguess:str):
    global imgrand,cnt,whetherstart
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    print(f'{msg.author.nickname} 猜词： {playerguess}')
    if not whetherstart: #若游戏未开始，则强制开始游戏
        start()
    if not whether_msg_is_legal(playerguess): #若不符合规范，则返回
        cm = CardMessage(Card(
            Module.Header('游戏已开始，快来猜词吧！'),
            Module.ImageGroup(
                Element.Image(f"http://请将这里替换为你对外开放的ip（用于图片的上传，共五处）/static/wordle-{imgrand}.png")
            )
        ))
        await msg.ctx.channel.send(cm)
        await msg.reply('您的输入错误，请输入五个字母的英文单词')
    else: #符合规范，继续判断
        cnt+=1
        right=0
        playerguess=playerguess.lower()
        for i in range(0,5):
            if playerguess[i]==choice[0][i]:
                rightletter(i)
                right+=1
            elif playerguess[i] in choice[0]:
                rightletter_wrongplace(i,playerguess)
            else:
                wrongletter(i, playerguess)
        gameimg = Image.open(f'static/wordle-{imgrand}.png')
        imgrand = random.randint(10001, 99999)
        gameimg.save(f'static/wordle-{imgrand}.png')
        cm = CardMessage(Card(
            Module.Header(playerguess.upper()),
            Module.ImageGroup(
                Element.Image(f"http://请将这里替换为你对外开放的ip（用于图片的上传，共五处）/static/wordle-{imgrand}.png")
            )
        ))
        await msg.ctx.channel.send(cm)
        if right==5:
            await msg.ctx.channel.send(f'恭喜(met){msg.author_id}(met) 猜对单词： {choice[0]}，单词释义：{choice[1]}')
            whetherstart=False
            del_files('static')
        elif cnt==4:
            await msg.ctx.channel.send(f'很遗憾没有猜对单词。本轮单词为： {choice[0]}，单词释义：{choice[1]}')
            whetherstart = False
            del_files('static')

@bot.command(name='restartwordle')#重启游戏
async def restartwordle(msg: Message):
    global imgrand,cnt,whetherstart
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    start()
    cm = CardMessage(Card(
        Module.Header('游戏已开始，快来猜词吧！'),
        Module.ImageGroup(
            Element.Image(f"http://请将这里替换为你对外开放的ip（用于图片的上传，共五处）/static/wordle-{imgrand}.png")
        )
    ))
    await msg.ctx.channel.send(cm)

@bot.command(name='cleancache')#清除缓存
async def cleancache(msg: Message):
    global whetherstart
    whetherstart=False
    del_files('static')
    await msg.reply('删除成功')

webstart = threading.Thread(name='webstarts',target= web)#启动网页服务
webstart.start()
bot.run()#启动机器人
