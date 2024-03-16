# Импортируем необходимые классы.
import logging
import keyboard
import random
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ConversationHandler, MessageHandler, filters, CommandHandler, Updater
from config import BOT_TOKEN, ID_GROUP

# Запускаем логгирование
logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

# txt файл с текстом первого сообщения
file = open("media/cofee.txt", encoding="utf8").read()



# кнопки для некоторых вопросов
# requirement
reply_keyboard = [['Моделирование и печать'],
				  ['Печать']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True,
							 input_field_placeholder="Что вас интерисует?")

# start
reply_keyboard_strt = [['Да', "/stop"]]
markup_start = ReplyKeyboardMarkup(reply_keyboard_strt, one_time_keyboard=True, resize_keyboard=True,
								   input_field_placeholder="Сделайте выбор")

# application
reply_keyboard_application = [['Да', "Заново"]]
markup_application = ReplyKeyboardMarkup(reply_keyboard_application, one_time_keyboard=True, resize_keyboard=True,
										 input_field_placeholder="Проверте данные перед отправкой!")

# pchoice_of_plastic
reply_keyboard_plastic = [['PLA', 'ABS', 'HIPS', "PVA"],
						  ['SBS', 'NYLON', "FLEX", 'PETG']]
markup_plastic = ReplyKeyboardMarkup(reply_keyboard_plastic, one_time_keyboard=True, resize_keyboard=True,
									 input_field_placeholder="Выберите пластик :)")

# кнопки в сообщения бота choice_of_plastic
keyboard = [
	[InlineKeyboardButton("Option 1", url="https://cvetmir3d.ru/blog/poleznoe/vidy-plastika-dlya-3d-printera/")]]

reply_markup = InlineKeyboardMarkup(keyboard)

# кнопка
keyboard_disk = [
	[InlineKeyboardButton("DropMiFiles", url="https://dropmefiles.com/")],
	[InlineKeyboardButton("ЯндексDisk", url="https://360.yandex.ru/disk/")],
	[InlineKeyboardButton("GoogleDisk", url="https://drive.google.com/drive/my-drive?hl=ru")]]

reply_markup_disk = InlineKeyboardMarkup(keyboard_disk)


# Определяем функцию-обработчик сообщений.
# У неё два параметра, updater, принявший сообщение и контекст - дополнительная информация о сообщении.

def main():
	application = Application.builder().token(BOT_TOKEN).build()
	application.add_handler(CommandHandler("close", close_keyboard))

	conv_handler = ConversationHandler(
		# Точка входа в диалог.
		# В данном случае — команда /start. Она задаёт первый вопрос.
		entry_points=[CommandHandler('start', start)],

		# Состояние внутри диалога.
		# Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
		states={
			# Функция читает ответ на первый вопрос и задаёт второй.
			0: [MessageHandler(filters.TEXT & ~filters.COMMAND, sity)],
			1: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
			# Функция читает ответ на второй вопрос и завершает диалог.
			2: [MessageHandler(filters.TEXT & ~filters.COMMAND, requirement)],
			3: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
			4: [MessageHandler(filters.TEXT & ~filters.COMMAND, descrip_file)],
			5: [MessageHandler(filters.TEXT & ~filters.COMMAND, descrip_photo)],
			6: [MessageHandler(filters.PHOTO & ~filters.COMMAND, choice_of_plastic)],
			7: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)],
			8: [MessageHandler(filters.TEXT & ~filters.COMMAND, proverka)]

		},

		# Точка прерывания диалога. В данном случае — команда /stop.
		fallbacks=[CommandHandler('stop', stop)]
	)

	application.add_handler(conv_handler)

	application.run_polling()


# точка входа в диалог
async def start(update, context):
	await update.message.reply_text(file, reply_markup=markup_start)
	return 0


# Дальнейшие вопросы для коректного заббора сообщений-ответов нужно вопрос задавать в предыдущей функции
async def sity(update, context):
	await update.message.reply_text("В каком городе вы живёте?")
	return 1


async def name(update, context):
	await update.message.reply_text("Ваше имя:")
	d = {"Город": update.message.text}
	context.bot_data.update(d)
	return 2


async def requirement(update, context):
	await update.message.reply_text("Что вам нужно?", reply_markup=markup)
	d = {"ФИО": update.message.text}
	context.bot_data.update(d)
	return 3


async def description(update, context):
	await update.message.reply_text("Дайте краткое описание:")
	d = {"Требования": update.message.text}
	context.bot_data.update(d)
	return 4


async def descrip_file(update, context):
	await update.message.reply_text("Пришлите ссылку на архив с референсом:\n"
									"  готовая 3D модель, чертёжи и тд",
									reply_markup=InlineKeyboardMarkup(keyboard_disk))
	d = {"Описание": update.message.text}
	context.bot_data.update(d)
	return 5


async def descrip_photo(update, context):
	await update.message.reply_html(
		text="Пришлите фото желаемой работы \n "
			 "<b>!Если вы сидите с ПК, то отправте с сжатием!</b>")

	d = {"Ссылка": update.message.text}
	context.bot_data.update(d)
	return 6


async def choice_of_plastic(update, context):
	await update.message.reply_text("Выберите вид пластика", reply_markup=markup_plastic)
	await update.message.reply_text("Информация о пластиках", reply_markup=InlineKeyboardMarkup(keyboard))
	# (красивый кнопка)
	d = {"Референс": update.message.photo[0].file_id}
	context.bot_data.update(d)
	return 7


async def second_response(update, context):
	d = {"Пластик": update.message.text}
	context.bot_data.update(d)

	weather = update.message.text
	logger.info(weather)
	await update.message.reply_text("Ваша заявка сформирована")

	# формируем одно большое сообщение сюдаже надо приписать пересылку картинки желательно её хранить с id пользователя
	# иначе когда 2 чела одновременно будут делать заявку бот попутает картинки
	s = (f"Город: {context.bot_data['Город']} \n"
		 f"ФИО: {context.bot_data['ФИО']} \n"
		 f"Требования: {context.bot_data['Требования']} \n"
		 f"Описание: {context.bot_data['Описание']} \n"
		 f"Пластик: {context.bot_data['Пластик']} \n"
		 f"Референс: {context.bot_data['Ссылка']}")
	await update.message.reply_text(s)
	await update.message.reply_photo(context.bot_data['Референс'])

	# опять раньше спрашиваем тк будет включена след функция
	await update.message.reply_text("Всё верно?", reply_markup=markup_application)

	return 8


# функция костыль (кудаж без них) спрашиваем у пользователя всё ли верно если да то присылаем в общий чат если нет,
# то всё заново
async def proverka(update, context):
	if update.message.text == "Да":
		await application(update, context)
	if update.message.text == "Заново":
		await update.message.reply_text("Давайте начнём заново /start")

	return ConversationHandler.END


# функция отправки заявки в общ группу
async def application(update, context):
	s = (f"Требования: {context.bot_data['Требования']} \n"
		 f"Город: {context.bot_data['Город']} \n"
		 f"Пользователь: @{update.message.chat.username}"
		 f" {update.message.chat.id} \n"
		 f"Имя: {context.bot_data['ФИО']} \n"
		 f"Пластик: {context.bot_data['Пластик']} \n"
		 f"Описание: {context.bot_data['Описание']} \n"
		 f"Референс: {context.bot_data['Ссылка']}")
	await context.bot.send_message(
		chat_id=ID_GROUP,
		text=s
	)

	await context.bot.send_photo(ID_GROUP, context.bot_data['Референс'])
	await update.message.reply_text("Заявка успешно отправлена! \n"
									"Для более приятного ожидания ответа, вот вам музончик :)")
	# mp3 файл для приятного ожидания
	musik_id = random.randint(1, 6)
	music = open(f"media/{musik_id}.mp3", "rb")
	await update.message.reply_audio(audio=music)
	await stop(update, context)


async def stop(update, context):
	await update.message.reply_text("Всего доброго!")
	return ConversationHandler.END


async def close_keyboard(update, context):
	await update.message.reply_text(
		"Ok",
		reply_markup=ReplyKeyboardRemove()
	)


# Это Серёжка, он держит весь этот код
#       (•_• )                                  ／＞　 　フ А это Барсик
# 　　＿ノ ヽ ノ＼ __                             |  -  - |    Он поддерживает Серёжку
# 　 /　`/ ⌒Ｙ⌒ Ｙ　ヽ                          ／` ミ＿xノ
# 　(　 (三ヽ人　 /　　 |                       /　　　　 |
# 　|　ﾉ⌒＼ ￣￣ヽ　 ノ                        /　 ヽ　　 ﾉ
# 　ヽ＿＿＿＞､＿＿_／                         │　　|　|　|
# 　　　 ｜( 王 ﾉ〈　                      ／￣|　　 |　|　|
# 　　　 /ﾐ`ー―彡\                       | (￣ヽ＿ヽ) __)
#                                       ＼二つ


if __name__ == '__main__':
	main()
