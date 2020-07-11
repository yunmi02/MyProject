import json
import os

import pandas as pd
import requests
import xlrd
import xlwt
from xlutils.copy import copy
from get_stations import *
from show_window import *

'''5-7 目的地 3  车次 6  出发地 8  出发时间 9  到达时间 10 历时 26 无坐 29 硬座
   24 软座 28 硬卧 33 动卧 23 软卧 21 高级软卧 30 二等座 31 一等座 32 商务座特等座
'''

data = []  # 用于保存整理好的车次信息
price_data = []#用于保存高铁票价
type_data = []  # 保存车次分类后最后的数据
sess = requests.session() #建立会话，保持cookie，由于每次登陆cookie值会发生变化导致爬取失败，所以要使用同一个cookie值
kv = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
    }
def query(date, from_station, to_station): #查询所有车票信息
    data.clear()  # 清空数据
    type_data.clear()  # 清空车次分类保存的数据
    # 查询请求地址
    sess.cookies.update(
        {
            'RAIL_EXPIRATION': '1569132689668',
            'RAIL_DEVICEID': 'Ry6Q7Tkau6lvtQFj-1-qD3Mrde9MOKac4kGC5MCLRvgQ5ADb2vySV_SptrTnvjckvQxVWcocw7621ci-T2TmMlg4pChroHuQoXvciR1XyZ52i4ZSiS_dClAx8x_Ck3tg_4or7LxX15-nWH7ilOFn53WcrBup-bN8',
            'route': 'c5c62a339e7744272a54643b3be5bf64'
        }
    )

    params = {
        'leftTicketDTO.train_date': date,
        'leftTicketDTO.from_station': from_station,
        'leftTicketDTO.to_station': to_station,
        'purpose_codes': 'ADULT'
    }
    ticket_url = 'https://kyfw.12306.cn/otn/leftTicket/query?'

    # 发送查询请求

    ticket = sess.get(url=ticket_url, headers=kv, params=params).content.decode('utf_8')
    # print(type(ticket))
    # print(type(ticket))
    # print('11111111111111111111111')
    # # 将json数据转换为字典类型，通过键值对取数据
    ticket =json.loads(ticket)
    # print(type(ticket))
    # print(ticket)
    ticket_list = ticket['data']['result']
    # print('11111111111111111111111')
    # print(type(ticket_list))
    # print(ticket_list)
    # print(ticket_list)
    # 判断车站文件是否存在
    if is_stations('stations.text') == True:
        stations = eval(read('stations.text'))  # 读取所有车站并转换为dic类型
        if len(ticket_list) != 0:  # 判断返回数据是否为空
            for i in ticket_list:
                # # 分割数据并添加到列表中
                tmp_list = i.split('|')
                # 因为查询结果中出发站和到达站为站名的缩写字母，所以需要在车站库中找到对应的车站名称
                from_station = list(stations.keys())[list(stations.values()).index(tmp_list[6])]
                to_station = list(stations.keys())[list(stations.values()).index(tmp_list[7])]

                # 车次
                train_num = tmp_list[3]
                #print(train_num)
                # 出发时间
                start_time = tmp_list[8]
                # 到达时间
                arrive_time = tmp_list[9]
                # 历时
                took_time = tmp_list[10]

                # 商务座
                business = tmp_list[32] or tmp_list[25]
                # 一等座
                first = tmp_list[31]
                # 二等座
                second = tmp_list[30]
                # 高级软卧
                high_soft_sleeper = tmp_list[21]
                # 软卧
                soft_sleeper = tmp_list[23]
                # 动卧
                act_sleeper = tmp_list[27]
                # 硬卧
                hard_sleeper = tmp_list[28]
                # 软座
                soft_seat = tmp_list[24]
                # 硬座
                hard_seat = tmp_list[29]
                # 无座
                no_seat = tmp_list[26]
                # 备注
                remark = tmp_list[1]

                # 创建座位数组，由于返回的座位数据中含有空既“”，所以将空改成--这样好识别
                seat = [train_num, from_station, to_station,start_time ,arrive_time,took_time
                    , business , first, second,  high_soft_sleeper
                    , soft_sleeper , act_sleeper , hard_sleeper , soft_seat, hard_seat, no_seat, remark]


                newSeat = []
                # 循环将座位信息中的空既“”，改成--这样好识别,遍历列表seat[]
                for s in seat:
                    if s == "":
                        s = "--"
                    if s == '24:00' or s == '99:59':
                        s = "--"
                    if s == '列车停运':
                        s = '停运'
                    else:
                        s = s
                    newSeat.append(s)  # 保存新的座位信息
                data.append(newSeat)
        # print(data[0])
        return data  # 返回整理好的车次信息

def query_price(date, from_station, to_station): #查询所有车票信息
    price_data.clear()  # 清空数据
    # 查询请求地址
    # sess.cookies.update(
    #     {
    #         'RAIL_EXPIRATION': '1569132689668',
    #         'RAIL_DEVICEID': 'Ry6Q7Tkau6lvtQFj-1-qD3Mrde9MOKac4kGC5MCLRvgQ5ADb2vySV_SptrTnvjckvQxVWcocw7621ci-T2TmMlg4pChroHuQoXvciR1XyZ52i4ZSiS_dClAx8x_Ck3tg_4or7LxX15-nWH7ilOFn53WcrBup-bN8',
    #         'route': 'c5c62a339e7744272a54643b3be5bf64'
    #     }
    # )

    params = {
        'leftTicketDTO.train_date': date,
        'leftTicketDTO.from_station': from_station,
        'leftTicketDTO.to_station': to_station,
        'purpose_codes': 'ADULT'
    }
    ticket_price_url = 'https://kyfw.12306.cn/otn/leftTicketPrice/queryAllPublicPrice?'

    # 发送查询请求

    ticket_price = sess.get(url=ticket_price_url, headers=kv, params=params).content.decode('utf_8')
    # # 将json数据转换为字典类型，通过键值对取数据
    ticket_price =json.loads(ticket_price)
    # print(ticket_price)

    train_price_list = []
    sss = ticket_price['data']
    # 判断车站文件是否存在
    if is_stations('stations.text') == True:
        stations = eval(read('stations.text'))  # 读取所有车站并转换为dic类型
        if len(sss) != 0:  # 判断返回数据是否为空
            for i in range(len(sss)):
                train_price_list.append(ticket_price['data'][i]['queryLeftNewDTO']) #此处为字典类型
            print(train_price_list[0])
            for k in train_price_list:
                # print(k['station_train_code'])
                # 列车编号
                train_num = k['station_train_code']

                # print(k.get('swz_price'))


                # 始发站
                from_station = k['from_station_name']

                # 终点站
                to_station = k['to_station_name']

                # 出发时间
                start_time = k['start_time']

                # 到达时间
                arrive_time = k['arrive_time']

                # 历时
                took_time = k['lishi']
                    
                # 商务座价格
                if k.get('swz_price') == None:
                    business_price = '--'
                else:
                    business_price=k['swz_price'][:4].lstrip('0') + '.' + k['swz_price'][4:]





                # 特等座价格
                if k.get('tz_price') == None:
                    special_price = '--'

                else:
                    special_price = k['tz_price'][:4].lstrip('0') + '.' + k['tz_price'][4:]

                # 一等座价格
                if k.get('zy_price') == None:
                    first_price = '--'
                else:
                    first_price = k['zy_price'][:4].lstrip('0') + '.' + k['zy_price'][4:]

                # 二等座价格
                if k.get('ze_price') == None:
                    second_price = '--'
                else:
                    second_price = k['ze_price'][:4].lstrip('0') + '.' + k['ze_price'][4:]

                # print(second_price)
                
                # 高级软卧
                high_soft_sleeper = '--'

                # 软卧
                soft_sleeper = '--'

                # 动卧
                act_sleeper = '--'

                # 硬卧
                hard_sleeper = '--'

                # 软座
                soft_seat = '--'

                # 硬座
                hard_seat = '--'

                # 无座
                no_seat = '--'

                # others
                other = '--'
                # 备注
                remark = '--'

                seat_price = [train_num, from_station, to_station, start_time, arrive_time, took_time,business_price
                    , special_price, first_price, second_price, high_soft_sleeper
                    , soft_sleeper, act_sleeper, hard_sleeper, soft_seat, hard_seat, no_seat, other, remark]
                newprice = []
                # 循环将座位信息中的空既“”，改成--这样好识别,遍历列表seat[]
                for s in seat_price:
                    if s == "--.":
                        s = "--"
                    else:
                        s = s
                    # print(s)
                    newprice.append(s)  # 保存新的座位信息
                price_data .append(newprice)
                # print(data[0])
        return price_data   # 返回整理好的车次信息


def data_write(file_path, datas):
    f = xlwt.Workbook()
    sheet1 = f.add_sheet(u'sheet1', cell_overwrite_ok=False)  # 创建sheet

    # 将数据写入第 i 行，第 j 列
    i = 0
    for data in datas:
        for j in range(len(data)):
            sheet1.write(i, j, data[j])
        i = i + 1
    f.save(file_path)
    messageDialog('成功', '已保存！')


def write_excel_xls_append(path, value):
    index = len(value)  # 获取需要写入数据的行数
    if os.path.exists(path):
        workbook = xlrd.open_workbook(path)
    else:
        data_write(path, value)
    sheets = workbook.sheet_names()  # 获取工作簿中的所有表格
    worksheet = workbook.sheet_by_name(sheets[0])  # 获取工作簿中所有表格中的的第一个表格
    rows_old = worksheet.nrows  # 获取表格中已存在的数据的行数
    new_workbook = copy(workbook)  # 将xlrd对象拷贝转化为xlwt对象
    new_worksheet = new_workbook.get_sheet(0)  # 获取转化后工作簿中的第一个表格
    for i in range(0, index):
        for j in range(0, len(value[i])):
            new_worksheet.write(i+rows_old, j, value[i][j])  # 追加写入数据，注意是从i+rows_old行开始写入
    new_workbook.save(path)  # 保存工作簿
    frame = pd.DataFrame(pd.read_excel(path))
    if '车次' in frame.columns:
        frame.to_excel(path, index=None)

    else:
        frame2 = pd.DataFrame(pd.read_excel(path,header=None))
        frame2.columns = ['车次', '始发站', '终点站', '出发时间', '到达时间', '历时', '商务座', '一等座', '二等座', '高级软卧', '软卧', '硬卧', '动卧', '软座',
                   '硬座', '无座', '备注', '时间']
        frame2.to_excel(path, index=None)
        # frame= frame.drop_duplicates(['车次', '始发站', '终点站', '出发时间', '到达时间', '历时', '商务座', '一等座', '二等座','高级软卧', '软卧', '硬卧', '动卧', '软座', '硬座', '无座', '备注', '时间'], keep='first',inplace=False)

    messageDialog('成功', '已保存！')

def write_price_excel_xls_append(path, value):
    index = len(value)  # 获取需要写入数据的行数
    if os.path.exists(path):
        workbook = xlrd.open_workbook(path)
    else:
        data_write(path, value)
    sheets = workbook.sheet_names()  # 获取工作簿中的所有表格
    worksheet = workbook.sheet_by_name(sheets[0])  # 获取工作簿中所有表格中的的第一个表格
    rows_old = worksheet.nrows  # 获取表格中已存在的数据的行数
    new_workbook = copy(workbook)  # 将xlrd对象拷贝转化为xlwt对象
    new_worksheet = new_workbook.get_sheet(0)  # 获取转化后工作簿中的第一个表格
    for i in range(0, index):
        for j in range(0, len(value[i])):
            new_worksheet.write(i+rows_old, j, value[i][j])  # 追加写入数据，注意是从i+rows_old行开始写入
    new_workbook.save(path)  # 保存工作簿
    messageDialog('成功', '已保存！')

# 获取高铁信息的方法
def g_vehicle():
    if len(data) != 0:
        for g in data:  # 循环所有火车数据
              # 判断车次首字母是不是高铁
            if g[0].startswith('G'):  # 如果是将该条信息添加到高铁数据中
                type_data.append(g)


# 移除高铁信息的方法
def r_g_vehicle():
    if len(data) != 0 and len(type_data) != 0:
        for g in data:
            if g[0].startswith('G'):  # 移除高铁信息
                type_data.remove(g)


# 获取动车信息的方法
def d_vehicle():
    if len(data) != 0:
        for d in data:  # 循环所有火车数据
            i = d[0].startswith('D')  # 判断车次首字母是不是动车
            if i == True:  # 如果是将该条信息添加到动车数据中
                type_data.append(d)


# 移除动车信息的方法
def r_d_vehicle():
    if len(data) != 0 and len(type_data) != 0:
        for d in data:
            i = d[0].startswith('D')
            if i == True:  # 移除动车信息
                type_data.remove(d)


# 获取直达车信息的方法
def z_vehicle():
    if len(data) != 0:
        for z in data:  # 循环所有火车数据
            i = z[0].startswith('Z')  # 判断车次首字母是不是直达
            if i == True:  # 如果是将该条信息添加到直达数据中
                type_data.append(z)


# 移除直达车信息的方法
def r_z_vehicle():
    if len(data) != 0 and len(type_data) != 0:
        for z in data:
            i = z[0].startswith('Z')
            if i == True:  # 移除直达车信息
                type_data.remove(z)


# 获取特快车信息的方法
def t_vehicle():
    if len(data) != 0:
        for t in data:  # 循环所有火车数据
            i = t[0].startswith('T')  # 判断车次首字母是不是特快
            if i == True:  # 如果是将该条信息添加到特快车数据中
                type_data.append(t)


# 移除特快车信息的方法
def r_t_vehicle():
    if len(data) != 0 and len(type_data) != 0:
        for t in data:
            i = t[0].startswith('T')
            if i == True:  # 移除特快车信息
                type_data.remove(t)


# 获取快速车数据的方法
def k_vehicle():
    if len(data) != 0:
        for k in data:  # 循环所有火车数据
            i = k[0].startswith('K')  # 判断车次首字母是不是快车
            if i == True:  # 如果是将该条信息添加到快车数据中
                type_data.append(k)


# 移除快速车数据的方法
def r_k_vehicle():
    if len(data) != 0 and len(type_data) != 0:
        for k in data:
            i = k[0].startswith('K')
            if i == True:  # 移除快车信息
                type_data.remove(k)




'''5-7 目的地 3  车次 6  出发地 8  出发时间 9  到达时间 10 历时 26 无坐 29 硬座
   24 软座 28 硬卧 33 动卧 23 软卧 21 高级软卧 30 二等座 31 一等座 32 商务座特等座
'''

today_car_list = []  # 保存今天列车信息，已经处理是否有票
two_car_list   = []  # 保存二天列车信息，已经处理是否有票
three_car_list = []  # 保存三天列车信息，已经处理是否有票
four_car_list  = []  # 保存四天列车信息，已经处理是否有票
five_car_list  = []  # 保存五天列车信息，已经处理是否有票

today_list = []  # 保存今天列车信息，未处理
two_list   = []  # 保存二天列车信息，未处理
three_list = []  # 保存三天列车信息，未处理
four_list =  []  # 保存四天列车信息，未处理
five_list  = []  # 保存五天列车信息，未处理


# 查询卧铺售票分析数据
#date：日期
#witch_day:1表示当天信息，3第三天信息，5表示第五天信息
def query_ticketing_analysis(date, from_station, to_station, which_day):
    # 查询请求地址
    sess.cookies.update(
        {
            'RAIL_EXPIRATION': '1569132689668',
            'RAIL_DEVICEID': 'Ry6Q7Tkau6lvtQFj-1-qD3Mrde9MOKac4kGC5MCLRvgQ5ADb2vySV_SptrTnvjckvQxVWcocw7621ci-T2TmMlg4pChroHuQoXvciR1XyZ52i4ZSiS_dClAx8x_Ck3tg_4or7LxX15-nWH7ilOFn53WcrBup-bN8',
            'route': 'c5c62a339e7744272a54643b3be5bf64'
        }
    )
    ticket_url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
        date, from_station, to_station)
    # 发送查询请求
    result = sess.get(url=ticket_url, headers=kv).content.decode('utf_8')
    # # 将json数据转换为字典类型，通过键值对取数据
    result = json.loads(result)
    result = result['data']['result']

    # 判断车站文件是否存在
    if is_stations('stations.text') == True:
        stations = eval(read('stations.text'))  # 读取所有车站并转换为dic类型
        if len(result) != 0:  # 判断返回数据是否为空
            for i in result:
                # # 分割数据并添加到列表中
                tmp_list = i.split('|')
                # 车次
                train_num = tmp_list[3]
                # print(train_num)
                # 出发时间
                start_time = tmp_list[8]
                # 到达时间
                arrive_time = tmp_list[9]
                # 历时
                took_time = tmp_list[10]
                # 高级软卧
                high_soft_sleeper = tmp_list[21]
                # 软卧
                soft_sleeper = tmp_list[23]
                # 硬卧
                hard_sleeper = tmp_list[28]
                # 备注
                remark = tmp_list[1]
                # 因为查询结果中出发站和到达站为站名的缩写字母，所以需要在车站库中找到对应的车站名称
                from_station = list(stations.keys())[list(stations.values()).index(tmp_list[6])]
                to_station = list(stations.keys())[list(stations.values()).index(tmp_list[7])]

                # 创建座位数组，其中包含高级软卧、软卧、硬卧
                if remark == '预订':
                    seat = [train_num, from_station, to_station, start_time, arrive_time, took_time, high_soft_sleeper,
                            soft_sleeper, hard_sleeper]
                    if which_day == 1:  # 判断今天的车次信息
                        if seat[0].startswith('G') == False and seat[0].startswith('D') == False and seat[0].startswith('C') == False:# 将高铁、动、C开头的车次，排除
                            today_list.append(seat)                                   # 将高级软卧、软卧、硬卧未处理信息添加至列表中
                            new_seat = is_ticket(tmp_list, from_station, to_station)  # 判断某车次是否有票
                            today_car_list.append(new_seat)                           # 将判断后的车次信息(已处理)添加至对应的列表当中

                    if which_day == 2:  # 判断今天的车次信息
                        # 将高铁、动、C开头的车次，排除
                        if seat[0].startswith('G') == False and seat[0].startswith('D') == False and seat[0].startswith('C') == False:
                            two_list.append(seat)  # 将高级软卧、软卧、硬卧未处理信息添加至列表中
                            new_seat = is_ticket(tmp_list, from_station, to_station)  # 判断某车次是否有票
                            two_car_list.append(new_seat)  # 将判断后的车次信息(已处理)添加至对应的列表当中

                    if which_day == 3:  # 判断三天的车次信息
                                        # 将高铁、动、C开头的车次，排除
                        if seat[0].startswith('G') == False and seat[0].startswith('D') == False and seat[0].startswith('C') == False:
                            three_list.append(seat)                                   #将高级软卧、软卧、硬卧未处理信息添加至列表中，用于处理折线图
                            new_seat = is_ticket(tmp_list, from_station, to_station)  # 判断某车次是否有票
                            three_car_list.append(new_seat)                           # 将判断后的车次信息(已处理)添加至对应的列表当中

                    if which_day == 4:  # 判断今天的车次信息
                        # 将高铁、动、C开头的车次，排除
                        if seat[0].startswith('G') == False and seat[0].startswith('D') == False and seat[0].startswith(
                                'C') == False:
                            four_list.append(seat)  # 将高级软卧、软卧、硬卧未处理信息添加至列表中
                            new_seat = is_ticket(tmp_list, from_station, to_station)  # 判断某车次是否有票
                            four_car_list.append(new_seat)  # 将判断后的车次信息(已处理)添加至对应的列表当中

                    if which_day == 5:  # 判断五天的车次信息
                                        # 将高铁、动、C开头的车次，排除
                        if seat[0].startswith('G') == False and seat[0].startswith('D') == False and seat[0].startswith('C') == False:
                            five_list.append(seat)  # 将高级软卧、软卧、硬卧未处理信息添加至列表中
                            new_seat = is_ticket(tmp_list, from_station, to_station)  # 判断某车次是否有票
                            five_car_list.append(new_seat)  # 将判断后的车次信息(已处理)添加至对应的列表当中


# 判断高级软卧、软卧、硬卧是否有票函数
def is_ticket(tmp_list,from_station, to_station):
    # 判断高级软卧、软卧、硬卧任何一个有票的话，就说明该趟类车有卧铺车票
    # if tmp_list[21]=='有' or tmp_list[23]=='有' or tmp_list[28]=='有':
    #     tmp_tem = '有'
    # elif tmp_list[21].isdigit() and tmp_list[23].isdigit() and tmp_list[28].isdigit():
    #         if int(tmp_list[21])==0 or int(tmp_list[23])==0 or int(tmp_list[28])==0:
    #             tmp_tem = '无'
    #         else:
    #              tmp_tem =  int(tmp_list[21])+ int(tmp_list[23])+int(tmp_list[28])
    #
    # elif tmp_list[21]!='有' and tmp_list[23]!='有' and tmp_list[28]!='有':
    #     if tmp_list[21].isdigit() or tmp_list[23].isdigit() or tmp_list[28].isdigit():
    #
    #
    #
    # else:
    #         tmp_tem = '无'

    temp = 0
    flag = False
    new_judge= []
    new_judge.append(tmp_list[21])
    new_judge.append(tmp_list[23])
    new_judge.append(tmp_list[28])
    for jj in new_judge:
        if jj == '有':
            flag = True
            break
        elif jj.isdigit():
            temp+=int(jj)
        elif jj == '无':
            continue
    if flag == True:
      tmp_tem = '有'
    elif temp == 0:
      tmp_tem = '无'
    else:
      tmp_tem = str(temp)


    # 创建新的座位列表，显示某趟列车是否有卧铺票
    new_seat = [tmp_list[3], from_station, to_station, tmp_list[8], tmp_list[9], tmp_list[10],tmp_tem ]
    # print('111111111111111111111111111111111111111111111111')
    # print(new_seat)
    return new_seat # 返回该列表



#查询车票起售时间函数
station_name_list = []  # 保存起售车站名称列表
station_time_list = []  # 保存起售车站对应时间列表

def query_time(station):
    station_name_list.clear()  # 清空数据
    station_time_list.clear()  # 清空数据
    stations = eval(read('time.text'))  # 读取所有车站并转换为dic类型
    url = 'https://www.12306.cn/index/otn/index12306/queryScSname'  # 请求地址
    form_data = {"station_telecode": station}  # 表单参数，station参数为需要搜索车站的英文缩写
    response = requests.post(url, data=form_data, verify=True)  # 请求并进行验证
    response.encoding = 'utf-8'  # 对请求所返回的数据进行编码
    json_data = json.loads(response.text)  # 解析json数据
    data = json_data.get('data')  # 获取json中可用数据，也就是查询车站所对应的站名
    for i in data:  # 遍历查询车站所对应的所有站名
        if i in stations:  # 在站名时间文件中，判断是否存在该站名
            station_name_list.append(i)  # 有该站名就将站名添加至列表中
    for name in station_name_list:  # 遍历筛选后的站名
        time = stations.get(name)  # 通过站名获取对应的时间
        station_time_list.append(time)  # 将时间保存至列表
    return station_name_list, station_time_list # 将列表信息返回

