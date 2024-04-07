import logging
from telegram.ext import Updater, CommandHandler, Application, MessageHandler, ConversationHandler, filters
from telegram import ReplyKeyboardMarkup
from config import BOT_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

tasks = {}  # Словарь для хранения задач
count_completed_tasks = 0  # Количество выполенных задач

# Определение различных состояний
ENTER_TITLE, ENTER_DESCRIPTION = range(2)  # добавление задач
ENTER_TASK = range(1)  # вывод задачи по названию
ENTER_TASK2, ENTER_RESPONSIBLE_PERSON, ENTER_DEADLINE = range(3)  # добавление ответсвенного и срока выполнения
ENTER_USER = range(1)  # вывод всех задач пользователя
ENTER_TASK3 = range(1)  # выполнение задачи
ENTER_TASK4 = range(1)  # удаление задачи
ENTER_TASK5, NAME_EDIT, ENTER_NEW_NAME = range(3)  # измение задачи


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        f"Добро пожаловать в бот-планировщик, {user.mention_html()}!\n"
        "Чтобы просмотреть все возможности бота, воспользуйтесь командой /help."
    )
    return ConversationHandler.END


# Подсказки с возможными командами бота
async def help(update, context):
    await update.message.reply_text(
        '/add_task - добавление задачи\n'
        '/assign_task - добавление ответственного за задачу и срок её выполнения.\n'
        "/list_task - список всех задач, вместе с ее ответственными и сроком выполнения.\n"
        "/get_task - информация о конкретной задаче\n"
        '/delete_task - удаление задачи\n'
        '/complete_task - выполнение задачи.\n'
    )
    return ConversationHandler.END


# Ответ на неизвестное сообщение
async def unknown(update, context):
    await update.message.reply_text(
        "Извините, я не могу понять Ваш запрос. Пожалуйста, воспользуйтесь командой /help для получения помощи.")


# Добавление задачи
async def add_task(update, context):
    await update.message.reply_text("Введите название задачи")
    return ENTER_TITLE


# Ввод названия задачи
async def enter_title(update, context):
    context.user_data['title'] = update.message.text
    await update.message.reply_text("Введите описание задачи")
    return ENTER_DESCRIPTION


# Ввод описания задачи
async def enter_description(update, context):
    context.user_data['description'] = update.message.text
    title = context.user_data['title']
    description = context.user_data['description']
    tasks[title] = []
    tasks[title].append(description)
    tasks[title].append('не указан')
    tasks[title].append('не указан')

    # Добавление задачи в Вашу систему
    await update.message.reply_text(f"Задача '{title}' с описанием '{description}' успешно добавлена!")
    return ConversationHandler.END


# Отмена операции
async def cancel(update, context):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END


# Вывод всех задач
async def list_task(update, context):
    if len(tasks) == 0:
        await update.message.reply_text(
            "У вас нет задач.\n"
            "Чтобы добавить задачи, воспользуйтесь функцией /add_task"
        )
    else:
        task_list = "\n".join(
            [f"{key}: {value[0]}, исполнитель - {value[1]}, срок выполнения - {value[2]}" for key, value in
             tasks.items()])
        await update.message.reply_text(f"Список задач:\n{task_list}")
        return ConversationHandler.END


# Вывод задачи по названию
async def get_task(update, context):
    await update.message.reply_text("Введите название задачи")
    return ENTER_TASK


# Ввод названия задачи
async def enter_task(update, context):
    title = update.message.text
    if title in tasks:
        await update.message.reply_text(
            f'Задача "{title}":\n'
            f'Описание - {tasks[title][0]}, исполнитель - {tasks[title][1]}, срок выполнения - {tasks[title][2]}')
    else:
        await update.message.reply_text(f'Задача с названием "{title}" не найдена.\n'
                                        f'Можете просмотреть список своих задач при помощи команды /list_task')
    return ConversationHandler.END


# Добавление отвественного за исполнение задачи; дедлайн
async def assign_task(update, context):
    await update.message.reply_text("Ведите название задачи")
    return ENTER_TASK2


# Ввод названия задачи
async def enter_task2(update, context):
    context.user_data['title'] = update.message.text
    title = context.user_data['title']
    if title not in tasks:
        await update.message.reply_text(f'Задача с названием "{title}" не найдена.\n'
                                        f'Можете просмотреть список своих задач при помощи команды /list_task')
        return ConversationHandler.END
    await update.message.reply_text(f'Введите ответственного для выполнения задачи "{title}"')
    return ENTER_RESPONSIBLE_PERSON


# Ввод ответственного
async def enter_responsible_person(update, context):
    context.user_data['person'] = update.message.text
    title = context.user_data['title']
    person = context.user_data['person']
    tasks[title][1] = person
    await update.message.reply_text(f'Введите срок выполнения')
    return ENTER_DEADLINE


# Ввод срока выполнения
async def enter_deadline(update, context):
    deadline = update.message.text
    title = context.user_data['title']
    person = context.user_data['person']
    tasks[title][2] = deadline
    await update.message.reply_text(f'Ответственный - {person} для задания "{title}" назначен.\n'
                                    f'Срок выполнения {deadline} установлен.')
    return ConversationHandler.END


# Список задач пользователя
async def user_task(update, context):
    await update.message.reply_text('Введите имя пользователя')
    return ENTER_USER


# Ввод имени пользователя
async def enter_user(update, context):
    user = update.message.text
    tasks_user = []
    for task in tasks:
        if user in tasks[task]:
            tasks_user.append(task)
    if len(tasks_user) > 0:
        tasks_list = "\n".join(
            [f"{task}: {tasks[task][0]}, исполнитель - {tasks[task][1]}, срок выполнения - {tasks[task][2]}" for
             task in tasks_user])
        await update.message.reply_text(
            f'Задачи пользователя{user}:\n{tasks_list}')
    else:
        await update.message.reply_text(f'Задачи пользователя {user} не найдены.')
        return ConversationHandler.END


# Вывод всех пользователей, ответственных за задачи
async def responsible_task(update, context):
    responsible_users = set()
    for task, details in tasks.items():
        responsible_user = details[1]
        responsible_users.add(responsible_user)

    if responsible_users:
        response_message = "Пользователи, ответственные за задачи:\n"
        for user in responsible_users:
            response_message += f"- {user}\n"
        await update.message.reply_text(response_message)
    else:
        await update.message.reply_text("Пока нет пользователей, ответственных за задачи.")
    return ConversationHandler.END


# Выполнение задачи
async def complete_task(update, context):
    await update.message.reply_text("Ведите название задачи")
    return ENTER_TASK3


# Ввод названия задачи
async def enter_task3(update, context):
    global count_completed_tasks

    task = update.message.text
    if task in tasks:
        del tasks[task]
        count_completed_tasks += 1
        await update.message.reply_text(
            f'Задача "{task}" выполнена. Поздравляем!\n'
            f'Вы выполнили {count_completed_tasks} задач!')
    else:
        await update.message.reply_text(f'Задача с названием "{task}" не найдена.')
        return ConversationHandler.END


# Удаление задачи
async def delete_task(update, context):
    await update.message.reply_text("Ведите название задачи")
    return ENTER_TASK4


# Ввод названия задачи
async def enter_task4(update, context):
    task = update.message.text
    if task in tasks:
        del tasks[task]
        await update.message.reply_text(f'Задача "{task}" успешно удалена.')
    else:
        await update.message.reply_text(f'Задача с названием "{task}" не найдена.')
    return ConversationHandler.END


# Изменение (названия, описания, ответственного, срока выполенния)
async def edit_task(update, context):
    await update.message.reply_text("Ведите название задачи")
    return ENTER_TASK5


# Ввод названия задачи
async def enter_task5(update, context):
    context.user_data['task'] = update.message.text
    task = context.user_data['task']
    if task not in tasks:
        await update.message.reply_text(f'Задача с названием "{task}" не найдена.')
        return ConversationHandler.END
    await update.message.reply_text(f'Что Вы хотите редактировать?\n'
                                    f'Название/Описание/Ответственный/Срок выполнения')
    return NAME_EDIT


# Ввод того, что именно нужно изменить (название/описание/ответственного/срок выполенния)
async def name_edit(update, context):
    subject = update.message.text
    subject = subject.lower()
    context.user_data['subject'] = subject
    if subject not in ['название', 'описание', 'ответственный', 'срок выполнения']:
        await update.message.reply_text('Извините, я не могу понять Ваш запрос.\n'
                                        'Изменить можно: Название/Описание/Ответственный/Срок выполнения')
        return ConversationHandler.END
    await update.message.reply_text(f'Введите новое {subject}')
    return ENTER_NEW_NAME


# Ввод нового значения
async def enter_new_name(update, context):
    new_name = update.message.text
    task = context.user_data['task']
    subject = context.user_data['subject']

    if subject == 'название':
        tasks[new_name] = tasks[task]
        del tasks[task]
        await update.message.reply_text('Новое название установлено.')
    elif subject == 'описание':
        tasks[task][0] = new_name
        await update.message.reply_text('Новое описание установлено.')
    elif subject == 'ответственный':
        tasks[task][1] = new_name
        await update.message.reply_text('Новый ответственный установлен.')
    elif subject == 'срок выполнения':
        tasks[task][2] = new_name
        await update.message.reply_text('Новый срок выполнения установлен.')
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))

    adding_tasks = ConversationHandler(
        entry_points=[CommandHandler('add_task', add_task)],
        states={
            ENTER_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_title)],
            ENTER_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_description)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(adding_tasks)

    application.add_handler(CommandHandler("list_task", list_task))

    getting_task = ConversationHandler(
        entry_points=[CommandHandler('get_task', get_task)],
        states={
            ENTER_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_task)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(getting_task)

    assigning_task = ConversationHandler(
        entry_points=[CommandHandler('assign_task', assign_task)],
        states={
            ENTER_TASK2: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_task2)],
            ENTER_RESPONSIBLE_PERSON: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_responsible_person)],
            ENTER_DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_deadline)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(assigning_task)

    person_task = ConversationHandler(
        entry_points=[CommandHandler('user_task', user_task)],
        states={
            ENTER_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_user)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(person_task)

    application.add_handler(CommandHandler("responsible_task", responsible_task))

    completing_task = ConversationHandler(
        entry_points=[CommandHandler('complete_task', complete_task)],
        states={
            ENTER_TASK3: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_task3)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(completing_task)

    deleting_task = ConversationHandler(
        entry_points=[CommandHandler('delete_task', delete_task)],
        states={
            ENTER_TASK4: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_task4)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(deleting_task)

    editing_task = ConversationHandler(
        entry_points=[CommandHandler('edit_task', edit_task)],
        states={
            ENTER_TASK5: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_task5)],
            NAME_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_edit)],
            ENTER_NEW_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_new_name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(editing_task)

    application.add_handler(MessageHandler(filters.COMMAND, unknown))  # введение непонятного текстового сообщения
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))  # введение неправильной команды
    application.run_polling()


if __name__ == '__main__':
    main()
