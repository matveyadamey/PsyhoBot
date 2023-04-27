import telebot
from telebot import types
import config
import diagramGenerator
import chatGPT


# достаем телеграм токен
c = config.Config()
chat_gpt=chatGPT.ChatGPT()
token = c.put("TELEGRAM_TOKEN")
bot = telebot.TeleBot(token)

gate = [0, 6]   # варианты ответов



# достаем вопросы
file = open("questions/reisas", "r", encoding="UTF8")
r = file.read()
t = r.split("\n")


@bot.message_handler(commands=["start"])
def start(message):
    global finished
    currentQuestion = 0
    finished = False
    back_q=False

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("0")
    btn2 = types.KeyboardButton("1")
    btn3 = types.KeyboardButton("2")
    btn4 = types.KeyboardButton("3")
    btn5 = types.KeyboardButton("4")
    btn6 = types.KeyboardButton("5")
    btn7 = types.KeyboardButton("6")
    btn8 = types.KeyboardButton("/back")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)

    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! "
        f"Я бот-психолог, моя цель - помочь тебе определить проблемы и дать совет по их устранению :)\n"
        f"Чтобы наше взаимодействие было как можно более эффективным, Вы можете познакомиться "
        f"со списком команд. Для этого введите /info"
    )
    bot.send_message(
        message.chat.id,
        f"Но а мы переходим к небольшому тесту.\n"
        f"На все вопросы отвечай числом от {gate[0]} до {gate[1]}, где \"{gate[0]}\" означает, "
        f"что изложенная позиция тебе совершенно не подходит, "
        f"а \"{gate[1]}\" - что ты полностью согласен с вышеуказанным", reply_markup=markup
    )

    # отправляем текущий вопрос
    bot.send_message(message.chat.id, t[0])
    c.push(str(message.chat.id),[currentQuestion,[],finished,back_q])


@bot.message_handler(commands=["info"])
def info(message):
    currentQuestion = c.put(str(message.chat.id))[0]
    bot.send_message(
        message.chat.id,
        f"Список команд:\n"
        f"/start - запустить/перезапустить бота\n"
        f"/info - открыть список команд\n"
        f"/back - вернуться к предыдущему вопросу"
    )
    bot.send_message(message.chat.id, t[currentQuestion])


# возвращаемся к вопросу
@bot.message_handler(commands=['back'])
def back(message):
    currentQuestion = c.put(str(message.chat.id))[0]
    user_ans=c.put(str(message.chat.id))[1]
    finished=c.put(str(message.chat.id))[2]
    if currentQuestion == 0:
        bot.send_message(
            message.chat.id,
            f"Не выёживайся!"
        )
        # currentQuestion -= 1
        bot.send_message(message.chat.id, t[currentQuestion])
        return
    bot.send_message(
        message.chat.id,
        f"Введите номер вопроса, к которому хотите вернуться"
    )
    back_q=True
    c.push(str(message.chat.id),[currentQuestion,user_ans,finished,back_q])




def reisastestSum(message):
    u = c.put(str(message.chat.id))[1]
    first=u[2]+u[5]+u[6]+u[7]+u[9]+u[17]+u[19]+u[20]+u[21]+u[24]+u[26]+u[27]+u[28]
    second=u[0]+u[1]+u[3]+u[4]+u[8]+u[10]+u[11]+u[12]+u[13]+u[14]+u[15]+u[16]+u[18]+u[22]+u[23]+u[25]+u[29]
    resSum=first+72-second
    return resSum


def finish_test(message):
        max_val = len(t) * gate[1]
        resSum=reisastestSum(message)
        # генерация и отправка диаграммы
        diagramGenerator.Diagram().bebra([resSum, max_val - resSum])
        photo = open("bebra.png", "rb")
        bot.send_photo(message.chat.id, photo)

        # отправлялка советов

        if 0<=resSum<=24:
            #очень неуверен в себе
            bot.send_message(message.chat.id,str(chat_gpt.ask("Что делать если ты очень неуверен в себе?")))

        if 25 <= resSum <=48 :
            #скорее не уверен, чем уверен
            bot.send_message(message.chat.id, chat_gpt.ask("Что делать если ты скорее не уверен, чем уверен в себе?"))

        if 49 <= resSum <=72:
            #среднее значение уверенности
            bot.send_message(message.chat.id, chat_gpt.ask("Что делать если среднее значение уверенности в себе?"))
        if 73 <= resSum <= 96:
            "уверен в себе"
            bot.send_message(message.chat.id, chat_gpt.ask("Что делать если ты уверен в себе?"))

        if 97 <= resSum <=120:
            "слишком самоуверен"
            bot.send_message(message.chat.id, chat_gpt.ask("Что делать если ты слишком самоуверен в себе?"))

        # обнуляем текущий вопрос и удаляем тест из списка ожидающих прохождение
        currentQuestion=0
        user_ans=[]
        finished=True
        back_q=False
        c.push(str(message.chat.id),[currentQuestion,user_ans,finished,back_q])


def next_query(message):
    finished=False
    currentQuestion = c.put(str(message.chat.id))[0] + 1
    user_ans = c.put(str(message.chat.id))[1]
    back_q=c.put(str(message.chat.id))[3]
    if back_q:
        bot.send_message(message.chat.id, t[currentQuestion - 1])
        return

    # проверяем является ли ответ числом
    if message.text.isdigit():
        text = int(message.text)
        # если да, тогда смотрим входит ли он в диапозон от 0 до 6
        if gate[0] <= text <= gate[1]:
            # увеличиваем результат и счетчик вопросов
            # print(currentQuestion)
            if not back_q:
                while len(user_ans) <= currentQuestion:
                    user_ans.append(0)
                user_ans[currentQuestion] = text
                c.push(str(message.chat.id),[currentQuestion,user_ans,finished,back_q])
                # bot.send_message(message.chat.id, str(sum(user_ans)))
                # print(sum(user_ans))
            if currentQuestion < len(t):
                bot.send_message(message.chat.id, t[currentQuestion])
            else:
                finish_test(message)
        # если не входит повторяем текущий вопрос
        else:
            bot.send_message(message.chat.id, f"шкала от {gate[0]} до {gate[1]}")
            bot.send_message(message.chat.id, t[currentQuestion - 1])
            currentQuestion-=1
            c.push(str(message.chat.id),[currentQuestion,user_ans,finished,back_q])
    else:
        # если ответ не является числом, говорим об этом юзеру
        bot.send_message(message.chat.id, "Я не могу понять твой ответ :(")
        currentQuestion -= 1
        bot.send_message(message.chat.id, t[currentQuestion])
        c.push(str(message.chat.id),[currentQuestion,user_ans,finished,back_q])


# принимаем ответ
@bot.message_handler(content_types=["text"])
def lalal(message):
    currentQuestion = c.put(str(message.chat.id))[0]
    user_ans = c.put(str(message.chat.id))[1]
    back_q=c.put(str(message.chat.id))[3]
    print(back_q)
    finished=False
    if back_q:
        if message.text.isdigit():
            text = int(message.text)
            if 1 <= text <= currentQuestion:
                currentQuestion = text - 1
                user_ans = user_ans[:currentQuestion]
                # bot.send_message(message.chat.id, t[currentQuestion - 1])
                c.push(str(message.chat.id), [currentQuestion, user_ans, finished, back_q])
                next_query(message)
                currentQuestion = c.put(str(message.chat.id))[0]
                user_ans = c.put(str(message.chat.id))[1]
                c.push(str(message.chat.id), [currentQuestion, user_ans, finished, False])
                return
            else:
                bot.send_message(
                    message.chat.id,
                    f"Введите число в диапазоне от 1 до {currentQuestion}"
                )
                return
        else:
            bot.send_message(message.chat.id, "Я не могу понять твой ответ :(")
            return

    if c.put(str(message.chat.id))[2]:  # если этот тест уже пройден
        bot.send_message(
            message.chat.id,
            f"Кажется, Вы уже прошли тестирование. Для повторного прохождения введите /start"
        )
        return

    # когда вопросы закончились
    if currentQuestion == len(t):
        print("я все, дядь")
        finish_test(message)
    else:
        # если не все вопросы заданы
        next_query(message)


bot.polling(none_stop=True)

