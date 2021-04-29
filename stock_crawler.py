
# # 회사별 주식 데이터 수집
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm
import requests
import time
import re



class stock_crawling():


    
    def __init__(self):
        self.table_number = "https://finance.naver.com/item/sise_day.nhn?code=" # html안잡힘.
        print('init')

        
        
    def start(self): # 브라우저 실행.
        driver = webdriver.Chrome(executable_path='chromedriver.exe') # 브라우저 열기
        # 현재 디렉토리에 크롬드라이버 exe 파일 있음.
        
        driver.implicitly_wait(3) # 암묵적으로 웹 자원을 (최대) 3초 기다리기
        
        
    def company(self, url, p_num):   # 회사별 주식 페이지 url 수집.
        
        driver = webdriver.Chrome(executable_path='chromedriver.exe') # 브라우저 열기

        self.company_url=[]

        for i in tqdm(range(1,p_num+1)):
            
            driver.get(str(url)+str(i)) # 시가총액 첫페이지
            
            time.sleep(1) # 웹페이지 열릴 시간을 줌.

            html=driver.page_source # html 소스 
            soup=BeautifulSoup(html, 'html.parser') # html 소스 정리

            notices = soup.select('tbody')[1].find_all('a') # 페이지의 모든 회사 url 획득

            for j in notices:
                if 'main' in j['href']:
                    self.company_url.append('https://finance.naver.com/'+str(j['href']))


        return self.company_url

    
    
    
    def stock(self,t_num,c_url): # t_num: 시세 테이블 페이지 수

        import pandas as pd
        
        self.t_num=t_num
        self.company_url=c_url
        print(self.company_url)
        
        #시세 table number
        self.company_price=pd.DataFrame()

        driver = webdriver.Chrome(executable_path='chromedriver.exe') # 브라우저 열기

        
        for c_url in tqdm(self.company_url):
            data=pd.DataFrame() # 회사마다 시세가 잠시 담기는 곳.




            driver.get(c_url)  # 회사 페이지 진입
            time.sleep(0.1)
            html=driver.page_source
            soup=BeautifulSoup(html,'html.parser')


            # 회사 이름
            c_name = soup.select('#middle > dl.blind > dd ')[1].text.split()[1:] # 이름 획득
            c_name = " ".join(c_name)
            print(c_name)

            # 업종
            try:
                d_name = soup.select('#content > div > h4 > em > a')[0].text # 이름 획득
                print(d_name)
            except:
                print('업종없음')
                d_name = '없종없음'


            price_url = soup.select('#content > ul > li > a.tab2')[0]['href'] 
            price_url = "https://finance.naver.com/"+price_url
            driver.get(price_url) # 시세 페이지 진입
            print(price_url)


            for num in range(1,self.t_num+1):
                table_url = self.table_number+c_url[-6:]+"&page="+str(num) # 고정 url, 지정 변수 입력(self.table_number)

                driver.get(table_url)
                time.sleep(0.1)
                data = pd.concat([data,pd.read_html(table_url, encoding='cp949')[0]]) # 시세 테이블 획득.

            data['회사이름'] = [c_name for _ in range(len(data))]
            data['업종'] = [d_name for _ in range(len(data))]
            self.company_price = pd.concat([self.company_price,data], ignore_index=True)

        return self.company_price

    
    

    def run(self,pages=12): # 위의 함수들을 실행시킬 함수.
        
        
        self.pages = pages

        play=stock_crawling() #1. 초기화
        
        play.start() #2. 브라우저 실행

        
        
        self.url='https://finance.naver.com/sise/sise_market_sum.nhn?&page=' #고정 url, 지정변수 입력
        p_num=32
        self.c_url = play.company(self.url,p_num) #3. 회사별 주식 페이지 url 수집

        stock_price = play.stock(self.pages, self.c_url) #4. 회사별 주식 수집, pages: 시세 테이블 페이지 수

        return stock_price




