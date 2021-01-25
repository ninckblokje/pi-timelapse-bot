import logging
import pickle
import timelapse
import uuid
from telegram.ext import (
    CommandHandler,
    Updater
)

_pickle_file = 'config/telegram.p'

_dispatcher = None
_updater = None

_chatkey = None
_trusted_chats = ()

def wrap_telegram_cmd(verifyChatId = True):
    def inner_wrap_telegram_cmd(func):
        def wrapper(*args, **kwargs):
            functionName = func.__name__
            try:
                chatId = args[0].effective_chat.id
                if verifyChatId and chatId not in _trusted_chats:
                    logging.warn('Received %s command from unauthorized chat %s', functionName, chatId)
                    return
                elif not verifyChatId:
                    logging.info('Received %s command from unknown chat %s', functionName, chatId)
                else:
                    logging.debug('Received %s command from chat %s', functionName, chatId)

                return func(*args, **kwargs)
            except:
                logging.exception('Exception in command: %s', functionName)
        return wrapper
    return inner_wrap_telegram_cmd

def init(config):
    _load_trusted_chats()

    global _chatkey
    _chatkey = str(uuid.uuid4())
    token = config['TELEGRAM'].get('token')

    global _updater, _dispatcher
    _updater = Updater(token=token, use_context=True)
    _dispatcher = _updater.dispatcher

    _set_cmds()

    _dispatcher.add_handler(CommandHandler('start', _start_cmd))
    _dispatcher.add_handler(CommandHandler('status', _status_cmd))
    _dispatcher.add_handler(CommandHandler('stop', _stop_cmd))

    _dispatcher.add_handler(CommandHandler('timelapse_last_img', _timelapse_last_img))
    _dispatcher.add_handler(CommandHandler('timelapse_render', _timelapse_render))
    _dispatcher.add_handler(CommandHandler('timelapse_start', _timelapse_start))
    _dispatcher.add_handler(CommandHandler('timelapse_stop', _timelapse_stop))

def _renderingCallback(chatId):
    def innerRenderingCallback(successfull, renderedFile):
        if successfull:
            with open(renderedFile, 'rb') as v:
                _dispatcher.bot.send_video(chat_id=chatId, video=v)
        else:
            _dispatcher.bot.send_message(chat_id=chatId, text='Rendering failed')
    return innerRenderingCallback

def start_polling():
    logging.info('Starting Telegram polling, chat key: %s', _chatkey)
    _updater.start_polling()
    _updater.idle()

@wrap_telegram_cmd()
def _timelapse_last_img(update, context):
    chatId = update.effective_chat.id

    lastImg = timelapse.get_last_img()
    if lastImg == None:
        context.bot.send_message(chat_id=chatId, text='No timelapse images found')
    else:
        with open(lastImg, 'rb') as p:
            context.bot.send_photo(chat_id=chatId, photo=p)

@wrap_telegram_cmd()
def _timelapse_render(update, context):
    chatId = update.effective_chat.id

    if timelapse.render(_renderingCallback(chatId)):
        context.bot.send_message(chat_id=chatId, text='Timelapse rendering started')
    else:
        context.bot.send_message(chat_id=chatId, text='Unable to start timelapse rendering')

@wrap_telegram_cmd()
def _timelapse_start(update, context):
    chatId = update.effective_chat.id

    if timelapse.start():
        context.bot.send_message(chat_id=chatId, text='Timelapse recording started')
    else:
        context.bot.send_message(chat_id=chatId, text='Unable to start timelapse recording')

@wrap_telegram_cmd()
def _timelapse_stop(update, context):
    chatId = update.effective_chat.id

    timelapse.stop()
    context.bot.send_message(chat_id=chatId, text='Timelapse recording stopped')

@wrap_telegram_cmd(verifyChatId=False)
def _start_cmd(update, context):
    chatId = update.effective_chat.id

    receivedChatkey = context.args
    if len(receivedChatkey) == 1 and receivedChatkey[0] == _chatkey:
        logging.debug('Received start command from chat %s', chatId)

        _add_chat_id(chatId)
        context.bot.send_message(chat_id=chatId, text='Welcome!')
    else:
        logging.warn('Received wrong chat key for start command from unauthorized chat %s', chatId)

@wrap_telegram_cmd()
def _status_cmd(update, context):
    chatId = update.effective_chat.id

    if timelapse.is_running():
        context.bot.send_message(chat_id=chatId, text='Timelapse recording is active now')
    else:
        context.bot.send_message(chat_id=chatId, text='Timelapse recording is not active')

@wrap_telegram_cmd()
def _stop_cmd(update, context):
    chatId = update.effective_chat.id

    context.bot.send_message(chat_id=chatId, text='Bye!')
    _remove_chat_id(chatId)

def _add_chat_id(chatId):
    logging.debug('Adding chat %s', chatId)
    global _trusted_chats
    _trusted_chats = _trusted_chats + (chatId,)
    with open(_pickle_file, 'wb') as f:
        logging.debug('Saving Telegram pickle file')
        pickle.dump(_trusted_chats, f)

def _load_trusted_chats():
    try:
        with open(_pickle_file, 'rb') as f:
            logging.debug('Loading Telegram pickle file')
            global _trusted_chats
            _trusted_chats = pickle.load(f)
    except FileNotFoundError:
        with open(_pickle_file, 'x+b') as f:
            logging.debug('Created Telegram pickle file')
            pickle.dump(_trusted_chats, f)

def _remove_chat_id(chatId):
    logging.debug('Removing chat %s', chatId)
    global _trusted_chats
    _trusted_chats = tuple(x for x in _trusted_chats if x != chatId)
    with open(_pickle_file, 'wb') as f:
        logging.debug('Saving Telegram pickle file')
        pickle.dump(_trusted_chats, f)

def _set_cmds():
    logging.debug('Registering commands')
    _updater.bot.set_my_commands([
        ("start", "Starts interaction"),
        ("stop", "Stops interaction"),
        ("status", "Current status of running jobs, for example timelapse recording"),
        ("timelapse_last_img", "Return the last image created for a timelapse recorder"),
        ("timelapse_render", "Render a timelapse video"),
        ("timelapse_start", "Start a timelapse recording"),
        ("timelapse_stop", "Stop a timelapse recording")
    ])
