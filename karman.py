﻿#!/usr/bin/python3
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ChatAction, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    RegexHandler,
    ConversationHandler,
)
from telegram.error import (
    TelegramError,
    Unauthorized,
    BadRequest,
    TimedOut,
    ChatMigrated,
    NetworkError,
)
import logging
import modules
import constant
from functools import wraps

(
    MENU,
    CHECK_STEP1,
    ADVANCED_STEP,
) = range(3)

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename=constant.LOG_STABLE,
)
logger = logging.getLogger(__name__)

back_reply_keyboard = [["В меню"]]

# Проверка по ID и доступ к боту
def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        user = update.message.from_user
        LIST_OF_USERS = modules.load_users(func)
        if user_id not in LIST_OF_USERS:
            quote_message = f"Доступ запрещен"
            update.message.reply_text(quote_message)
            logger.warning(
                f"Ошибка, пользователь не авторизован с ID {user_id}, Его имя {user.full_name}"
            )
            context.bot.send_message(
                chat_id=constant.MAIN_ADMIN,
                text=f"Ошибка, пользователь не авторизован с ID {user_id}, Имя пользователя - {user.full_name}.",
            )
            return
        return func(update, context, *args, **kwargs)

    return wrapped

@restricted  # Объявляем где должен отработать метод доступа
def start(update, context):
    # Стартовый метод, который подгружает меню а так же выдаем приветственное сообщение
    user = update.message.from_user
    reply_keyboard = modules.back_to_user_keyboard("menu")
    update.message.reply_text(
        f"{constant.hi_message}",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,  resize_keyboard=True
        ),
    )
    logger.info(f"Приветствие или команда /start. Пользователь - {user.full_name}")
    return CHECK_STEP1


@restricted
def start_var2(update, context):
    # Стартовый метод, который подгружает меню а так же выдаем приветственное сообщение
    user = update.message.from_user
    reply_keyboard = modules.back_to_user_keyboard("menu")
    update.message.reply_text(
        constant.VICTORY + constant.hi_message,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,  resize_keyboard=True
        ),
    )
    logger.info(f"Приветствие или команда /start. Пользователь - {user.full_name}")
    return MENU

def menu(update, context):
    # Метод "Разруливающий", отбрасывает пользователя туда куда нужно
    message = update.message.text
    user = update.message.from_user
    if "/start" in message:
        update.message.reply_text(
            "Пожалуйста введите IP"
        )
        logger.info(f"Переход по шагу - Проверить устройство для {user.full_name}")
        return CHECK_STEP1
    else:
        reply_keyboard = modules.back_to_user_keyboard("menu")
        update.message.reply_text(
            "Возращаемся в меню",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,  resize_keyboard=True
            ),
        )
        return CHECK_STEP1

def check_step1(update, context):
    user = update.message.from_user
    # Первый этап проверки, метод собирающий базовую информацию SYSNAME, Модель устройства а так же собирающий Uptime
    host = update.message.text
    chat_id = update.effective_user.id
    model = modules.get_model(host)
    id_mass = modules.load_id_users(chat_id)
    # Выгружаем хост и модель в массив
    hosts.insert(id_mass, host)
    models.insert(id_mass, model)

    result = modules.basic_info(host, model)
    logger.info(f"Получаем базовую информацию {user.full_name} для устройства {host}")
    if (
        ("Неверный IP" in result)
        
    ):
        logger.info(
            f"Условие неверный IP или устройство не на связи. Пользователь - {user.full_name}, IP - {host}"
        )
        reply_keyboard = modules.back_to_user_keyboard("menu")
        update.message.reply_text(
            f"{result}",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,  resize_keyboard=True
            ),
        )
        return CHECK_STEP1
    else:
        get_type = modules.get_type(host, model)
        if get_type == "switches":
            
            reply_keyboard = modules.back_to_user_keyboard(
                'get_type == "switches"'
            )
            logger.info(
                f"Выбор пункта - Далее, Пользователь - {user.full_name}, IP - {host}"
            )
            update.message.reply_text(
                f"{result}",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard,  resize_keyboard=True
                ),
            )
            return CHECK_STEP1
        else:
            reply_keyboard = modules.back_to_user_keyboard("menu")
            update.message.reply_text(
                "Возращаемся в меню",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard,  resize_keyboard=True
                ),
            )
            return CHECK_STEP1


def cancel(update, context):
    user = update.message.from_user
    logger.info(f"User {user.full_name} canceled the conversation.")
    update.message.reply_text("Удачного дня!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def error(update, context):
    try:
        logger.warning(f"Update {update} caused error {context.error}")
        raise context.error
    except Unauthorized:
        pass
        # remove update.message.chat_id from conversation list
    except BadRequest:
        pass
        # handle malformed requests - read more below!
    except TimedOut:
        pass
        # handle slow connection problems
    except NetworkError:
        pass
        # handle other connection problems
    except ChatMigrated as e:
        pass
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        pass
        # handle all other telegram related errors

def main():
    global USERS
    USERS = modules.load_users(1)
    global hosts, models
    hosts = []
    models = []
    for gen in range(len(USERS)):
        hosts.append('')
        models.append('')
    updater = Updater(constant.TOKEN, use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.text, start),
            CommandHandler("start", start_var2, run_async=True),
        ],
        states={
            MENU: [MessageHandler(Filters.text, menu, run_async=True)],
            
            CHECK_STEP1: [MessageHandler(Filters.text, check_step1, run_async=True)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()