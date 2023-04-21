import telebot
import config
import diagramGenerator

import openai


# достаем телеграм токен
c = config.Config()
token = c.put("TELEGRAM_TOKEN")
bot = telebot.TeleBot(token)

openai.api_key = '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'

# инициализируем текущий вопрос и результат теста
global currentQuestion
global user_ans
currentQuestion = 0
user_ans = []   # замена ISum, хранит список всех ответов пользователя

# варианты ответов
gate = [0, 6]

# достаем вопросы
file = open("questions/reisas", "r", encoding="UTF8")
r = file.read()
t = r.split("\n")

global finished
global gpt_running
finished = False
gpt_running = False

global back_q
back_q = False


@bot.message_handler(commands=["start"])
def start(message):
    global currentQuestion
    # get username
    global username
    global gpt_running
    global finished
    username = str(message.chat.id)

    currentQuestion = 0
    user_ans = []
    gpt_running = False
    finished = False

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
    c.push(username, [currentQuestion + 1, user_ans])


@bot.message_handler(commands=["info"])
def info(message):
    global currentQuestion
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

    if currentQuestion == 0:
        bot.send_message(
            message.chat.id,
            f"Не выёживайся!"
        )
        bot.send_message(message.chat.id, t[currentQuestion])
        return

    currentQuestion = c.put(str(message.chat.id))[0]
    user_ans = c.put(str(message.chat.id))[1]
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

    print(user_ans)
    if back_q:
        try:
            text = int(message.text)
            # если да, тогда смотрим входит ли он в диапозон от 0 до 6
            if 1 <= text < currentQuestion:
                currentQuestion = text - 1
                user_ans = user_ans[:currentQuestion]
                c.push(str(message.chat.id), [currentQuestion, user_ans])
                back_q = False
                bot.send_message(message.chat.id, t[currentQuestion])
                return
            else:
                bot.send_message(
                    message.chat.id,
                    f"Введите число в диапазоне от 1 до {currentQuestion - 1}"
                )
                return
        except:
            bot.send_message(message.chat.id, "Я не могу понять твой ответ :(")
            return

    if finished:
        bot.send_message(
            message.chat.id,
            f"Кажется, Вы уже прошли тестирование. Для повторного прохождения введите /start"
        )
        return
    currentQuestion = c.put(str(message.chat.id))[0]
    user_ans = c.put(str(message.chat.id))[1]
    # если не все вопросы заданы
    # проверяем является ли ответ числом
    try:
        text = int(message.text)
        # если да, тогда смотрим входит ли он в диапозон от 0 до 6
        if gate[0] <= text <= gate[1]:
            # увеличиваем результат и счетчик вопросов
            user_ans.append(text)
            c.push(str(message.chat.id), [currentQuestion, user_ans])
            c.push(str(message.chat.id), [currentQuestion + 1, user_ans])
            if currentQuestion <= len(t) - 1:
                bot.send_message(message.chat.id, t[currentQuestion])
        # если не входит повторяем текущий вопрос
        else:
            bot.send_message(message.chat.id, f"шкала от {gate[0]} до {gate[1]}")
            bot.send_message(message.chat.id, t[currentQuestion-1])
    except:
        # если ответ не является числом, говорим об этом юзеру
        bot.send_message(message.chat.id, "Я не могу понять твой ответ :(")
        bot.send_message(message.chat.id, t[currentQuestion-1])

    if currentQuestion == len(t):
        # когда вопросы закончились, генерируем диаграмму и отправляем юзеру
        max_val = len(t) * gate[1]
        print(sum(user_ans))
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
        finished = True

        # обнуляем текущий вопрос и удаляем тест из списка ожидающих прохождение
        c.push(str(message.chat.id), [0, 0])


bot.polling(none_stop=True)
