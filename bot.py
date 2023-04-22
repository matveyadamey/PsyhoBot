import telebot
import config
import diagramGenerator

import openai


# достаем телеграм токен
c = config.Config()
token = c.put("TELEGRAM_TOKEN")
openai.api_key = c.put("openai_token")
bot = telebot.TeleBot(token)


global currentQuestion #текущий вопрос
global user_ans # хранит список всех ответов пользователя
global finished #завершен тест или нет
finished = False
global back_q
back_q = False
gate = [0, 6] # варианты ответов


#global gpt_running
#gpt_running = False


# достаем вопросы
file = open("questions/reisas", "r", encoding="UTF8")
r = file.read()
t = r.split("\n")



@bot.message_handler(commands=["start"])
def start(message):
    global currentQuestion
    global finished
    currentQuestion = 0
    finished = False
    #global gpt_running
    #gpt_running = False

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
    c.push(str(message.chat.id), [currentQuestion + 1, [],finished])


@bot.message_handler(commands=["info"])
def info(message):
    global currentQuestion
    currentQuestion = c.put(str(message.chat.id))[0]
    bot.send_message(
        message.chat.id,
        f"Списк команд:\n"
        f"/start - запустить/перезапустить бота\n"
        f"/info - открыть список команд\n"
        f"/back - вернуться к предыдущему вопросу"
    )
    bot.send_message(message.chat.id, t[currentQuestion])


# возвращаемся к вопросу
@bot.message_handler(commands=['back'])
def back(message):
    global user_ans
    global currentQuestion
    global finished
    global back_q
    currentQuestion = c.put(str(message.chat.id))[0]
    user_ans = c.put(str(message.chat.id))[1]
    if currentQuestion == 0:
        bot.send_message(
            message.chat.id,
            f"Не выёживайся!"
        )
        bot.send_message(message.chat.id, t[currentQuestion])
        return
    bot.send_message(
        message.chat.id,
        f"Введите номер вопроса, к которому хотите вернуться"
    )
    back_q = True


# принимаем ответ
@bot.message_handler(content_types=["text"])
def lalal(message):
    global user_ans
    global currentQuestion
    global finished
    global back_q

    print(str(message.chat.id),message.text)



    if back_q:
        if message.text.isdigit():
            text = int(message.text)
            # если да, тогда смотрим входит ли он в диапозон от 0 до 6
            if 1 <= text < currentQuestion:
                currentQuestion = text - 1
                c.push(str(message.chat.id), [currentQuestion, user_ans, finished])
                user_ans = user_ans[:currentQuestion]
                back_q = False
                bot.send_message(message.chat.id, t[currentQuestion])
                return
            else:
                bot.send_message(
                    message.chat.id,
                    f"Введите число в диапазоне от 1 до {currentQuestion - 1}"
                )
                return
        else:
            bot.send_message(message.chat.id, "Я не могу понять твой ответ :(")
            return

    if c.put(str(message.chat.id))[2]: #если тест уже завершен
        bot.send_message(
            message.chat.id,
            f"Кажется, Вы уже прошли тестирование. Для повторного прохождения введите /start"
        )
        return
    currentQuestion = c.put(str(message.chat.id))[0]
    user_ans = c.put(str(message.chat.id))[1]
    # если не все вопросы заданы
    # проверяем является ли ответ числом
    if message.text.isdigit():
        text = int(message.text)
        # если да, тогда смотрим входит ли он в диапозон от 0 до 6
        if gate[0] <= text <= gate[1]:
            # увеличиваем результат и счетчик вопросов
            user_ans.append(text)
            c.push(str(message.chat.id), [currentQuestion+1, user_ans,finished])
            if currentQuestion <= len(t) - 1:
                bot.send_message(message.chat.id, t[currentQuestion])
        # если не входит повторяем текущий вопрос
        else:
            bot.send_message(message.chat.id, f"шкала от {gate[0]} до {gate[1]}")
            bot.send_message(message.chat.id, t[currentQuestion-1])
    else:
        # если ответ не является числом, говорим об этом юзеру
        bot.send_message(message.chat.id, "Я не могу понять твой ответ :(")
        bot.send_message(message.chat.id, t[currentQuestion-1])

    if currentQuestion == len(t):
        # когда вопросы закончились, генерируем диаграмму и отправляем юзеру
        max_val = len(t) * gate[1]
        diagramGenerator.Diagram().bebra([sum(user_ans), max_val - sum(user_ans)])
        photo = open("bebra.png", "rb")
        bot.send_photo(message.chat.id, photo)
        if sum(user_ans) < max_val / 3:
            bot.send_message(
                message.chat.id,
                f"Небольшой совет: вы сможете достичь больших высот, если будете вести себя увереннее ;)"
            )
        if max_val / 3 <= sum(user_ans) < max_val / 3 * 2:
            bot.send_message(
                message.chat.id,
                "Вы превосходно сбалансированы в вопросе своей уверенности, нам даже нечего рекомендовать ;)"
            )
        if max_val / 3 * 2 <= sum(user_ans):
            bot.send_message(
                message.chat.id,
                f"Вы крайне уверены в себе, Вам может это показаться приятным, но, к сожалению, "
                f"иногда Ваше поведение может быть агрессивным и вызывать раздражение у окружающих. "
                f"Выводы можете делать сами ;)"
            )

        # обнуляем текущий вопрос и удаляем тест из списка ожидающих прохождение
        c.push(str(message.chat.id), [0, 0,[],True])


bot.polling(none_stop=True)
