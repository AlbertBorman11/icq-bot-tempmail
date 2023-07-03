#!/usr/bin/env python
import logging
from threading import Thread
import time
from bot.bot import Bot
from bot.handler import MessageHandler
from onesec_api import Mailbox

TOKEN = "" # Token from @metabot (ICQ)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y.%m.%d %I:%M:%S %p', level=logging.DEBUG)
bot = Bot(token=TOKEN)

def message_cb(bot, event):
    if event.text != '/mail':
        # Send a welcome message to the user if the command is not "/mail"
        bot.send_text(chat_id=event.from_chat, text=f'Hello, {event.data["from"]["firstName"]}!\n'
                                                     f'This bot is created for quickly getting temporary emails.\n'
                                                     f'To use the bot, type /mail\n\n')
    elif event.text == '/mail':
        # Start a new thread to handle the email retrieval process
        Thread(target=handle_mail, args=(bot, event)).start()

def handle_mail(bot, event):
    # Create a mailbox object
    ma = Mailbox('')
    
    # Generate a temporary email address
    email = f'{ma._mailbox_}@1secmail.com'
    
    # Send the email address to the user
    bot.send_text(chat_id=event.from_chat, text='📫 Your email:')
    bot.send_text(chat_id=event.from_chat, text=email)
    
    # Provide instructions to the user
    bot.send_text(chat_id=event.from_chat, text='Send an email, it will be automatically checked every 5 seconds.\n'
                                                'If a new email arrives, we will notify you!\n\n'
                                                'You can receive only 1 email on 1 mailbox.')
    
    while True:
        # Check for new emails every 5 seconds
        mb = ma.filtred_mail()
        
        if isinstance(mb, list):
            # If a new email is found, read its details and send them to the user
            mf = ma.mailjobs('read', mb[0])
            js = mf.json()
            fromm = js['from']
            theme = js['subject']
            mes = js['textBody']
            bot.send_text(chat_id=event.from_chat, text=f'📩 New email:\n'
                                                        f'From: {fromm}\n'
                                                        f'Theme: {theme}\n'
                                                        f'Message: {mes}')
            break
        else:
            # If no new email is found, continue checking
            pass
        time.sleep(5)

# Register the message handler callback
bot.dispatcher.add_handler(MessageHandler(callback=message_cb))

# Start polling for new messages
bot.start_polling()

# Keep the bot idle
bot.idle()
