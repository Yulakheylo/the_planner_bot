import logging
from telegram.ext import Updater, CommandHandler, Application, MessageHandler, filters
from telegram import ReplyKeyboardMarkup
from config import BOT_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

tasks = {}  # Словарь для хранения задач


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        f"Добро пожаловать в бот-планировщик, {user.mention_html()}!\n"
        "Чтобы просмотреть все возможности бота, воспользуйтесь командой /help."
    )


# Подсказки с возможными командами бота
async def help(update, context):
    await update.message.reply_text(
        "/add_task - добавление задачи. Вызов в формате /add_task {название задачи}, {описание}\n"
        "Например, /add_task Сходить в магазин, Купить 3 шт. мороженого\n\n"
        "/list_task - список всех задач.\n\n"
        "/get_task - информация о конкретной задаче. Вызов в формате /get_task {название задачи}\n"
        "Например, /get_task Сходить в магазин"
    )


# Ответ на неизвестное сообщение
async def unknown(update, context):
    await update.message.reply_text(
        "Извините, я не могу понять Ваш запрос. Пожалуйста, воспользуйтесь командой /help для получения помощи.")


# Добавление задачи (в формате команда (/add_task) название задачи; описание задачи)
async def add_task(update, context):
    text = context.args
    text = (' '.join(text)).split(',')
    if len(text) < 2:
        await update.message.reply_text(
            "Вы не ввели название / описание задачи.\n"
            "Введите название задачи, которую хотите добавить в формате {название}, {описание}.\n"
            "Например, /add_task Сходить в магазин, Купить 3 шт. мороженого"
        )
    else:
        title = text[0]
        task = ' '.join(text[1:])
        if title in tasks:  # Если задача уже есть в списке
            await update.message.reply_text(
                f'Задача "{title}" уже существует.\n'
                f'Вы можете просмотреть информацию о данной задаче вызвав команду /get_task {title}\n'
                f'Пожалуйста, придумайте новое название задачи'
            )
        else:
            tasks[title] = []
            tasks[title].append(task)
            tasks[title].append('не указан')
            tasks[title].append('не указан')
            await update.message.reply_text(f'Задача "{title}" успешно добавлена!')


# Вывод всех задач
async def list_task(update, context):
    if len(tasks) == 0:
        await update.message.reply_text(
            "У вас нет задач.\n"
            "Чтобы добавить задачи, воспользуйтесь функцией /add_task"
        )
    else:
        task_list = "\n".join(
            [f"{key}: описание - {value[0]}, исполнитель - {value[1]}, срок выполнения - {value[2]}" for key, value in
             tasks.items()])
        await update.message.reply_text(f"Список задач:\n{task_list}")


# Вывод задачи по названию
async def get_task(update, context):
    text = ' '.join(context.args)
    if len(text) < 1:
        await update.message.reply_text(
            "Вы не ввели название задачи.\n"
            "Введите название задачи, о которой Вы хотите увидеть информацию.\n"
            "Например, /get_task Сходить в магазин"
        )
    else:
        if text in tasks:
            await update.message.reply_text(f"Задача {text}: {tasks[text]}")
        else:
            await update.message.reply_text(f'Задача с названием "{text}" не найдена.')


# Добавление отвественного за исполнение задачи; дедлайн
async def assign_task(update, context):
    text = context.args
    text = (' '.join(text)).split(',')
    if len(text) < 3:
        await update.message.reply_text(
            "Вы не ввели ответственного / срок выполнения задачи\n"
            "Введите название задачи, ответственного и срок выполнения задачи\n"
            "в формате {название задачи}, {ответственный}, {срок выполнения}.\n"
            "Например, /assign_task Сходить в магазин, Иван Иванов, 24.04.2024"
        )
    else:
        task = text[0]
        person = text[1]
        deadline = ' '.join(text[2])
        tasks[task][1] = person
        tasks[task][2] = deadline
        await update.message.reply_text(f'Ответственный - {person} для задания "{task}" назначен.\n'
                                        f'Срок выполнения {deadline} установлен')


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("add_task", add_task))
    application.add_handler(CommandHandler("list_task", list_task))
    application.add_handler(CommandHandler("get_task", get_task))
    application.add_handler(CommandHandler("assign_task", assign_task))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))  # Обработчик для неопределенных текстовых сообщений
    application.run_polling()


if __name__ == '__main__':
    main()
