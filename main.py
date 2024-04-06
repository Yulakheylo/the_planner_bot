from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from config import BOT_TOKEN

# Определение различных состояний
ENTER_TITLE, ENTER_DESCRIPTION = range(2)
tasks = {}  # Словарь для хранения задач

async def start(update, context):
    await update.message.reply_text("Добро пожаловать в бот-планировщик, {user.mention_html()}!\n"
                                    "Чтобы просмотреть все возможности бота, воспользуйтесь командой /help")
    return ConversationHandler.END


# Подсказки с возможными командами бота
async def help(update, context):
    await update.message.reply_text(
        "/add_task - добавление задачи.\n\n"
        '/assign_task - добавление ответственного за задачу и срок её выполнения.\n'
        'Например, /assign_task Сходить в магазин, Иван Иванов, 24.04.2024\n'
        'Если вы хотите редактировать срок выполнения или изменить ответственного, просто заново напишите '
        'команду /assign_task\n'
        'Например, /assign_task Сходить в магазин, Петя Смирнов, 30.05.2024\n\n'
        "/list_task - список всех задач, вместе с ее ответственными и сроком выполнения.\n\n"
        "/responsible_task - выводит всех пользователей ответственные за задачи\n\n"
        "/get_task - информация о конкретной задаче. Вызов в формате /get_task {название задачи}\n"
        "Например, /get_task Сходить в магазин\n\n"
        '/delete_task - удаление задачи\n'
        'Например, /delete_task Сходить в магазин'
    )
    return ConversationHandler.END

async def add_task(update, context):
    await update.message.reply_text("Введите название задачи:")
    return ENTER_TITLE


async def enter_title(update, context):
    context.user_data['title'] = update.message.text
    await update.message.reply_text("Введите описание задачи:")
    return ENTER_DESCRIPTION


async def enter_description(update, context):
    context.user_data['description'] = update.message.text
    title = context.user_data['title']
    description = context.user_data['description']
    tasks[title] = []
    tasks[title].append(description)

    # Добавление задачи в Вашу систему
    await update.message.reply_text(f"Задача '{title}' с описанием '{description}' успешно добавлена!")
    return ConversationHandler.END


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
            [f"{key}: {value[0]}" for key, value in
             tasks.items()])
        await update.message.reply_text(f"Список задач:\n{task_list}")
        return ConversationHandler.END


# Ответ на неизвестное сообщение
async def unknown(update, context):
    await update.message.reply_text(
        "Извините, я не могу понять Ваш запрос. Пожалуйста, воспользуйтесь командой /help для получения помощи.")
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add_task', add_task)],
        states={
            ENTER_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_title)],
            ENTER_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_description)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("list_task", list_task))
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))  # введение непонятного текстового сообщения
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))  # введение неправильной команды
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
