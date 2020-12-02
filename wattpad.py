from selenium import webdriver
import json
import pypandoc
import telebot
import requests  
#import datetime

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
        input1=message.text
        bot.send_message(message.from_user.id, "Подождите несколько минут!")

        #GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google_chrome'
        #CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'

        #chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument('--disable-gpu')
        #chrome_options.add_argument('--no-sandbox')
        #chrome_options.binary_location = GOOGLE_CHROME_PATH

        #driver = webdriver.Chrome(execution_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)

        driver = webdriver.PhantomJS()

        #chromedriver = "C:\programs\chromedriver.exe"
        #driver = webdriver.Chrome(chromedriver)

        #while input1[0:24]!='https://www.wattpad.com/' and input1[0:23]!='http://www.wattpad.com/' and input1[0:16]!='www.wattpad.com/' and input1[0:12]!='wattpad.com/':
        #   input1 = input("Введена некорректная ссылка! Скопируйте в окне браузера и вставьте в текстовое поле бота.")

        driver.get(input1)
        #driver.get('https://www.wattpad.com/story/47855929-%D1%96%D0%B2%D0%B0%D0%BD-%D0%BA%D0%B0%D1%80%D0%BF%D0%BE%D0%B2%D0%B8%D1%87-%D0%BA%D0%B0%D1%80%D0%BF%D0%B5%D0%BD%D0%BA%D0%BE-%D0%BA%D0%B0%D1%80%D0%B8%D0%B9-%D0%BC%D0%B0%D1%80%D1%82%D0%B8%D0%BD-%D0%B1%D0%BE%D1%80%D1%83%D0%BB%D1%8F')

        main_title1 = driver.find_elements_by_xpath('//header[@class="background background-lg"]/div[@class="container"]/h1')
        for i in main_title1:
            main_title = i.text

        titles = []
        chapters = []

        titles.append("# "+ main_title + " {epub:type=prologue}")
        description = driver.find_elements_by_xpath('//h2[@class="description"]')
        chapters.append(description[0].text)

        ch_transition = driver.find_elements_by_xpath('//*[@id="story-landing"]/div/div[1]/main/div/div[1]/a')

        for i in ch_transition:
            driver.get(i.get_attribute("href"))

        t1 = driver.find_elements_by_xpath("//header[@class='panel panel-reading text-center']/h2")
        ch1 = driver.find_elements_by_xpath("//div[@class='col-xs-10 col-xs-offset-1 col-sm-10 col-sm-offset-1 col-md-7 col-md-offset-1 col-lg-6 col-lg-offset-3 panel panel-reading' and @class!='num-comment' and @class!='comment-marker on-inline-comments-modal']")
        for i in t1:
            titles.append("# "+ i.text + " {epub:type=prologue}")
        for i in ch1:
            chapters.append(i.text)
            bot.send_message(message.from_user.id, i.text)

        bot.send_message(message.from_user.id, "Первая глава есть!")

        while driver.find_elements_by_xpath('//a[@class="on-navigate next-part-link"]')[0].get_attribute('textContent') and driver.find_elements_by_xpath('//a[@class="on-navigate next-part-link"]')[0].get_attribute('textContent').strip():
            next_ch = driver.find_elements_by_xpath('//a[@class="on-navigate next-part-link"]')
            for j in next_ch:
                driver.get(j.get_attribute('href'))
            t2 = driver.find_elements_by_xpath("//header[@class='panel panel-reading text-center']/h2")
            ch2 = driver.find_elements_by_xpath("//div[@class='col-xs-10 col-xs-offset-1 col-sm-10 col-sm-offset-1 col-md-7 col-md-offset-1 col-lg-6 col-lg-offset-3 panel panel-reading' and @class!='num-comment' and @class!='comment-marker on-inline-comments-modal']")
            for k in t2:
                not_formatted = "# "+ k.text + " {epub:type=prologue}"
                formatted = not_formatted.replace('\n', '\n\n')
                titles.append(formatted)

                bot.send_message(message.from_user.id, formatted)
                bot.send_message(message.from_user.id, "Новая глава есть!")
            for m in ch2:
                not_formatted = m.text
                formatted = not_formatted.replace('\n', '\n\n')
                print(formatted)
                chapters.append(formatted)
            try:
                driver.find_elements_by_xpath('//a[@class="on-navigate next-part-link"]')[0]
            except IndexError:
                break

        bot.send_message(message.from_user.id, "Уже в конце!")

        full = []
        i = 0
        while i < len(titles):
            full.append(titles[i])
            full.append(chapters[i])
            i = i+1

        text = "\n\n".join(full)
        text = text.replace(r'\n', '\n')
        output_name = main_title + ".epub"
        title_arg = '--metadata title=' + main_title
        
        try:
            output = pypandoc.convert_text(text, 'epub3', format='md', outputfile=output_name)
        except:
            output = pypandoc.convert_text(text, 'epub3', format='md', outputfile="1.epub")
            output_name="1.epub"
            

        driver.quit()

        file = open(output_name, 'rb')
        bot.send_document(message.chat.id, file)
        file.close()
    else:
        bot.send_message(message.from_user.id, "Я не понимаю. Напишите /help.")

bot.polling(none_stop=True, interval=0)