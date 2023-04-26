import telebot
import config
import diagramGenerator

import openai


# достаем телеграм токен
c = config.Config()
token = c.put("TELEGRAM_TOKEN")
openai.api_key = c.put("openai_token")
bot = telebot.TeleBot(token)

gate = [0, 6]   # варианты ответов


# global gpt_running
# gpt_running = False


# достаем вопросы
file = open("questions/reisas", "r", encoding="UTF8")
r = file.read()
t = r.split("\n")



@bot.message_handler(commands=["start"])
def start(message):
    global finished
    currentQuestion = 0
    finished = False
    global back_q
    back_q=False
    # global gpt_running
    # gpt_running = False

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
        f"а \"{gate[1]}\" - что ты полностью согласен с вышеуказанным"
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
        resSum=reisastestSum()
        # генерация и отправка диаграммы
        diagramGenerator.Diagram().bebra(resSum,max_val - resSum)
        photo = open("bebra.png", "rb")
        bot.send_photo(message.chat.id, photo)

        # отправлялка советов

        if 0<=resSum<=24:
            bot.send_message(
                message.chat.id,
                "очень неуверен в себе"
            )
        if 25 <= resSum <=48 :
            bot.send_message(
                message.chat.id,
                "скорее не уверен, чем уверен"
            )
        if 49 <= resSum <=72:
            bot.send_message(
                message.chat.id,"среднее значение уверенности")
        if 73 <= resSum <= 96:
            bot.send_message(
                message.chat.id, "уверен в себе")
        if 97 <= resSum <=120:
            bot.send_message(
                message.chat.id,"слишком самоуверен")

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
            print(currentQuestion)
            if not back_q:
                while len(user_ans) < currentQuestion:
                    user_ans.append(0)
                user_ans[currentQuestion - 1] = text
                c.push(str(message.chat.id),[currentQuestion,user_ans,finished,back_q])
                # bot.send_message(message.chat.id, str(sum(user_ans)))
                print(sum(user_ans))
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
    finished=False
    if back_q:
        if message.text.isdigit():
            text = int(message.text)
            if 1 <= text <= currentQuestion:
                currentQuestion = text - 2
                user_ans = user_ans[:currentQuestion]
                # bot.send_message(message.chat.id, t[currentQuestion - 1])
                back_q = False
                c.push(str(message.chat.id), [currentQuestion, user_ans, finished, back_q])
                next_query(message)
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
