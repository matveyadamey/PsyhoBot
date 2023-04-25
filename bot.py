import telebot
import config
import diagramGenerator

import openai


# достаем телеграм токен
c = config.Config()
token = c.put("TELEGRAM_TOKEN")
openai.api_key = c.put("openai_token")
bot = telebot.TeleBot(token)


global finished # завершен тест или нет
finished = False
global back_q
back_q = False
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
    c.push(str(message.chat.id), [currentQuestion, [], finished])


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
    global finished
    global back_q
    currentQuestion = c.put(str(message.chat.id))[0]

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
    back_q = True


def finish_test(message):
        user_ans = c.put(str(message.chat.id))[1]
        max_val = len(t) * gate[1]

        # генерация и отправка диаграммы
        diagramGenerator.Diagram().bebra([sum(user_ans), max_val - sum(user_ans)])
        photo = open("bebra.png", "rb")
        bot.send_photo(message.chat.id, photo)

        # отправлялка советов

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
        c.push(str(message.chat.id), [0, 0, [], True])


def next_query(message):
    global back_q
    currentQuestion = c.put(str(message.chat.id))[0] + 1
    user_ans = c.put(str(message.chat.id))[1]

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
                c.push(str(message.chat.id), [currentQuestion, user_ans, finished])
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
            c.push(str(message.chat.id), [currentQuestion - 1, user_ans, finished])
    else:
        # если ответ не является числом, говорим об этом юзеру
        bot.send_message(message.chat.id, "Я не могу понять твой ответ :(")
        bot.send_message(message.chat.id, t[currentQuestion - 1])
        c.push(str(message.chat.id), [currentQuestion - 1, user_ans, finished])


# принимаем ответ
@bot.message_handler(content_types=["text"])
def lalal(message):
    global finished
    global back_q
    currentQuestion = c.put(str(message.chat.id))[0]
    user_ans = c.put(str(message.chat.id))[1]
    print(str(message.chat.id), message.text, currentQuestion, back_q)
    print(user_ans)

    if back_q:
        if message.text.isdigit():
            text = int(message.text)
            if 1 <= text <= currentQuestion:
                currentQuestion = text - 1
                user_ans = user_ans[:currentQuestion]
                c.push(str(message.chat.id), [currentQuestion, user_ans, finished])
                # bot.send_message(message.chat.id, t[currentQuestion - 1])
                next_query(message)
                back_q = False
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
