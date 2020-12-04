def scroll(SCROLL_PAUSE_TIME, driver):
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    time.sleep(SCROLL_PAUSE_TIME * 2)

from selenium import webdriver
import pypandoc
import telebot
import time
import os
from flask import Flask, request

server = Flask(__name__)

bot = telebot.TeleBot('1450326509:AAEaq_unPJX3BKSTx0QSjZGJMGzmg4oMEDc')

@bot.message_handler(content_types=['text']) 
def get_text_messages(message): 
    if message.text == "Привет": 
        bot.send_message(message.from_user.id, "Привет! Вставьте ссылку на историю из Wattpad для скачивания и я пришлю файл!") 
    elif message.text == "/help": 
        bot.send_message(message.from_user.id, "Я - бот, качающий истории из Wattpad. Если хотите что-то скачать - вставьте ссылку на историю, а я спустя несколько минут пришлю файл в epub-формате.") 
    elif message.text == "/start":
        bot.send_message(message.from_user.id, "Вставьте ссылку на историю из Wattpad для скачивания.")
    elif message.text[0:24]=='https://www.wattpad.com/' or message.text[0:23]=='http://www.wattpad.com/' or message.text[0:16]=='www.wattpad.com/' or message.text[0:12]=='wattpad.com/': 
        input1 = message.text
        bot.send_message(message.from_user.id, "Подождите некоторое время! Скачивание больших работ занимает от 10 минут.")

        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')

        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

        driver.get(input1)
        try:
            main_page = driver.find_elements_by_xpath("//div[@class='cover cover-lg']")
            is_main_page = 2

            try:
                main_page[0]

                ######## MAIN CODE

                is_main_page = 1

                SCROLL_PAUSE_TIME = 1.5
                scroll(SCROLL_PAUSE_TIME, driver)

                main_title1 = driver.find_elements_by_xpath(
                    '//header[@class="background background-lg"]/div[@class="container"]/h1')
                for i in main_title1:
                    main_title = i.text

                titles = []
                chapters = []

                titles.append("# " + main_title + " {epub:type=prologue}")
                description = driver.find_elements_by_xpath('//h2[@class="description"]')
                chapters.append(description[0].text)

                ch_transition = driver.find_elements_by_xpath('//*[@id="story-landing"]/div/div[1]/main/div/div[1]/a')

                for i in ch_transition:
                    driver.get(i.get_attribute("href"))

                t1 = driver.find_elements_by_xpath("//header[@class='panel panel-reading text-center']/h2")
                ch1 = driver.find_elements_by_xpath(
                    "//div[@class='col-xs-10 col-xs-offset-1 col-sm-10 col-sm-offset-1 col-md-7 col-md-offset-1 col-lg-6 col-lg-offset-3 panel panel-reading']/pre/p")
                for i in t1:
                    titles.append("# " + i.text + " {epub:type=prologue}")

                ft = ""
                for i in ch1:
                    not_formatted = str(driver.execute_script("""
                                arguments[0].removeChild(arguments[0].childNodes[arguments[0].childNodes.length - 1]);
                                var fulltext = new String();
                                for (let i = 0; i <= arguments[0].childNodes.length - 2; i++) {
                                    fulltext = fulltext + arguments[0].childNodes[i].textContent;
                                }
                                return fulltext
                                """, i))
                    formatted = not_formatted.replace('\n', '\n\n')
                    ft = ft + formatted

                chapters.append(ft)

                while driver.find_elements_by_xpath('//a[@class="on-navigate next-part-link"]')[0].get_attribute(
                        'textContent') and driver.find_elements_by_xpath('//a[@class="on-navigate next-part-link"]')[
                    0].get_attribute('textContent').strip():
                    next_ch = driver.find_elements_by_xpath('//a[@class="on-navigate next-part-link"]')
                    for j in next_ch:
                        driver.get(j.get_attribute('href'))
                    scroll(SCROLL_PAUSE_TIME, driver)
                    t2 = driver.find_elements_by_xpath("//header[@class='panel panel-reading text-center']/h2")
                    ch2 = driver.find_elements_by_xpath(
                        "//div[@class='col-xs-10 col-xs-offset-1 col-sm-10 col-sm-offset-1 col-md-7 col-md-offset-1 col-lg-6 col-lg-offset-3 panel panel-reading']/pre/p")
                    ctt = ""
                    for k in t2:
                        not_formatted = "# " + k.text + " {epub:type=prologue}"
                        formatted = not_formatted.replace('\n', '\n\n')
                        ctt = ctt + '\n\n' + formatted

                    titles.append(ctt)

                    ftt = ""
                    for k in ch2:
                        not_formatted = str(driver.execute_script("""
                                    arguments[0].removeChild(arguments[0].childNodes[arguments[0].childNodes.length - 1]);
                                    var fulltext = new String();
                                    for (let i = 0; i <= arguments[0].childNodes.length - 2; i++) {
                                        fulltext = fulltext + arguments[0].childNodes[i].textContent;
                                    }
                                    return fulltext
                                    """, k))
                        # not_formatted = k.text
                        formatted = not_formatted.replace('\n', '\n\n')
                        ftt = ftt + '\n\n' + formatted

                    chapters.append(ftt)
                    
                    bot.send_message(message.from_user.id, ftt)
                    bot.send_message(message.from_user.id, "Новая глава есть!")
                    try:
                        driver.find_elements_by_xpath('//a[@class="on-navigate next-part-link"]')[0]
                    except IndexError:
                        break

                full = []
                i = 0
                while i < len(titles):
                    full.append(titles[i])
                    full.append(chapters[i])
                    i = i + 1

                text = "\n\n".join(full)
                text = text.replace(r'\n', '\n')
                output_name = main_title + ".epub"
                title_arg = '--metadata title=' + main_title
            except:
                is_main_page = 0

                SCROLL_PAUSE_TIME = 1.5
                scroll(SCROLL_PAUSE_TIME, driver)

                t1 = driver.find_elements_by_xpath("//header[@class='panel panel-reading text-center']/h2")
                ch1 = driver.find_elements_by_xpath(
                    "//div[@class='col-xs-10 col-xs-offset-1 col-sm-10 col-sm-offset-1 col-md-7 col-md-offset-1 col-lg-6 col-lg-offset-3 panel panel-reading']/pre/p")

                title = ""
                for i in t1:
                    title = i.text

                fr = ""
                for i in ch1:
                    not_formatted = str(driver.execute_script("""
                            arguments[0].removeChild(arguments[0].childNodes[arguments[0].childNodes.length - 1]);
                            var fulltext = new String();
                            for (let i = 0; i <= arguments[0].childNodes.length - 2; i++) {
                                fulltext = fulltext + arguments[0].childNodes[i].textContent;
                            }
                            return fulltext
                            """, i))
                    # not_formatted = str(driver.execute_script('return arguments[0].childNodes[0].nodeValue', i))

                    # not_formatted = i.text
                    formatted = not_formatted.replace('\n', '\n\n')
                    fr = fr + '\n\n' + formatted

                text = fr.replace(r'\n', '\n')
                output_name = title + ".epub"

            try:
                output = pypandoc.convert_text(text, 'epub3', format='md', outputfile=output_name)
            except:
                output = pypandoc.convert_text(text, 'epub3', format='md', outputfile="1.epub")
                output_name = "1.epub"

            file = open(output_name, 'rb')
            bot.send_document(message.chat.id, file)
            if is_main_page == 1:
                bot.send_message(message.from_user.id,
                                 "Если какие-то главы не пропечатались, я могу попробовать сохранить их отдельно в ответ на конкретные ссылки.")
            else:
                bot.send_message(message.from_user.id,
                                 "Если не пропечатались отдельные куски - скорее всего, на сайте произошла ошибка, попробуйте вставить ссылку снова. Если вся глава - скорее всего, у меня почему-то не получается её сохранить.")
            bot.send_message(message.from_user.id,
                             "Если Вам пришел пустой файл, попробуйте снова - на сайте произошла ошибка!")
            file.close()
        except:
            bot.send_message(message.from_user.id, "Произошла ошибка!")
            pass
        driver.quit()


    else:
        bot.send_message(message.from_user.id, "Я не понимаю. Напишите /help.")

bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    server.debug = True
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))