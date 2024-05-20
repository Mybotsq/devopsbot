import logging
import re
import psycopg2
from psycopg2 import Error
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import paramiko

import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')

host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def get_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port, username, password)
    return client

def get_postgresql_connection():
    connection = None
    try:
        connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                      password=os.getenv('DB_PASSWORD'),
                                      host=os.getenv('DB_HOST'),
                                      port=os.getenv('DB_PORT'),
                                      database=os.getenv('DB_DATABASE'))
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL", error)
    return connection

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def cancel(update: Update, context):
    update.message.reply_text('Диалог был отменен.')
    return ConversationHandler.END

def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email адресов: ')
    return 'findEmails'

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль: ')
    
    return 'verifyPassword'

def findEmails(update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) email адреса
    emailRegex = re.compile(r"\b[a-zA-Z0-9._%+-]+(?<!\.\.)@[a-zA-Z0-9.-]+(?<!\.)\.[a-zA-Z]{2,}\b") # Регулярное выражение для поиска email
    emailList = emailRegex.findall(user_input) # Ищем email адреса

    if not emailList: # Обрабатываем случай, когда email адресов нет
        update.message.reply_text('Email адреса не найдены')
        return ConversationHandler.END # Завершаем выполнение функции
    
    emails = '' # Создаем строку, в которую будем записывать email адреса
    for i, email in enumerate(emailList):
        emails += f'{i+1}. {email}\n' # Записываем очередной email
        
    update.message.reply_text(emails) # Отправляем сообщение пользователю
    
    context.user_data['found_data_emails'] = emailList
    update.message.reply_text('Хотите сохранить найденные email-адреса в базу данных? Отправьте "да" для сохранения.')

    return 'saveEmailData'


def findPhoneNumbers(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    # Регулярное выражение для поиска номеров телефонов
    phoneNumRegex = re.compile(r'(\+7|8|7)[\s\(-]?(\d{3})[\)\s-]?(\d{1,3})[\s-]?(\d{2})[\s-]?(\d{2})')

    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов
    
    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END  # Завершаем выполнение функции

    phoneNumbers = ''
    phonematch = [''.join(match) for match in phoneNumberList]  # Создаем строку, в которую будем записывать номера телефонов
    for index, phone in enumerate(phonematch, start=1):
        phoneNumbers += f"{index}. {phone}\n"

    update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю
    
    context.user_data['found_data_phones'] = phoneNumberList
    update.message.reply_text('Хотите сохранить найденные номера телефонов в базу данных? Отправьте "да" для сохранения.')

    return 'savePhoneData'
    

def verifyPassword(update: Update, context):

    password = update.message.text
    passwordRegex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()]).{8,}$')
    if passwordRegex.match(password):
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')      
    return ConversationHandler.END

def get_release(update, context):
    try:
        ssh_client = get_ssh_client()
        stdin, stdout, stderr = ssh_client.exec_command('cat /etc/*release')
        release_info = stdout.read().decode('utf-8')
        update.message.reply_text(release_info)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении информации о релизе: {e}")
    finally:
        ssh_client.close()
        
def get_release(update, context):
    try:
        ssh_client = get_ssh_client()
        stdin, stdout, stderr = ssh_client.exec_command('cat /etc/*release')
        release_info = stdout.read().decode('utf-8')
        update.message.reply_text(release_info)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении информации о релизе: {e}")
    finally:
        ssh_client.close()
        
def get_uname(update, context):
    try:
        ssh_client = get_ssh_client()
        stdin, stdout, stderr = ssh_client.exec_command('uname -a')
        uname_info = stdout.read().decode('utf-8')
        update.message.reply_text(uname_info)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении информации о системе: {e}")
    finally:
        ssh_client.close()

def get_uptime(update, context):
    try:
        ssh_client = get_ssh_client()
        stdin, stdout, stderr = ssh_client.exec_command('uptime')
        uptime_info = stdout.read().decode('utf-8')
        update.message.reply_text(uptime_info)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении информации о времени работы: {e}")
    finally:
        ssh_client.close()
        
def get_df(update, context):
    try:
        ssh_client = get_ssh_client()
        stdin, stdout, stderr = ssh_client.exec_command('df -h')
        uptime_info = stdout.read().decode('utf-8')
        update.message.reply_text(uptime_info)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении информации о дисках: {e}")
    finally:
        ssh_client.close()
        
def get_free(update, context):
    try:
        ssh_client = get_ssh_client()
        stdin, stdout, stderr = ssh_client.exec_command('free -h')
        uptime_info = stdout.read().decode('utf-8')
        update.message.reply_text(uptime_info)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении информации о свободной памяти: {e}")
    finally:
        ssh_client.close()
        
def get_mpstat(update, context):
    try:
        ssh_client = get_ssh_client()
        stdin, stdout, stderr = ssh_client.exec_command('mpstat')
        uptime_info = stdout.read().decode('utf-8')
        update.message.reply_text(uptime_info)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении информации о производительности: {e}")
    finally:
        ssh_client.close()
        
def get_w(update, context):
    try:
        ssh_client = get_ssh_client()
        stdin, stdout, stderr = ssh_client.exec_command('w')
        w_info = stdout.read().decode('utf-8')
        update.message.reply_text(w_info)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении информации о пользователях: {e}")
    finally:
        ssh_client.close()
        
def get_auths(update, context):
    try:
        ssh_client = get_ssh_client()
        stdin, stdout, stderr = ssh_client.exec_command('w')
        auths_info = stdout.read().decode('utf-8')
        update.message.reply_text(auths_info)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении логов входа: {e}")
    finally:
        ssh_client.close()
        
def get_critical(update, context):
    try:
        ssh_client = get_ssh_client()
        stdin, stdout, stderr = ssh_client.exec_command('journalctl -p crit -n 5')
        auths_info = stdout.read().decode('utf-8')
        update.message.reply_text(auths_info)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении критических логов: {e}")
    finally:
        ssh_client.close()
        
def get_ps(update, context):
    try:
        ssh_client = get_ssh_client()
        stdin, stdout, stderr = ssh_client.exec_command('ps')
        processes_info = stdout.read().decode('utf-8')
        update.message.reply_text(processes_info)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении информации о процессах: {e}")
    finally:
        ssh_client.close()  
        
def get_ss(update, context):
    try:
        ssh_client = get_ssh_client()
        stdin, stdout, stderr = ssh_client.exec_command('ss -tulpn')
        ports_info = stdout.read().decode('utf-8')
        update.message.reply_text(ports_info)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении информации об используемых портах: {e}")
    finally:
        ssh_client.close()    
        
def GetAptListCommand(update, context):
    update.message.reply_text(
        "Выберите действие:\n"
        "1 - Вывести все установленные пакеты\n"
        "2 - Найти информацию о конкретном пакете\n"
        "Отправьте номер действия."
    )
    return 'GetAptList'

def list_packages(update, context):
    user_choice = update.message.text
    if user_choice == '1':
        try:
            ssh_client = get_ssh_client()
            stdin, stdout, stderr = ssh_client.exec_command('apt list --installed | head')
            installed_packages = stdout.read().decode('utf-8')
            update.message.reply_text(installed_packages)
        except Exception as e:
            update.message.reply_text(f"Ошибка при получении списка установленных пакетов: {e}")
        finally:
            ssh_client.close()
        return ConversationHandler.END
    elif user_choice == '2':
        update.message.reply_text("Введите название пакета:")
        return "GetAptListName"
    else:
        update.message.reply_text("Неверный выбор. Пожалуйста, отправьте '1' или '2'.")
        return 'GetAptList'
    
def search_package(update, context):
    package_name = update.message.text
    try:
        ssh_client = get_ssh_client()
        stdin, stdout, stderr = ssh_client.exec_command(f'apt list --installed | grep {package_name}')
        package_info = stdout.read().decode('utf-8')
        update.message.reply_text(package_info if package_info else "Пакет не найден.")
    except Exception as e:
        update.message.reply_text(f"Ошибка при поиске информации о пакете: {e}")
    finally:
        ssh_client.close()
    return ConversationHandler.END

def get_services(update, context):
    try:
        ssh_client = get_ssh_client()
        # Команда для получения статуса всех сервисов
        stdin, stdout, stderr = ssh_client.exec_command('service --status-all')
        services_status = stdout.read().decode('utf-8')
        update.message.reply_text(services_status)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении статуса сервисов: {e}")
    finally:
        ssh_client.close()
        
def get_repl_logs(update, context):
    try:
        ssh_client = get_ssh_client()
        stdin, stdout, stderr = ssh_client.exec_command('cat /var/lib/docker/volumes/postgres_logs/_data/* | grep -A 40 "received replication command\|получена команда репликации"')
        logs_status = stdout.read().decode('utf-8')
        update.message.reply_text(logs_status)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении логов: {e}")
    finally:
        ssh_client.close()
        
def get_emails(update, context):
    connection = None
    try:
        connection = get_postgresql_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM emails;")
        data = cursor.fetchall()
        update.message.reply_text("\n".join([str(row) for row in data]))
    except (Exception, Error) as error:
        update.message.reply_text(f"Ошибка при работе с PostgreSQL: {error}")
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
            
            
def get_phonenumbers(update, context):
    connection = None
    try:
        connection = get_postgresql_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phonenumbers;")
        data = cursor.fetchall()
        update.message.reply_text("\n".join([str(row) for row in data]))
    except (Exception, Error) as error:
        update.message.reply_text(f"Ошибка при работе с PostgreSQL: {error}")
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
            
def saveEmailData(update, context):
    user_choice = update.message.text.lower()
    
    if user_choice == 'да':
        try:
            connection = get_postgresql_connection()
            cursor = connection.cursor()
            for email in context.user_data['found_data_emails']:
                cursor.execute("INSERT INTO emails (email) VALUES (%s);", (email,))
                connection.commit()
            update.message.reply_text("email адреса успешно сохранены в базу данных")
        except (Exception, Error) as error:
            update.message.reply_text(f"Ошибка при работе с PostgreSQL: {error}")
    else:
        update.message.reply_text("Отмена сохранения")
        
    return ConversationHandler.END

def savePhoneNumberData(update, context):
    user_choice = update.message.text.lower()
    
    phone_tuples = context.user_data['found_data_phones']
    phoneNumberList = [''.join(t) for t in phone_tuples]
    
    if user_choice == 'да':
        try:
            connection = get_postgresql_connection()
            cursor = connection.cursor()
            for i in range (len(phoneNumberList)):
                cursor.execute("INSERT INTO phonenumbers (phonenumber) VALUES (%s);", (phoneNumberList[i],))
                connection.commit()
            update.message.reply_text("Телефонные номера успешно сохранены в базу данных")
        except (Exception, Error) as error:
            update.message.reply_text(f"Ошибка при работе с PostgreSQL: {error}")
    else:
        update.message.reply_text("Отмена сохранения")
        
    return ConversationHandler.END
                

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Обработчик диалога для поиска email адресов
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'saveEmailData': [MessageHandler(Filters.text & ~Filters.command, saveEmailData)],
        },
        fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.command, cancel)]
    )
    
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'savePhoneData': [MessageHandler(Filters.text & ~Filters.command, savePhoneNumberData)],
    },
    fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.command, cancel)]
    )
    
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
    },
    fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.command, cancel)]
    )
    
    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', GetAptListCommand)],states={
            'GetAptList': [MessageHandler(Filters.text & ~Filters.command, list_packages)],
            'GetAptListName': [MessageHandler(Filters.text & ~Filters.command, search_package)],
        }, 
    fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.command, cancel)]
    )

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("cancel", cancel))
    dp.add_handler(convHandlerFindEmails) 
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(convHandlerGetAptList)
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phonenumbers", get_phonenumbers))
    
    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    
    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()

