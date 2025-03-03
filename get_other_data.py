import jdatetime
import re
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Keys, ActionChains
from logging import exception


def fa_to_en(text):
    new_text = ''
    for c in text:
        chr_code = ord(c)
        new_text += chr(chr_code - 1728) if (chr_code >= 1776 and chr_code <= 1785) else c
    return new_text

def read_from_divar(dataset):
    driver.get(f'https://divar.ir/v/-/{dataset['token']}')
    print(dataset['token'])
    try:
        sleep(1)
        WebDriverWait(driver, 4).until(
            EC.presence_of_element_located(
                (By.XPATH, "//h1[@class='kt-page-title__title kt-page-title__title--responsive-sized']"))
        )
        dataset['Title'] = driver.find_element(By.XPATH,"//h1[@class='kt-page-title__title kt-page-title__title--responsive-sized']").text

        age = driver.find_element(By.XPATH,"(//td[contains(@class,'kt-group-row-item kt-group-row-item__value')])[2]").text
        dataset['Age'] = jdatetime.datetime.now().year - int(fa_to_en(age.replace(' ', '')))

        price_element = WebDriverWait(driver, 6).until(
                EC.presence_of_element_located((By.XPATH, "//p[@class='kt-base-row__title kt-unexpandable-row__title' and contains(text(), 'قیمت کل')]"))
        )
        price = price_element.find_element(By.XPATH, "./../following-sibling::div//p[@class='kt-unexpandable-row__value']").text
        dataset['Price'] = fa_to_en(price.replace('تومان', '').replace('٬', '').replace(' ', ''))

        meter = driver.find_element(By.XPATH, "//td[contains(@class,'kt-group-row-item kt-group-row-item__value')]").text
        dataset['Meter'] = fa_to_en(meter.replace(' ', ''))

        driver.find_element(By.XPATH, "//p[text()='نمایش همهٔ جزئیات']").click()
        facilities = driver.find_element(By.XPATH, "//div[@class='kt-modal__body kt-modal__body--actionable']").text
        if 'پارکینگ ندارد' in facilities:
            dataset['Parking'] = 0
        else:
            dataset['Parking'] = 1

        if 'آسانسور ندارد' in facilities:
            dataset['Elevator'] = 0
        else:
            dataset['Elevator'] = 1

        if 'انباری ندارد' in facilities:
            dataset['WareHouse'] = 0
        else:
            dataset['WareHouse'] = 1

        WebDriverWait(driver, 6).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='kt-modal__title']/following-sibling::button[1]")))
        driver.find_element(By.XPATH, "//div[@class='kt-modal__title']/following-sibling::button[1]").click()
        WebDriverWait(driver, 6).until(
            EC.presence_of_element_located(
                (By.XPATH, "(//td[contains(@class,'kt-group-row-item kt-group-row-item__value')])[3]")))

        rooms = driver.find_element(By.XPATH,
                                    "(//td[contains(@class,'kt-group-row-item kt-group-row-item__value')])[3]").text
        dataset['Rooms'] = fa_to_en(rooms.replace(' ', ''))

        floor_element = WebDriverWait(driver, 6).until(
            EC.presence_of_element_located(
                (By.XPATH, "//p[@class='kt-base-row__title kt-unexpandable-row__title' and contains(text(), 'طبقه')]"))
        )
        floor = floor_element.find_element(By.XPATH,
                                           "./../following-sibling::div//p[@class='kt-unexpandable-row__value']").text
        dataset['Floor'] = fa_to_en(floor.replace(' ', ''))

        date_element = WebDriverWait(driver, 6).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'kt-page-title__subtitle') and contains(text(), 'در تهران')]"))
        )
        date = driver.execute_script("return arguments[0].textContent;", date_element)
        if date.split()[1] == 'روز':
            days_ago = int(fa_to_en(date.split()[0]))
        elif date.split()[1] == 'ماه':
            days_ago = int(fa_to_en(date.split()[0])) * 30
        else:
            days_ago = 0
        dataset['validDate'] = datetime.now() - timedelta(days=days_ago)

        description_element = WebDriverWait(driver, 6).until(
            EC.presence_of_element_located(
                (By.XPATH, "//p[@class='kt-description-row__text kt-description-row__text--primary']"))
        )
        description = driver.execute_script("return arguments[0].textContent;", description_element)
        description = description.replace('\u200C', '').replace(' ', '').replace('\n', '')
        pre_sales = ['پیشفروش', 'پیشخرید', 'درحالساخت', 'پیشپرداخت', 'اقساط', 'سرمایه', 'سهام', 'پروژه', 'معاوضه', 'تهاتر']
        if any(item in description for item in pre_sales):
            dataset['Price'] = 0

        if 'وام' in description:
            dataset['Loan'] = 1
        else:
            dataset['Loan'] = 0
    except:
        pass

    return dataset

def get_tokens(dataset,n):
    x = 70
    y = 184
    #extra scroll:
    # for i in range(0,1):
    # x = x + y
    # driver.execute_script(f"window.scrollTo(0, {x});")
    #end scroll
    sleep(2)
    i = 0
    x = x + y
    while i < (n / 2):
        for j in range(1, 3):
            try:
                more = driver.find_elements(By.XPATH,"//span[@class='kt-text-truncate no-pointer-event' and contains(text(), 'آگهی‌های بیشتر')]")
                if len(more) > 0:
                    print("is more")
                    element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH,
                                                    "//span[@class='kt-text-truncate no-pointer-event' and contains(text(), 'آگهی‌های بیشتر')]"))
                    )
                    driver.execute_script("arguments[0].click();", element)
                    sleep(8)
                    print("--------------------")
                amlak = driver.find_element(By.XPATH,
                                            f"(//div[@data-index={i}]/div/div)[{j}]/article/a")
                href = amlak.get_attribute('href')[-8:]
                title = amlak.find_element(By.XPATH, 'div//div//h2').text.replace('\u200C', '').replace(' ', '')

                pre_sales = ['پیش', 'درحالساخت', 'اقساط', 'سرمایه', 'سهام', 'پروژه', 'معاوضه', 'تهاتر', 'وام']
                if not any(item in title for item in pre_sales):
                    dataset = dataset._append({'token': href, 'title2': title}, ignore_index=True)
                else:
                    print("token nemigiram pish forosheeeeeeee!")
            except Exception as e:
                print(e)
                print("Couldn't get token")
        x = x + y
        driver.execute_script(f"window.scrollTo(0, {x});")
        i = i + 1
    return dataset


token_number = int(input("How many tokens would you like to use? "))
if token_number%2 != 0:
    token_number = token_number + 1

driver = webdriver.Chrome()
driver.get("https://divar.ir/s/tehran/buy-apartment/chitgar?price=2000000000-")
driver.maximize_window()

df = pd.DataFrame({
    'token': [],
    'Title':[],
    'title2':[],
    'Age':[],
    'Price':[],
    'Meter': [],
    'Loan': [],
    'Parking':[],
    'Elevator':[],
    'WareHouse':[],
    'Rooms':[],
    'Floor':[]
})

df = get_tokens(df,token_number)
print(len(df))

if not pd.isna(df.iloc[-1]['token']):
    df = df.apply(read_from_divar,axis=1)

df = df[df['Price']!=0]
df = df.dropna()

df.to_csv('divar_prop2.csv', index=False)
df.to_excel('divar_prop2.xlsx', index=False)
