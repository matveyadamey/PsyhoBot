import random

import telebot
import config
import decider

c = config.Config()
token = c.put("TELEGRAM_TOKEN")
bot=telebot.TeleBot(token)
decider=decider.Decider()


global currentQuestion
global ISum
currentQuestion = 0
ISum = 0


file=open("questions/reisas","r",encoding="UTF8")
r=file.read()
t=r.split("\n")

@bot.message_handler(commands=["start"])
def start(message):
    global currentQuestion
    bot.send_message(message.chat.id,"Привет! Я бот-психолог, я хочу помочь тебе решить все твои проблемы и разобраться в себе.")
    bot.send_message(message.chat.id,"Для начала пройди небольшой тест."
                                     "На все вопросы выводите число от 0 до 6, где 0 означает, что изложенная позиция Вам совершенно не подходит,а 6 что Вы полностью согласны с вышеуказанным")
    bot.send_message(message.chat.id,t[currentQuestion])
    currentQuestion+=1


@bot.message_handler(content_types=["text"])
def lalal(message):
    global ISum
    global currentQuestion
    if(currentQuestion<=29):
        try:
            text=int(message.text)

        except:
            bot.send_message(message.chat.id, "Я тебя не понимаю")
            bot.send_message(message.chat.id, t[currentQuestion])
        if(text):
            if(text<=6 and text>=0):
                    ISum+=text
                    bot.send_message(message.chat.id, t[currentQuestion])
                    currentQuestion += 1
            else:
                    bot.send_message(message.chat.id, "шкала от 0 до 6")
                    bot.send_message(message.chat.id, t[currentQuestion])

    else:
        decider.decide([ISum, 100 - ISum])
        photo=open("bebra.png","rb")
        bot.send_photo(message.chat.id,photo)
        currentQuestion=0
        bot.send_message(message.chat.id,"Совет: если вы будете увереннее в себе, то сможете достичь большего")

bot.polling(none_stop=True)