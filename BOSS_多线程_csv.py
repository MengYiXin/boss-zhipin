from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from lxml import etree
import time,random,requests,json,threading,queue,csv,multiprocessing
#程序开始时间
start = time.time()
q = queue.Queue()
#导入openpyxl列表
"""
解析城市的编号。每一个城市有一个独特的编号
然后随机选取100个城市，并将其分成四部分
"""
response = requests.get('https://www.zhipin.com/common/data/city.json').content
data = json.loads(response.decode())
city_number = []
for i in data['data']['cityList']:
    for j in i['subLevelModelList']:
        city_number.append(j['code'])
city_number_100 = random.sample(city_number,100)
city_number1 = city_number_100[0:25]
city_number2 = city_number_100[25:50]
city_number3 = city_number_100[50:75]
city_number4 = city_number_100[75:100]
#主函数，使用selenium开启网页  并用xpath进行解析  然后写入excel文件中
def getdata(city_number):
    driver = webdriver.Chrome()
        #设置显性等待，以判断出现验证码界面时
    wait = WebDriverWait(driver,0)
    locator = (By.XPATH,'//*[@id="wrap"]/div/form/p/img')
    driver.get("https://www.zhipin.com/job_detail/?query=&scity="+str(city_number)+"&industry=&position=")
        #用于记录爬虫进行到第几页
    page_number = 1
    while True:
        try:
            #判断是否出现了验证码的图片，此处采用的时xpath查找的方法
            wait.until(EC.presence_of_element_located(locator))
            print("请在80秒内输入正确的验证码!")
            time.sleep(60)
        except:
            pass
        #利用xpath进行解析，分别解析出城市，公司，职位，薪水，经验要求，学历要求等信息
        element = etree.HTML(driver.page_source,etree.HTMLParser())
        location = element.xpath("//*[@id='main']/div/div[2]/ul/li/div/div[1]/p/text()[1]")
        companys = element.xpath("//*[@id='main']/div/div[2]/ul/li/div/div[2]/div/h3/a/text()")
        positions = element.xpath("//*[@id='main']/div/div[2]/ul/li/div/div[1]/h3/a/div[1]/text()")
        salary = element.xpath("//*[@id='main']/div/div[2]/ul/li/div/div[1]/h3/a/span/text()")
        experience = element.xpath("//*[@id='main']/div/div[2]/ul/li/div/div[1]/p/text()[2]")
        education_background = element.xpath("//*[@id='main']/div/div[2]/ul/li/div/div[1]/p/text()[3]")
        data_list = []
        for i in range(0,min(len(location),len(positions),len(salary),len(experience),len(education_background))):
            data_list.append(
                [location[i], companys[i], positions[i], salary[i], experience[i], education_background[i]])
        q.put(data_list)
        '''with open('BOSS直聘数据.csv', 'a', newline='') as csv_file:
            write = csv.writer(csv_file, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for j in data_list:
                write.writerow(j)'''
        print("%s的第%s页数据爬取完成！" % (location[0], str(page_number)))
        # 如果在页面源码里找到"下一页"为隐藏的标签，就退出循环
        if driver.page_source.find('next disabled')!= -1:
            break
        # 一直点击下一页
        driver.find_element_by_class_name("next").click()
        page_number += 1
    # 关闭chrome浏览器
    driver.quit()
    #保存数据
#主函数。控制爬取的城市
def run(k):
    for j in k:
        getdata(j)
    with open('G:\\2018\\Python\\python_workspaces\\boss\\BOSS_多线程.csv', 'a', newline='') as csv_file:
        write = csv.writer(csv_file, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        while not q.empty():
            for j in q.get():
                write.writerow(j)
    end = time.time()
    print('程序共运行: %s Seconds!' % (end - start))
def main():
    pool = multiprocessing.Pool(processes=5)
    pool.apply_async(run, args=[city_number1])
    pool.apply_async(run, args=[city_number2])
    pool.apply_async(run, args=[city_number3])
    pool.apply_async(run, args=[city_number4])
    pool.close()
    pool.join()
    print("主线程终止")
#线程
if __name__=="__main__":
    print(city_number1)
    print(city_number2)
    print(city_number3)
    print(city_number4)
    main()

