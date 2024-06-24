# from credential import tg_token, wb_token, gs_token, sheet_id, col1, col2, col3
import telebot
from telebot import types
import dataframe_image as dfi
import matplotlib.pyplot as plt
from plotly import graph_objects as go
from plotly.subplots import make_subplots
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
import pandas as pd
import numpy as np
import httplib2
from datetime import datetime, timedelta
import time
import requests
import json

bot = telebot.TeleBot(tg_token)

# Функция дат
def date(d):
    if d == 'today_m':
        return datetime.now().month
    elif d == 'today_q':
        return (datetime.now().month+2)//3
    elif d == 'today_y':
        return datetime.now().year
    elif d == 'today':
        return datetime.now()
    elif d == 'start_of_month':
        return datetime.now().date().replace(day=1)
    elif d == 'start_of_year':
        return datetime.now().date().replace(month=1, day=1)
    
# Парсим ВБ
def wb(method,base_url,param,body):
    headers = {'Authorization': "Bearer {}".format(wb_token)}
    if method == 'get':
        resp = requests.get(base_url+param,headers = headers,json=body).json()
    elif method == 'post':
        resp = requests.post(base_url+param,headers = headers,json=body).json()
    return(resp)

# Подсоединение к Google Таблицам
def get_service_sacc():
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds_service = ServiceAccountCredentials.from_json_keyfile_dict(gs_token,scopes).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)

# Функция наименования месяца
def def_month(m):
    if m == 1:
        return 'Январь'
    elif m == 2:
        return 'Февраль'
    elif m == 3:
        return 'Март'
    elif m == 4:
        return 'Апрель'
    elif m == 5:
        return 'Май'
    elif m == 6:
        return 'Июнь'
    elif m == 7:
        return 'Июль'
    elif m == 8:
        return 'Август'
    elif m == 9:
        return 'Сентябрь'
    elif m == 10:
        return 'Октябрь'
    elif m == 11:
        return 'Ноябрь'
    elif m == 12:
        return 'Декабрь'

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.username == 'evgenii_butorin' or message.from_user.username == 'zhdakaevn':
        global markup
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Реклама")
        btn2 = types.KeyboardButton("Заказы")
        btn3 = types.KeyboardButton("Продажи")
        btn4 = types.KeyboardButton("Отзывы")
        btn5 = types.KeyboardButton("Ссылка на блогера")
        btn6 = types.KeyboardButton("PROMPT")
        btn7 = types.KeyboardButton("Остатки")
        btn8 = types.KeyboardButton("Продажи по странам")
        btn9 = types.KeyboardButton('Продажи по регионам')
        btn10 = types.KeyboardButton('Воронка продаж')
        markup.add(btn1,btn2,btn3,btn4,btn5,btn6,btn7,btn8,btn9,btn10)
        send = bot.send_message(message.chat.id,'{0.first_name}, привет!\n\n'
                                                'Это бот отчетности <b>Zenith Pharma</b>.\n' 
                                                'С моей помощью ты можешь посмотреть все основные отчеты, и даже получить готовый промпт для GPT-чата'.format(message.from_user),parse_mode = 'HTML',reply_markup=markup)
        bot.register_next_step_handler(send,func)
    else:
        bot.send_message(message.chat.id,text = "Это закрытый канал".format(message.from_user))
    
@bot.message_handler(content_types=['text'])
def func(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Реклама")
    btn2 = types.KeyboardButton("Заказы")
    btn3 = types.KeyboardButton("Продажи")
    btn4 = types.KeyboardButton("Отзывы")
    btn5 = types.KeyboardButton("Ссылка на блогера")
    btn6 = types.KeyboardButton("PROMPT")
    btn7 = types.KeyboardButton("Остатки")
    btn8 = types.KeyboardButton("Продажи по странам")
    btn9 = types.KeyboardButton('Продажи по регионам')
    btn10 = types.KeyboardButton('Воронка продаж')
    markup.add(btn1,btn2,btn3,btn4,btn5,btn6,btn7,btn8,btn9,btn10)
    if message.text == 'Реклама':
        if message.from_user.username == 'evgenii_butorin' or message.from_user.username == 'zhdakaevn':
            # Забираем данные и парсим Google Sheet
            df = get_service_sacc().spreadsheets().values().batchGet(spreadsheetId=sheet_id, ranges=["Лист1"]).execute()
            for i in df['valueRanges']:
                e = i['values']
            df = pd.DataFrame(e)
            df.columns = df.iloc[0]
            df = df[1:]
            df['Дата рекламы'] = pd.to_datetime(df['Дата рекламы'], format= '%d.%m.%Y')
            df['Месяц рекламы'] = df['Дата рекламы'].dt.month
            df['Квартал рекламы'] = df['Дата рекламы'].dt.quarter
            df['Номер недели в месяце'] = df['Дата рекламы'].apply(lambda d: (d.day-1) // 7 + 1)
            df['month_cnt'] = df.groupby(['Месяц рекламы'])['Имя блогера'].transform('count')
            df['week_cnt'] = df.groupby(['Месяц рекламы','Номер недели в месяце'])['Имя блогера'].transform('count')
            df['mean_w'] = df.groupby('Месяц рекламы')['week_cnt'].transform('mean')
            
            # Собираем ДФ для графиков
            df_m = df.copy()
            df_m['count'] = df_m.groupby(['Номер недели в месяце','Месяц рекламы','Квартал рекламы'])['Имя блогера'].transform('count')
            df_m = df_m[['Номер недели в месяце','count','Месяц рекламы','Квартал рекламы']]
            df_m = df_m.drop_duplicates()
            max_week = max(df_m['Номер недели в месяце'])
            max_add = max(df_m['count'])
            # Рисуем графики
            fig,(ax, ax2, ax3) = plt.subplots(1,3)

            # 1 месяц
            df1 = df_m[(df_m['Квартал рекламы'] == date('today_q'))&(df_m['Месяц рекламы'] == date('today_m')-2)]
            month = def_month(df1['Месяц рекламы'].values[0])

            ax.bar_label(ax.bar(df1['Номер недели в месяце'],df1['count'],label = 'Кол-во рекламы',color = col1), fmt=lambda x: f'{x:.0f}',fontsize = 8, padding=3, color='black')
            ax.hlines(y=3, xmin=.5, xmax=max_week+.5, linewidth=2, color='gray',alpha = 1,label = 'KPI',linestyle = 'dashed')
            ax.set_title(f'{month}', 
                          fontweight ='bold',
                          y=1.05, 
                          fontsize=15)
            ax.set_yticks(range(0,max_add+2))
            ax.set_xticks(range(0,max_week+2))
            ax.set_xlabel('Номер недели в месяце')
            ax.set_ylabel('Количество рекламы')
            ax.legend()

            # 2 месяц
            df2 = df_m[(df_m['Квартал рекламы'] == date('today_q'))&(df_m['Месяц рекламы'] == date('today_m')-1)]
            month = def_month(df2['Месяц рекламы'].values[0])

            ax2.bar_label(ax2.bar(df2['Номер недели в месяце'],df2['count'],label = 'Кол-во рекламы',color = col1), fmt=lambda x: f'{x:.0f}',fontsize = 8, padding=3, color='black')
            ax2.hlines(y=3, xmin=.5, xmax=max_week+.5, linewidth=2, color='gray',alpha = 1,label = 'KPI',linestyle = 'dashed')
            ax2.set_title(f'{month}', 
                          fontweight ='bold',
                          y=1.05, 
                          fontsize=15)
            ax2.set_yticks(range(0,max_add+2))
            ax2.set_xticks(range(0,max_week+2))
            ax2.set_xlabel('Номер недели в месяце')
            ax2.set_ylabel('Количество рекламы')
            ax2.legend()

            # 3 месяц
            df3 = df_m[(df_m['Квартал рекламы'] == date('today_q'))&(df_m['Месяц рекламы'] == date('today_m'))]
            month = def_month(df3['Месяц рекламы'].values[0])

            ax3.bar_label(ax3.bar(df3['Номер недели в месяце'],df3['count'],label = 'Кол-во рекламы',color = col1), fmt=lambda x: f'{x:.0f}',fontsize = 8, padding=3, color='black')
            ax3.hlines(y=3, xmin=.5, xmax=max_week+.5, linewidth=2, color='gray',alpha = 1,label = 'KPI',linestyle = 'dashed')
            ax3.set_title(f'{month}', 
                          fontweight ='bold',
                          y=1.05, 
                          fontsize=15)
            ax3.set_yticks(range(0,max_add+2))
            ax3.set_xticks(range(0,max_week+2))
            ax3.set_xlabel('Номер недели в месяце')
            ax3.set_ylabel('Количество рекламы')
            ax3.legend()

            fig.set_figheight(5)
            fig.set_figwidth(15)
            plt.savefig('add.png',bbox_inches='tight')
            description = '<b>Реклама</b>\n\nВерхние графики показывают три последних месяца с количеством рекламы в неделю (для оценки выполнения KPI).'
            bot.send_message(message.chat.id,text = description.format(message.from_user),parse_mode = 'HTML')
            bot.send_photo(message.chat.id, photo=open('add.png','rb'))

            # Квартал
            fig,ax4 = plt.subplots(1,1)

            df4 = df[(df['Квартал рекламы'] == date('today_q'))]
            x4 = df4['Месяц рекламы']
            y4 = df4.groupby('Месяц рекламы')['Имя блогера'].transform('count')

            ax4.bar_label(ax4.bar(x4,y4,label = 'Кол-во рекламы в месяц',color = col1), fmt=lambda x: f'{x:.0f}',fontsize = 8, padding=3, color='black')
            ax4.plot(df4['Месяц рекламы'],df4['mean_w'],'ro',label = 'Среднее кол-во рекламы в неделю')
            ax4.set_title(f'Количество рекламы по месяцам в {date("today_y")} году', 
                          fontweight ='bold',
                          y=1.05, 
                          fontsize=15)
            ax4.set_yticks(range(0,max(y4)+2))
            ax4.set_xticks(range(0,13))
            ax4.set_xlabel('Номер недели в месяце')
            ax4.set_ylabel('Количество рекламы')
            ax4.legend()

            fig.set_figheight(6)
            fig.set_figwidth(16)
            plt.savefig('add.png',bbox_inches='tight')
            description = 'Нижний график показывает общее количество рекламы в месяц и среднее количество в неделю'
            bot.send_message(message.chat.id,text = description.format(message.from_user),parse_mode = 'HTML')
            bot.send_photo(message.chat.id, photo=open('add.png','rb'))
        else:
            bot.send_message(message.chat.id,text = "У вас нет доступа к этому отчету".format(message.from_user))
    elif message.text == 'Заказы':
        if message.from_user.username == 'evgenii_butorin' or message.from_user.username == 'zhdakaevn':
            # Забираем данные и парсим Google Sheets
            df = get_service_sacc().spreadsheets().values().batchGet(spreadsheetId=sheet_id, ranges=["Лист1"]).execute()
            for i in df['valueRanges']:
                e = i['values']
            df = pd.DataFrame(e)
            df.columns = df.iloc[0]
            df = df[1:]
            df['Дата рекламы'] = pd.to_datetime(df['Дата рекламы'], format= '%d.%m.%Y').dt.strftime('%d.%m.%Y')
            df_add = df.copy()
            df_add['Дата рекламы'] = pd.to_datetime(df_add['Дата рекламы'],format='%d.%m.%Y')
            df_add.sort_values('Дата рекламы', inplace=True)
            df_add_d3 = df_add[(df_add['Продукт']=='Витамин Д')|(df_add['Продукт']=='Коллаген + Витамин Д')]
            df_add_coll = df_add[(df_add['Продукт']=='Коллаген')|(df_add['Продукт']=='Коллаген + Витамин Д')]
            # Парсим ВБ
            df = pd.DataFrame(wb(method = 'get',base_url = 'https://statistics-api.wildberries.ru/api/v1/supplier/orders',param = f'?flag=0&dateFrom={date("start_of_month")}',body=''))
            df['product'] = df.apply(lambda row: 'Витамин D3' if row['supplierArticle'] == 'wbomijui7' else 'Коллаген', axis=1)
            df_sale = df.copy()
            df_sale = df_sale[pd.to_datetime(df_sale['date'],format = 'ISO8601') >= f'{date("start_of_month")}T00:00:00']
            df_sale['date'] = df_sale['date'].astype({'date':'datetime64[ns]'}).dt.strftime('%d.%m.%Y')
            df_sale = df_sale[['date','product']]
            df_sale.sort_index(inplace=True)
            df_sale_d3 = df_sale[(df_sale['product']=='Витамин D3')]
            df_sale_coll = df_sale[(df_sale['product']=='Коллаген')]

            # Рисуем графики
            # Коллаген
            fig,(ax2, ax) = plt.subplots(1,2)

            x = pd.to_datetime(df_sale_coll['date'],dayfirst=True).dt.day
            y = df_sale_coll.groupby('date')['product'].transform('count')
            ax2.bar_label(ax2.bar(x,y,label = 'Кол-во продаж',color = col1), fmt=lambda x: f'{x:.0f}',fontsize = 8, padding=3, color='black')

            w = df_add_coll['Дата рекламы'].dt.day
            z = df_add_coll.groupby('Дата рекламы')['Имя блогера'].transform('count')
            ax2.bar_label(ax2.bar(w,z/2,label = 'Кол-во рекламы',color = col2), fmt=lambda x: f'{x * 2:.0f}',fontsize = 8, padding=3, color='black')

            ax2.set_title('Коллаген', 
                      fontweight ='bold',
                      y=1.05, 
                      fontsize=19)
            ax2.set_yticks(range(1,max(y)+2))
            ax2.set_xticks(range(1,max(w)+2 if max(w)+2 >= max(x)+2 else max(x)+2))
            ax2.set_xlabel('Номер дня в месяце')
            ax2.set_ylabel('Кол-во')
            ax2.legend()

            # Витамин Д3
            x1 = pd.to_datetime(df_sale_d3['date'],dayfirst=True).dt.day
            y1 = df_sale_d3.groupby('date')['product'].transform('count')
            ax.bar_label(ax.bar(x1,y1,label = 'Кол-во продаж',color = col1), fmt=lambda x: f'{x:.0f}',fontsize = 8, padding=3, color='black')

            w1 = df_add_d3['Дата рекламы'].dt.day
            z1 = df_add_d3.groupby('Дата рекламы')['Имя блогера'].transform('count')
            ax.bar_label(ax.bar(w1,z1/2,label = 'Кол-во рекламы',color = col2), fmt=lambda x: f'{x * 2:.0f}',fontsize = 8, padding=3, color='black')

            ax.set_title('Витамин Д3', 
                      fontweight ='bold',
                      y=1.05, 
                      fontsize=19)
            ax.set_yticks(range(1,max(y)+2))
            ax.set_xticks(range(1,max(w1)+2 if max(w1)+2 >= max(x1)+2 else max(x1)+2))
            ax.set_xlabel('Номер дня в месяце')
            ax.set_ylabel('Кол-во')
            ax.legend()

            fig.set_figheight(8)
            fig.set_figwidth(22)
            plt.savefig('sales_sep.png',bbox_inches='tight')
            description = '<b>Заказы</b>\n\nВерхние графики показывают данные по заказам в текущем месяце по продуктам отдельно'
            bot.send_message(message.chat.id,text = description.format(message.from_user),parse_mode = 'HTML')
            bot.send_photo(message.chat.id, photo=open('sales_sep.png','rb'))

            # Тотал
            fig, ax3 = plt.subplots(1,1)

            x = pd.to_datetime(df_sale['date'],dayfirst=True).dt.day
            y = df_sale.groupby('date')['product'].transform('count')
            ax3.bar_label(ax3.bar(x,y,label = 'Кол-во продаж',color = col1), fmt=lambda x: f'{x:.0f}',fontsize = 8, padding=3, color='black')

            w = df_add['Дата рекламы'].dt.day
            z = df_add.groupby('Дата рекламы')['Имя блогера'].transform('count')
            ax3.bar_label(ax3.bar(w,z/2,label = 'Кол-во рекламы',color = col2), fmt=lambda x: f'{x * 2:.0f}',fontsize = 8, padding=3, color='black')

            ax3.set_title('Тотал', 
                      fontweight ='bold',
                      y=1.05, 
                      fontsize=19)
            ax3.set_yticks(range(1,max(y)+2))
            ax3.set_xticks(range(1,max(w)+2 if max(w)+2 >= max(x)+2 else max(x)+2))
            ax3.set_xlabel('Номер дня в месяце')
            ax3.set_ylabel('Кол-во')
            ax3.legend()
            fig.set_figheight(8)
            fig.set_figwidth(22)
            plt.savefig('sales.png',bbox_inches='tight')
            description = 'Нижний график показывает данные по заказам в текущем месяце суммарно'
            bot.send_message(message.chat.id,text = description.format(message.from_user),parse_mode = 'HTML')
            bot.send_photo(message.chat.id, photo=open('sales.png','rb'))
        else:
            bot.send_message(message.chat.id,text = "У вас нет доступа к этому отчету".format(message.from_user))
    elif message.text == 'Продажи':
        if message.from_user.username == 'evgenii_butorin' or message.from_user.username == 'zhdakaevn':
            # Парсим ВБ
            df = pd.DataFrame(wb(method = 'get',base_url = 'https://statistics-api.wildberries.ru/api/v1/supplier/sales',param = f'?flag=0&dateFrom={date("start_of_year")}',body=''))
            df['product'] = df.apply(lambda row: 'Витамин D3' if row['supplierArticle'] == 'wbomijui7' else 'Коллаген', axis=1)
            df = df[['date','priceWithDisc']]
            df = df[pd.to_datetime(df['date'],format = 'ISO8601') >= f'{date("start_of_year")}T00:00:00']
            df['date'] = df['date'].astype({'date':'datetime64[ns]'}).dt.strftime('%d.%m.%Y')
            df['priceWithDisc'] = df['priceWithDisc'].astype('int')
            df.sort_index(inplace=True)

            # Создаем план
            data = [['01.01.2024', 89600], ['01.02.2024', 108800], ['01.03.2024', 153600], ['01.04.2024', 70400],['01.05.2024', 70400],['01.06.2024', 96000],['01.07.2024', 67200],['01.08.2024', 83200],['01.09.2024', 128000],['01.10.2024', 99200],['01.11.2024', 105600],['01.12.2024', 128000]]
            plan = pd.DataFrame(data, columns=['date', 'plan'])
            plan['date'] = pd.to_datetime(plan['date'],dayfirst=True).dt.month

            # Объединяем и считаем долю выполнения
            df['date'] = pd.to_datetime(df['date'],dayfirst=True).dt.month
            df['sales'] = pd.DataFrame(df.groupby(df['date'])['priceWithDisc'].transform('sum'))
            df = df[['date','sales']]
            df = plan.merge(df,how = 'left')
            df['share'] = df['sales']/df['plan']*100
            df = df[['date','plan','sales','share']]
            df = df.drop_duplicates()

            # Рисуем графики
            fig,ax = plt.subplots()

            #add first line to plot
            ax.bar_label(ax.bar(df['date'], df['plan'], color=col1, label = 'План, тыс.'), fmt=lambda x: f'{x/1000:.1f}',fontsize = 8, padding=3, color='black')
            ax.bar_label(ax.bar(df['date'], df['sales'], color=col2, label = 'Продажи, тыс.'),fmt=lambda x: f'{x/1000:.1f}',fontsize = 8, padding=3, color='white')
            ax.set_xlabel('Номер месяца')
            ax.set_ylabel('Сумма продаж')

            # Добаляем вторую шкалу
            ax2 = ax.twinx ()
            ax2.plot(df['date'], df['share'], color=col3, marker='o', linewidth= 3, linestyle='dashed',label = '% выполнения плана')
            ax2.bar_label(ax2.bar(df['date'],df['share'],color=col3, alpha=0),fmt=lambda x: f'{x:.0f}%',fontsize = 8, padding=3, color='black')
            ax2.set_ylabel('% выполнения плана')
            ax2.set_yticks(range(0,110,20))

            plt.title('Выполнение плана', 
                      fontweight ='bold',
                      y=1.05, 
                      fontsize=19)
            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            fig.set_figheight(7)
            fig.set_figwidth(10)
            ax2.legend(lines + lines2, labels + labels2, bbox_to_anchor=(1.1, 0.5)).get_frame().set_alpha(1)
            plt.tight_layout()
            plt.savefig('plan.png',bbox_inches='tight')
            description = '<b>Продажи</b>\n\nОтчет содержит продажи YTD (без вычета комиссий, логистики и хранения), план и процент выполнения плана'
            bot.send_message(message.chat.id,text = description.format(message.from_user),parse_mode = 'HTML')
            bot.send_photo(message.chat.id, photo=open('plan.png','rb'))
        else:
            bot.send_message(message.chat.id,text = "У вас нет доступа к этому отчету".format(message.from_user))
    elif message.text == 'Отзывы':
        if message.from_user.username == 'evgenii_butorin' or message.from_user.username == 'zhdakaevn':
            # Парсим ВБ
            resp = wb(method = 'get',base_url = 'https://feedbacks-api.wildberries.ru/api/v1/feedbacks',param = '?isAnswered=True&skip=0&take=1000',body='')
            df = pd.DataFrame(resp['data']['feedbacks'])
            df['product'] = df.apply(lambda row: 'Витамин D3' if 'wbomijui7' in row['productDetails'] else 'Коллаген', axis=1)
            df = df[['createdDate','productValuation','product']]
            df = df[pd.to_datetime(df['createdDate'],format = 'ISO8601') >= f'{date("start_of_year")}T00:00:00Z']
            df['createdDate'] = pd.to_datetime(df['createdDate']).dt.strftime('%d.%m.%Y')

            # Рисуем графики
            # По дням
            fig,(ax2, ax) = plt.subplots(1,2)

            w = df['productValuation']
            z = df.groupby('productValuation')['product'].transform('count')
            ax2.bar_label(ax2.barh(w,z,height=0.7,label = 'Кол-во отзывов',color = col1), fmt=lambda x: f'{x:.0f}',fontsize = 8, padding=3, color='black')

            ax2.set_title('Количество отзывов по рейтингу', 
                          fontweight ='bold',
                          y=1.05, 
                          fontsize=19)
            ax2.set_yticks(range(0,6))
            ax2.set_xticks(range(1,max(z)+10,20))
            ax2.set_xlabel('Количество отзывов')
            ax2.set_ylabel('Количество *')
            ax2.legend()

            # По месяцам
            df1 = df.copy()
            df1['x'] = pd.to_datetime(df1['createdDate'],dayfirst=True).dt.month
            df1['y'] = df1.groupby('x')['productValuation'].transform('count')
            df1 = df1[['x','y']]
            df1 = df1.drop_duplicates()
            ax.bar_label(ax.bar(df1['x'],df1['y'],label = 'Кол-во отзывов',color = col1), fmt=lambda x: f'{x:.0f}',fontsize = 8, padding=3, color='black')

            ax.set_title('Количество отзывов по месяцам', 
                          fontweight ='bold',
                          y=1.05, 
                          fontsize=19)
            ax.set_xlabel('Номер месяца')
            ax.set_ylabel('Количество отзывов')
            ax.legend()

            fig.set_figheight(6)
            fig.set_figwidth(14)
            
            plt.savefig('feedback.png',bbox_inches='tight')
            description = '<b>Отзывы</b>\n\nОтчет содержит статистику по количеству отзывов. В отчете учитываются <b>только отзывы с текстом</b>'
            bot.send_message(message.chat.id,text = description.format(message.from_user),parse_mode = 'HTML')
            bot.send_photo(message.chat.id, photo=open('feedback.png','rb'),reply_markup=markup)
        else:
            bot.send_message(message.chat.id,text = "У вас нет доступа к этому отчету".format(message.from_user))
    elif message.text == 'Ссылка на блогера':
        if message.from_user.username == 'evgenii_butorin' or message.from_user.username == 'zhdakaevn':
            # Забираем данные и парсим Google Sheets
            df = get_service_sacc().spreadsheets().values().batchGet(spreadsheetId=sheet_id, ranges=["Лист1"]).execute()
            for i in df['valueRanges']:
                e = i['values']
            df = pd.DataFrame(e)
            df.columns = df.iloc[0]
            df = df[1:]
            df['Дата рекламы'] = pd.to_datetime(df['Дата рекламы'], format= '%d.%m.%Y')
            df = df[df['Дата рекламы'] == date('today').date()]
            if len(df) > 0:
                link = df['Ссылка на аккаунт'].values[0]
                description = '<b>Ссылка на блогера</b>\n\nОтчет содержит ссылку на блогера с сегодняшней рекламой'
                bot.send_message(message.chat.id,text = description.format(message.from_user),parse_mode = 'HTML')
                bot.send_message(message.chat.id,text = link.format(message.from_user))
            else:
                bot.send_message(message.chat.id,text = 'Сегодня нет рекламы'.format(message.from_user))
        else:
            bot.send_message(message.chat.id,text = "У вас нет доступа к этому отчету".format(message.from_user))
    elif message.text == 'PROMPT':
        if message.from_user.username == 'evgenii_butorin' or message.from_user.username == 'zhdakaevn':
            # Парсим ВБ
            resp = wb(method = 'get',base_url = 'https://feedbacks-api.wildberries.ru/api/v1/feedbacks',param = '?isAnswered=False&skip=0&take=1000',body='')
            df = pd.DataFrame(resp['data']['feedbacks'])
            if len(df) > 0:
                df['product'] = df.apply(lambda row: 'Витамин D3' if 'wbomijui7' in row['productDetails'] else 'Коллаген', axis=1)
                feedback = df['text'].values[0]
                product = df['product'].values[0]
                person = df['userName'].values[0]
                prompt = f'Напиши ответ на отзыв от {person} на {product} от Zenith Pharma: "{feedback}". Порекомендуй купить {"Витамин D3" if product == "Коллаген" else "Коллаген"} от Zenith Pharma'
                description = '<b>PROMPT</b>\n\nОтчет содержит готовый запрос (PROMPT) для получения ответа на отзыв от чат GPT'
                bot.send_message(message.chat.id,text = description.format(message.from_user),parse_mode = 'HTML')
                bot.send_message(message.chat.id,text = prompt.format(message.from_user))
            else:
                description = '<b>PROMPT</b>\n\nОтчет содержит готовый запрос (PROMPT) для получения ответа на отзыв от чат GPT'
                bot.send_message(message.chat.id,text = description.format(message.from_user),parse_mode = 'HTML')
                bot.send_message(message.chat.id,text = 'На текущий момент все отзывы отвечены. PROMPT не требуется'.format(message.from_user))
        else:
            bot.send_message(message.chat.id,text = "У вас нет доступа к этому отчету".format(message.from_user))
    elif message.text == 'Остатки':
        if message.from_user.username == 'evgenii_butorin' or message.from_user.username == 'zhdakaevn':
            # Парсим ВБ
            df = pd.DataFrame(wb(method = 'get',base_url = 'https://statistics-api.wildberries.ru/api/v1/supplier/stocks',param = f'?dateFrom={date("start_of_month")}',body=''))
            df['product'] = df.apply(lambda row: 'Витамин D3' if 'wbomijui7' in row['supplierArticle'] else 'Коллаген', axis=1)
            df = df[['product','quantity','inWayToClient','inWayFromClient','quantityFull']]
            df = df.groupby('product')[['quantity','inWayToClient','inWayFromClient']].sum().reset_index()

            # Выводим остатки
            fig, ax = plt.subplots()
            ax.axis('tight')
            ax.axis('off')
            col = ['Продукт','Остатки на складе','В пути к клиенту','В пути от клиента']
            #plotting data
            table = ax.table(cellText = df.values,
                    colLabels = col,
                    colLoc = 'center', 
                    rowLoc = 'center',
                    loc = 'center')
            fig.set_figheight(7)
            fig.set_figwidth(14)
            table.set_fontsize(20)
            table.scale(1,2)
            plt.savefig('remains.png',
                        bbox_inches='tight',
                        edgecolor=fig.get_edgecolor(),
                        facecolor=fig.get_facecolor(),
                        dpi=150)
            description = '<b>Остатки</b>\n\nОтчет показывает остатки на текущий момент, также в таблице отражены товары в пути до клиента и от клиента'
            bot.send_message(message.chat.id,text = description.format(message.from_user),parse_mode = 'HTML')
            bot.send_photo(message.chat.id, photo=open('remains.png','rb'),reply_markup=markup)
        else:
            bot.send_message(message.chat.id,text = "У вас нет доступа к этому отчету".format(message.from_user))
    elif message.text == 'Продажи по странам':
        if message.from_user.username == 'evgenii_butorin' or message.from_user.username == 'zhdakaevn':
            # Парсим ВБ
            df = pd.DataFrame(wb(method = 'get',base_url = 'https://statistics-api.wildberries.ru/api/v1/supplier/orders',param = f'?flag=0&dateFrom={date("start_of_year")}',body=''))
            df['product'] = df.apply(lambda row: 'Витамин D3' if row['supplierArticle'] == 'wbomijui7' else 'Коллаген', axis=1)
            df['cnt'] = 1
            df['countryName'] = df['countryName'].str.title()
            df = df[pd.to_datetime(df['date'],format = 'ISO8601') >= f'{date("start_of_year")}T00:00:00']
            df['date'] = df['date'].astype({'date':'datetime64[ns]'}).dt.strftime('%d.%m.%Y')
            df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
            df['month'] = df['date'].dt.month
            df_country = df[['countryName','product','cnt']]
            df_country = df_country.groupby(['countryName','product'])['cnt'].sum().reset_index()

            # Рисуем графики
            fig, ax = plt.subplots()
            # Рисуем графики
            lst = []
            for i in range(1,len(df_country)+1):
                if i % 2 == 0:
                    lst.append('#FF6A49')
                else:
                    lst.append('#0095B6')
            fig, ax = plt.subplots()
            ax.scatter(df_country['product'], df_country['countryName'],s=df_country['cnt']*50, alpha=0.5, c = lst)

            # # Decoration
            x_ticks = [-1,0,1,2,]
            plt.title('Продажи по странам')
            plt.xticks(ticks=x_ticks)
            for (xi, yi,zi) in zip(df_country['product'], df_country['countryName'],df_country['cnt']):
                plt.text(xi, yi, zi, va='bottom', ha='center')
   
            plt.savefig('country_sales.png',bbox_inches='tight',dpi = 150)
            description = '<b>Продажи по странам</b>\n\nОтчет показывает продажи по странам за весь 2024 год'
            bot.send_message(message.chat.id,text = description.format(message.from_user),parse_mode = 'HTML')
            bot.send_photo(message.chat.id, photo=open('country_sales.png','rb'),reply_markup=markup)
        else:
            bot.send_message(message.chat.id,text = "У вас нет доступа к этому отчету".format(message.from_user))
    elif message.text == 'Продажи по регионам':
        if message.from_user.username == 'evgenii_butorin' or message.from_user.username == 'zhdakaevn':
            # Парсим ВБ
            df = pd.DataFrame(wb(method = 'get',base_url = 'https://statistics-api.wildberries.ru/api/v1/supplier/sales',param = f'?flag=0&dateFrom={date("start_of_year")}',body=''))
            df['cnt'] = 1
            df = df[pd.to_datetime(df['date'],format = 'ISO8601') >= f'{date("start_of_year")}T00:00:00']
            df = df[df['countryName'] == 'Россия']

            df_region = df[['regionName','cnt']]
            df_region = df_region.groupby(['regionName'])['cnt'].sum().reset_index()
            df_region = df_region.sort_values(by = 'cnt', ascending = True)

            # Рисуем графики
            fig, ax2 = plt.subplots()

            x = np.array(df_region['regionName'])
            y = np.array(df_region['cnt'])
            ax2.bar_label(ax2.barh(x,y,height=0.7,label = 'Продажи',color = col1), fmt=lambda x: f'{x:.0f}',fontsize = 8, padding=3, color='black')
            ax2.set_title('Количество продаж по регионам', 
                          fontweight ='bold',
                          y=1.05, 
                          fontsize=19)

            ax2.set_xlabel('Количество заказов')
            ax2.set_ylabel('Регион')
            fig.set_figheight(20)
            fig.set_figwidth(14)
            ax2.legend()
            plt.savefig('region_sales.png',bbox_inches='tight')
            description = '<b>Продажи по регионам</b>\n\nОтчет показывает продажи по регионам за весь 2024 год'
            bot.send_message(message.chat.id,text = description.format(message.from_user),parse_mode = 'HTML')
            bot.send_photo(message.chat.id, photo=open('region_sales.png','rb'),reply_markup=markup)
        else:
            bot.send_message(message.chat.id,text = "У вас нет доступа к этому отчету".format(message.from_user))
    elif message.text == 'Воронка продаж':
        if message.from_user.username == 'evgenii_butorin' or message.from_user.username == 'zhdakaevn':
            # Парсим ВБ
            body = {
                    'period':{
                            "begin": f"{date('today').date()-timedelta(14)} 00:00:00",
                            "end": f"{date('today')}"
                             },
                    'page':1
                    }
            resp = wb(method = 'post',base_url = 'https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail',param = '',body = body)
            df = pd.DataFrame({'product':[],'Перешли в карточку':[],'Добавили в корзину':[],'Заказали':[]})
            for i in resp['data']['cards']:
                product = 'Витамин D3' if 'wbomijui7' in i['vendorCode'] else 'Коллаген'
                open_card = i['statistics']['selectedPeriod']['openCardCount']
                add_to_basket = i['statistics']['selectedPeriod']['addToCartCount']
                ordered = i['statistics']['selectedPeriod']['buyoutsCount']
                df.loc[len(df)] = [product, open_card,add_to_basket,ordered]
            df1 = df.transpose().reset_index()
            df1 = df1.rename(columns=df1.iloc[0]).drop(df1.index[0])
            df_d3 = df1[['product','Витамин D3']]
            df_d3 = df_d3.rename(columns={'product': 'metrics', 'Витамин D3': 'cnt'})
            df_d3['product'] = 'Витамин D3'
            df_coll = df1[['product','Коллаген']]
            df_coll = df_coll.rename(columns={'product': 'metrics', 'Коллаген': 'cnt'})
            df_coll['product'] = 'Коллаген'
            # Рисуем воронку
            fig = make_subplots(rows=1, cols=2,subplot_titles=("Витамин Д3","Коллаген"), shared_yaxes=True)

            fig.add_trace(go.Funnel(
                name = 'Витамин D3',
                y = df_d3['metrics'],
                x = df_d3['cnt'],
                textposition = "auto",
                marker = {"color": "#FF6A49"},
                textinfo = "value+percent initial"),row=1, col=1)

            fig.add_trace(go.Funnel(
                name = 'Коллаген',
                orientation = "h",
                y = df_coll['metrics'],
                x = df_coll['cnt'],
                marker = {"color": "#0095B6"},
                textposition = "auto",
                textinfo = "value+percent previous"),row=1, col=2)

            fig.update_layout(title=go.layout.Title(text=f"Воронка продаж {date('today').date()-timedelta(14)} - {date('today').date()}", x = 0.5, xanchor = 'center'))

            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',showlegend=False,height=600, width=1000)
            fig.write_image('funnel.png')
            description = '<b>Воронка продаж</b>\n\nОтчет показывает воронку продаж за последние 14 дней'
            bot.send_message(message.chat.id,text = description.format(message.from_user),parse_mode = 'HTML')
            bot.send_photo(message.chat.id, photo=open('funnel.png','rb'),reply_markup=markup)
        else:
            bot.send_message(message.chat.id,text = "У вас нет доступа к этому отчету".format(message.from_user))
    
bot.polling(none_stop=True)

