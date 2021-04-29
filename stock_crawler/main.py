import stock_crawler

def main():
    
    start=stock_crawler.stock_crawling()
    stock_price = start.run(12) #  회사별 종가 테이블 12페이지 까지만 가져옴.
    stock_price.to_excel(r'C:\Users\user\증권크롤링\주식 시세.xlsx') # 크롤링 결과 엑셀 파일로 저장.

if __name__ == "__main__":
    main()
