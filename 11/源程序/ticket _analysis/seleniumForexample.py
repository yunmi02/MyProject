import random
import re
import time
from PIL import  Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import chaojiying
from selenium.webdriver import ActionChains #动作链


class Auto_Buy(object):

    def login_12306(self, Username, Password, from_station, to_station, train_date ,checi):
            global bro
            bro = webdriver.Chrome(executable_path = r'C:\Users\yangyang\AppData\Local\Google\Chrome\Application\chromedriver.exe') #加载驱动
            url = 'https://kyfw.12306.cn/otn/login/init' #登录页面URL

            bro.get(url) #打开URL

            time.sleep(2) #休眠两秒

            #录入账号和密码
            Username_tag = bro.find_element_by_id('username')
            Username_tag.send_keys(Username)

            Password_tag = bro.find_element_by_id('password')
            Password_tag.send_keys(Password)

            #验证码
            bro.save_screenshot('./main.png')
            #对截图进行截取获得验证码图片

            #验证码图片的img标签
            code_img_tag = bro.find_element_by_xpath('//*[@id="loginForm"]/div/ul[2]/li[4]/div/div/div[3]/img')
            location = code_img_tag.location #当前标签在当前页面中的左下角坐标
            size = code_img_tag.size #尺寸,字典类型
            # height = size['height']
            # width = size['width']

            #rangle = (int(location['x'])+55, int(location['y'])+65, int(location['x']+size['width'])+158, int(location['y']+size['height'])+120) #此处为%125缩放情况
            rangle = (int(location['x']), int(location['y']), int(location['x']+size['width']), int(location['y']+size['height']))#此处为%100缩放情况

            img = Image.open('./main.png')
            code_img_name = 'ver.png'
            frame = img.crop(rangle)
            frame.save(code_img_name )

            result = chaojiying.Chaojiying_Client.transform_code_img(code_img_name ,9004) #此处是使用打码网站来实现打码
           # print(result)

            all_list = []
            if '|' in result:
                list_1 = result.split('|')
                count_1 = len(list_1)
                for i in range(count_1):
                    xy_list = []
                    x = int(list_1[i].split(',')[0])
                    y = int(list_1[i].split(',')[1])
                    xy_list.append(x)
                    xy_list.append(y)
                    all_list.append(xy_list)
            else:
                xy_list = []
                x = int(result.split(',')[0])
                y = int(result.split(',')[1])
                xy_list.append(x)
                xy_list.append(y)
                all_list.append(xy_list)
           # print(all_list)

            for pos in all_list:
                x = pos[0]
                y = pos[1]
                ActionChains(bro).move_to_element_with_offset(code_img_tag,x,y).click().perform()
                time.sleep(1)

            #登录按钮
            # if bro.find_element_by_xpath('//*[@id="error_msgmypasscode1"]'):
            #     self.login_12306(self, Username, Password, from_station, to_station, train_date ,checi)
            # else:
            bro.find_element_by_id('loginSub').click()

            time.sleep(5)
            self.query_ticket(from_station, to_station, train_date ,checi)



    def query_ticket(self, from_station, to_station, train_date ,checi):
        my_car_list =checi
       # print(my_car_list)

        ticket_url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc'
        train_date = train_date
        bro.get(ticket_url)
        try:
            bro.find_element_by_id("fromStationText").click()
            bro.find_element_by_id("fromStationText").send_keys(Keys.BACKSPACE)
            bro.find_element_by_id("fromStationText").send_keys(from_station)
            bro.find_element_by_id("fromStationText").send_keys(Keys.ENTER)
            bro.find_element_by_id("toStationText").click()
            bro.find_element_by_id("toStationText").send_keys(Keys.BACKSPACE)
            bro.find_element_by_id("toStationText").send_keys(to_station)
            bro.find_element_by_id("toStationText").send_keys(Keys.ENTER)
            js = "var setDate=document.getElementById('train_date');setDate.removeAttribute('readonly');"
            bro.execute_script(js)
            bro.find_element_by_id("train_date").clear()
            bro.find_element_by_id("train_date").send_keys(train_date)
        except:
            pass

        time.sleep(3)
        bro.find_element_by_id("query_ticket").click()
        time.sleep(2)
        ticket_list = []
        ticket = re.findall(r'id="(ticket_\w{10,16})"', bro.page_source) #查找车次所在的tr标签内内的id

        for i in ticket:
            num = re.search('([KGTZD]\d+\w+)', i).group(1)[:-2]
            ticket_list.append(num)
        # print(ticket_list)

        my_ticket = []
        for i in range(len(ticket)):
            for j in my_car_list:
                if j in ticket_list[i]:
                    my_ticket.append(ticket[i])
        print(my_ticket)
        print('111111111')
        return my_ticket

        count_query = 0

    def qiangpiao(self, zuowei,from_station, to_station, train_date ,checi):
        my_ticket = self.query_ticket(from_station, to_station, train_date ,checi)

        if zuowei == 'TZ_':
            for i in my_ticket:
                tic_num = i.split("_")[1]
                print(tic_num)
                print('22222222')
                ger = bro.find_element_by_id(zuowei + tic_num).text
                print(ger)

                if ger.isdigit() or ger == '有':
                    bro.find_element_by_id(i).find_element_by_class_name("btn72").click()
                    time.sleep(1)
                    bro.find_element_by_id("normalPassenger_0").click()
                    time.sleep(1)
                    # 商务座(9),特等座(P),一等座(M),二等座(O),高级软卧(6),软卧(4),硬卧(3),软座(2),硬座(1),无座(1)

                    sel = bro.find_element_by_id("seatType_1" )

                    value_list = []
                    option_list = bro.find_elements_by_css_selector("select#seatType_1 option" )

                    for option_text in option_list:
                                value_list.append(option_text.get_attribute("value"))

                    if 'P' in value_list:
                                print("选择特等座...")
                                Select(sel).select_by_value('P')  # 硬卧

                                print("提交订单...")
                                bro.find_element_by_id("submitOrder_id").click()

                    elif '9' in value_list:
                                print("选择商务座！")
                                Select(sel).select_by_value('9')  # 软卧

                                print("提交订单...")
                                bro.find_element_by_id("submitOrder_id").click()

                elif ger == '候补':
                    count = 0
                    flag = True
                    while flag:
                        bro.find_element_by_id('query_ticket').click()
                        # WebDriverWait(driver, 10).until(lambda the_driver: the_driver.find_element_by_id('t-list').is_displayed())
                        time.sleep(2)
                        count += 1

                        bro.execute_script("window.scrollTo(0,%d)" % (600 + random.randint(0, 100)))
                        if ger.isdigit() or ger == '有':
                            flag = False
                            self.qiangpiao(zuowei,from_station, to_station, train_date ,checi )
                        print("循环点击查询... 第{}次".format(count))
                        time.sleep(2)
        elif zuowei == 'SWZ_':
            for i in my_ticket:
                tic_num = i.split("_")[1]
                print(tic_num)
                ger = bro.find_element_by_id(zuowei + tic_num).text
                print(ger)

                if ger.isdigit() or ger == '有':
                    bro.find_element_by_id(i).find_element_by_class_name("btn72").click()
                    time.sleep(1)
                    bro.find_element_by_id("normalPassenger_0").click()
                    time.sleep(1)
                    # 商务座(9),特等座(P),一等座(M),二等座(O),高级软卧(6),软卧(4),硬卧(3),软座(2),硬座(1),无座(1)

                    sel = bro.find_element_by_id("seatType_1" )

                    value_list = []
                    option_list = bro.find_elements_by_css_selector("select#seatType_1 option" )

                    for option_text in option_list:
                                value_list.append(option_text.get_attribute("value"))

                    if '9' in value_list:
                                print("选择商务座！")
                                Select(sel).select_by_value('9')  # 软卧

                                print("提交订单...")
                                bro.find_element_by_id("submitOrder_id").click()

                elif ger == '候补':
                    count = 0
                    flag = True
                    while flag:
                        bro.find_element_by_id('query_ticket').click()
                        # WebDriverWait(driver, 10).until(lambda the_driver: the_driver.find_element_by_id('t-list').is_displayed())
                        time.sleep(2)
                        count += 1

                        bro.execute_script("window.scrollTo(0,%d)" % (600 + random.randint(0, 100)))
                        if ger.isdigit() or ger == '有':
                            flag = False
                            self.qiangpiao(zuowei,from_station, to_station, train_date ,checi )
                        print("循环点击查询... 第{}次".format(count))
                        time.sleep(2)

        #一等座
        elif zuowei == 'ZY_':
            for i in my_ticket:
                tic_num = i.split("_")[1]

                ger = bro.find_element_by_id(zuowei + tic_num).text

                if ger.isdigit() or ger == '有':
                    bro.find_element_by_id(i).find_element_by_class_name("btn72").click()
                    time.sleep(1)


                    bro.find_element_by_id("normalPassenger_0").click()
                    time.sleep(1)


                    # 商务座(9),特等座(P),一等座(M),二等座(O),高级软卧(6),软卧(4),硬卧(3),软座(2),硬座(1),无座(1)

                    sel = bro.find_element_by_id("seatType_1" )

                    value_list = []
                    option_list = bro.find_elements_by_css_selector("select#seatType_1 option" )

                    for option_text in option_list:
                                value_list.append(option_text.get_attribute("value"))

                    if 'M' in value_list:
                                print("选择一等座...")
                                Select(sel).select_by_value('M')  # 硬卧

                                print("提交订单...")
                                bro.find_element_by_id("submitOrder_id").click()


                else:
                    count = 0
                    flag = True
                    while flag:
                        bro.find_element_by_id('query_ticket').click()
                        # WebDriverWait(driver, 10).until(lambda the_driver: the_driver.find_element_by_id('t-list').is_displayed())
                        time.sleep(2)
                        count += 1
                        print("循环点击查询... 第{}次".format(count))
                        bro.execute_script("window.scrollTo(0,%d)" % (600 + random.randint(0, 100)))
                        if ger.isdigit() or ger == '有':
                            flag = False
                            self.qiangpiao(zuowei, from_station, to_station, train_date, checi)
                        time.sleep(2)


        #二等座
        elif zuowei == 'ZE_':
            for i in my_ticket:
                tic_num = i.split("_")[1]

                ger = bro.find_element_by_id(zuowei + tic_num).text

                if ger.isdigit() or ger == '有':
                    bro.find_element_by_id(i).find_element_by_class_name("btn72").click()
                    time.sleep(3)

                    #bro.find_element_by_id("normalPassenger_0").click()
                    bro.find_element_by_xpath('//*[@id="normalPassenger_0"]').click()
                    time.sleep(1)

                    # 商务座(9),特等座(P),一等座(M),二等座(O),高级软卧(6),软卧(4),硬卧(3),软座(2),硬座(1),无座(1)

                    sel = bro.find_element_by_id("seatType_1")

                    value_list = []
                    option_list = bro.find_elements_by_css_selector("select#seatType_1 option")

                    for option_text in option_list:
                        value_list.append(option_text.get_attribute("value"))

                    if 'O' in value_list:
                        print("选择二等座...")
                        Select(sel).select_by_value('O')  # 硬卧

                        print("提交订单...")
                        bro.find_element_by_id("submitOrder_id").click()


                else:
                    count = 0
                    flag = True
                    while flag:
                        if ger.isdigit() or ger == '有':
                            flag = False
                            self.qiangpiao(zuowei, from_station, to_station, train_date, checi)
                        bro.find_element_by_id('query_ticket').click()
                        # WebDriverWait(driver, 10).until(lambda the_driver: the_driver.find_element_by_id('t-list').is_displayed())
                        time.sleep(2)
                        count += 1
                        print("循环点击查询... 第{}次".format(count))
                        bro.execute_script("window.scrollTo(0,%d)" % (600 + random.randint(0, 100)))

                        time.sleep(2)
        #高级软卧
        elif zuowei == 'GR_':
            for i in my_ticket:
                tic_num = i.split("_")[1]

                ger = bro.find_element_by_id(zuowei + tic_num).text

                if ger.isdigit() or ger == '有':
                    bro.find_element_by_id(i).find_element_by_class_name("btn72").click()
                    time.sleep(1)

                    bro.find_element_by_id("normalPassenger_0").click()
                    time.sleep(1)

                    # 商务座(9),特等座(P),一等座(M),二等座(O),高级软卧(6),软卧(4),硬卧(3),软座(2),硬座(1),无座(1)

                    sel = bro.find_element_by_id("seatType_1")

                    value_list = []
                    option_list = bro.find_elements_by_css_selector("select#seatType_1 option")

                    for option_text in option_list:
                        value_list.append(option_text.get_attribute("value"))

                    if '6' in value_list:
                        print("选择高级软卧...")
                        Select(sel).select_by_value('6')  # 硬卧

                        print("提交订单...")
                        bro.find_element_by_id("submitOrder_id").click()

                else:
                    count = 0
                    flag = True
                    while flag:
                        bro.find_element_by_id('query_ticket').click()
                        # WebDriverWait(driver, 10).until(lambda the_driver: the_driver.find_element_by_id('t-list').is_displayed())
                        time.sleep(2)
                        count += 1
                        print("循环点击查询... 第{}次".format(count))
                        bro.execute_script("window.scrollTo(0,%d)" % (600 + random.randint(0, 100)))
                        if ger.isdigit() or ger == '有':
                            flag = False
                            self.qiangpiao(zuowei, from_station, to_station, train_date, checi)
                        time.sleep(2)

        elif zuowei == 'RW_':
            for i in my_ticket:
                tic_num = i.split("_")[1]

                ger = bro.find_element_by_id(zuowei + tic_num).text

                if ger.isdigit() or ger == '有':
                    bro.find_element_by_id(i).find_element_by_class_name("btn72").click()
                    time.sleep(1)

                    bro.find_element_by_id("normalPassenger_0").click()
                    time.sleep(1)

                    # 商务座(9),特等座(P),一等座(M),二等座(O),高级软卧(6),软卧(4),硬卧(3),软座(2),硬座(1),无座(1)

                    sel = bro.find_element_by_id("seatType_1")

                    value_list = []
                    option_list = bro.find_elements_by_css_selector("select#seatType_1 option")

                    for option_text in option_list:
                        value_list.append(option_text.get_attribute("value"))

                    if '4' in value_list:
                        print("选择软卧...")
                        Select(sel).select_by_value('4')  # 硬卧

                        print("提交订单...")
                        bro.find_element_by_id("submitOrder_id").click()
                else:
                    count = 0
                    flag = True
                    while flag:
                        bro.find_element_by_id('query_ticket').click()
                        # WebDriverWait(driver, 10).until(lambda the_driver: the_driver.find_element_by_id('t-list').is_displayed())
                        time.sleep(2)
                        count += 1
                        print("循环点击查询... 第{}次".format(count))
                        bro.execute_script("window.scrollTo(0,%d)" % (600 + random.randint(0, 100)))
                        if ger.isdigit() or ger == '有':
                            flag = False
                            self.qiangpiao(zuowei, from_station, to_station, train_date, checi)
                        time.sleep(2)
        elif zuowei == 'YW_':
            for i in my_ticket:
                tic_num = i.split("_")[1]

                ger = bro.find_element_by_id(zuowei + tic_num).text

                if ger.isdigit() or ger == '有':
                    bro.find_element_by_id(i).find_element_by_class_name("btn72").click()
                    time.sleep(1)

                    bro.find_element_by_id("normalPassenger_0").click()
                    time.sleep(1)

                    # 商务座(9),特等座(P),一等座(M),二等座(O),高级软卧(6),软卧(4),硬卧(3),软座(2),硬座(1),无座(1)

                    sel = bro.find_element_by_id("seatType_1")

                    value_list = []
                    option_list = bro.find_elements_by_css_selector("select#seatType_1 option")

                    for option_text in option_list:
                        value_list.append(option_text.get_attribute("value"))

                    if '3' in value_list:
                        print("选择硬卧...")
                        Select(sel).select_by_value('3')  # 硬卧

                        print("提交订单...")
                        bro.find_element_by_id("submitOrder_id").click()
                else:
                    count = 0
                    flag = True
                    while flag:
                        bro.find_element_by_id('query_ticket').click()
                        # WebDriverWait(driver, 10).until(lambda the_driver: the_driver.find_element_by_id('t-list').is_displayed())
                        time.sleep(2)
                        count += 1
                        print("循环点击查询... 第{}次".format(count))
                        bro.execute_script("window.scrollTo(0,%d)" % (600 + random.randint(0, 100)))
                        if ger.isdigit() or ger == '有':
                            flag = False
                            self.qiangpiao(zuowei, from_station, to_station, train_date, checi)
                        time.sleep(2)


        elif zuowei == 'RZ_':
            for i in my_ticket:
                tic_num = i.split("_")[1]

                ger = bro.find_element_by_id(zuowei + tic_num).text

                if ger.isdigit() or ger == '有':
                    bro.find_element_by_id(i).find_element_by_class_name("btn72").click()
                    time.sleep(1)

                    bro.find_element_by_id("normalPassenger_0").click()
                    time.sleep(1)

                    # 商务座(9),特等座(P),一等座(M),二等座(O),高级软卧(6),软卧(4),硬卧(3),软座(2),硬座(1),无座(1)

                    sel = bro.find_element_by_id("seatType_1")

                    value_list = []
                    option_list = bro.find_elements_by_css_selector("select#seatType_1 option")

                    for option_text in option_list:
                        value_list.append(option_text.get_attribute("value"))

                    if '2' in value_list:
                        print("选择软座...")
                        Select(sel).select_by_value('2')  # 硬卧

                        print("提交订单...")
                        bro.find_element_by_id("submitOrder_id").click()
                else:
                    count = 0
                    flag = True
                    while flag:
                        if ger.isdigit() or ger == '有':
                            flag = False
                            self.qiangpiao(zuowei, from_station, to_station, train_date, checi)
                        bro.find_element_by_id('query_ticket').click()
                        # WebDriverWait(driver, 10).until(lambda the_driver: the_driver.find_element_by_id('t-list').is_displayed())
                        time.sleep(2)
                        count += 1
                        print("循环点击查询... 第{}次".format(count))
                        bro.execute_script("window.scrollTo(0,%d)" % (600 + random.randint(0, 100)))

                        time.sleep(2)

        elif zuowei == 'YZ_':
            for i in my_ticket:
                tic_num = i.split("_")[1]

                ger = bro.find_element_by_id(zuowei + tic_num).text

                if ger.isdigit() or ger == '有':
                    bro.find_element_by_id(i).find_element_by_class_name("btn72").click()
                    time.sleep(1)

                    bro.find_element_by_id("normalPassenger_0").click()
                    time.sleep(1)

                    # 商务座(9),特等座(P),一等座(M),二等座(O),高级软卧(6),软卧(4),硬卧(3),软座(2),硬座(1),无座(1)

                    sel = bro.find_element_by_id("seatType_1")

                    value_list = []
                    option_list = bro.find_elements_by_css_selector("select#seatType_1 option")

                    for option_text in option_list:
                        value_list.append(option_text.get_attribute("value"))

                    if '1' in value_list:
                        print("选择硬座...")
                        Select(sel).select_by_value('1')  # 硬卧

                        print("提交订单...")
                        bro.find_element_by_id("submitOrder_id").click()
                else:
                    count = 0
                    flag = True
                    while flag:
                        bro.find_element_by_id('query_ticket').click()
                        # WebDriverWait(driver, 10).until(lambda the_driver: the_driver.find_element_by_id('t-list').is_displayed())
                        time.sleep(2)
                        count += 1
                        print("循环点击查询... 第{}次".format(count))
                        bro.execute_script("window.scrollTo(0,%d)" % (600 + random.randint(0, 100)))
                        if ger.isdigit() or ger == '有':
                            flag = False
                            self.qiangpiao(zuowei, from_station, to_station, train_date, checi)
                        time.sleep(2)
        else:
            for i in my_ticket:
                bro.find_element_by_id(i).find_element_by_class_name("btn72").click()
                time.sleep(1)
                bro.find_element_by_id("normalPassenger_0").click()
                time.sleep(1)
                bro.find_element_by_id("submitOrder_id").click()
                time.sleep(1)
    













