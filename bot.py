import telebot
import config
import diagramGenerator


#достаем телеграм токен
c = config.Config()
token = c.put("TELEGRAM_TOKEN")
bot=telebot.TeleBot(token)

#инициализируем текущий вопрос и результат теста
global currentQuestion
global ISum
currentQuestion = 0
ISum = 0

#достаем вопросы
file=open("questions/reisas","r",encoding="UTF8")
r=file.read()
t=r.split("\n")

@bot.message_handler(commands=["start"])
def start(message):
    global currentQuestion
    #get username
    global username
    username=str(message.chat.id)
    c.push(username,[currentQuestion,ISum])

    bot.send_message(message.chat.id,"Привет! Я бот-психолог, я хочу помочь тебе решить все твои проблемы и разобраться в себе.")
    bot.send_message(message.chat.id,"Для начала пройди небольшой тест."
                                     "На все вопросы выводите число от 0 до 6, где 0 означает, что изложенная позиция Вам совершенно не подходит,а 6 что Вы полностью согласны с вышеуказанным")

    #отправляем текущий вопрос
    bot.send_message(message.chat.id,t[c.put(str(message.chat.id))[0]])


#принимаем ответ
@bot.message_handler(content_types=["text"])
def lalal(message):
    global ISum
    global currentQuestion

    #если не все вопросы заданы
    if(c.put(str(message.chat.id))[0]<=len(t)-2):
        #проверяем является ли ответ числом
        try:
            text=int(message.text)
            if (text):
                    #если да, тогда смотрим входит ли он в диапозон от 0 до 6
                    if (0<=text<= 6):
                        #увеличиваем результат и счетчик вопросов
                        print(c.put(str(message.chat.id))[0],c.put(str(message.chat.id))[1])
                        c.push(str(message.chat.id),[c.put(str(message.chat.id))[0],c.put(str(message.chat.id))[1]+text])
                        print(c.put(str(message.chat.id))[0], c.put(str(message.chat.id))[1])
                        c.push(str(message.chat.id),[c.put(str(message.chat.id))[0]+1,c.put(str(message.chat.id))[1]])
                        bot.send_message(message.chat.id, t[c.put(str(message.chat.id))[0]])
                    #если не входит повторяем текущий вопрос
            else:
                        bot.send_message(message.chat.id, "шкала от 0 до 6")
                        bot.send_message(message.chat.id, t[c.put(str(message.chat.id)[0])])

        except:
            #если ответ не является числом, говорим об этом юзеру
            bot.send_message(message.chat.id, "Я тебя не понимаю")
            bot.send_message(message.chat.id, t[c.put(str(message.chat.id))[0]])


    else:
        #когда вопросы закончились, генерируем диаграмму и отправляем юзеру
        diagramGenerator.Diagram().bebra([ISum, 100 - ISum])
        photo=open("bebra.png","rb")
        bot.send_photo(message.chat.id,photo)
        bot.send_message(message.chat.id,"Совет: если вы будете увереннее в себе, то сможете достичь большего")

        #обнуляем текущий вопрос и удаляем тест из списка ожидающих прохождение
        c.push(str(message.chat.id),[0,0])

bot.polling(none_stop=True)