# stock_crawling and analysis with corona

#### 코스피 주식을 수집하고, 코로나 데이터를 불러와 이들간의 상관성에 대한 EDA를 진행합니다.
* 코스피 데이터 크롤링.

stock_crawler 폴더에 담긴 py파일은 네이버 주식 사이트에 게재된 코스피 등록 회사들의 주가를 지정한 기간만큼 수집하는 크롤러입니다.

stock_crawling 클래스로 구현되어 있으며, 네이버 주식 페이지에서 시작하도록 되어 있습니다. 크롤링을 위하여 반드시 webdriver.exe 파일이 current directory에 설치가 되어 있어야 합니다.

start(): webdriver 를 활용하여 브라우저에 입장합니다.
company(): 회사별로 주식 페이지에 대한 url을 수집합니다.
stock(): 회사별로 주식 정보가 담긴 테이블 페이지를 webdriver를 활용해 열고, 회사이름, 업종, 종가를 수집합니다.
run(): 위의 함수들을 실행시키는 함수입니다. 리턴 값으로 수집한 주식 데이터가 출력됩니다.








```python
import pandas as pd

```

# 주식데이터 불러오기

```python
def stock_data(fname):
    stock = pd.read_excel(fname)
    
    
    stock.dropna(axis=0, how ='any', inplace=True) # 시장 문 닫은 주말 제거
    
    company_name = list(set(stock.회사이름)) # 회사이름 획득.
    
    stock_anal = stock[['날짜','종가','회사이름','업종']] # 필요한 변수
    stock_date = [i.replace('.','') for i in stock_anal['날짜'].tolist()] # 날짜 변수 전처리
    
    stock_anal['날짜'] = stock_date
    
    stock_anal.reset_index(drop=True, inplace=True)
    
    return stock_anal
```



```python
stock_anal = stock_data('주식 시세_최종.xlsx') # 주식 데이터 불러오기. 실행.
```

```python
stock_anal.head() # 불러온 결과.
```



# 코로나 데이터 불러오기



```python
def corona_data(fname):
    corona=pd.read_csv(fname, encoding='cp949')
    
    corona = pd.pivot_table(data=corona, index='date', columns='region',values='confirmed') #피벗테이블
    
    corona["확진자"]=corona.sum(axis=1) # 전국 확진자 합계
    
    # 필요한 변수
    corona=corona[['확진자']]
    corona['날짜'] = [str(i) for i in corona.index]
    
    return corona
```



```python
corona = corona_data('코로나 발생.txt') # 코로나 데이터 불러오기. 실행.
```

```python
corona.head() #불러온 결과
```

![image-20210430002409540](corona_stock.assets/image-20210430002409540.png)



# 코로나+주식 데이터 병합

```python
def combine(corona, stock):
    stock_corona = pd.merge(left=stock, right=corona, on='날짜') # 병합
    
    stock_corona.sort_values(by=['회사이름','날짜'],ascending=True, inplace=True) # 정렬
    
    return stock_corona
```

```python
stock_corona = combine(corona, stock_anal) # 데이터 병합하기.
stock_corona.head() # 실행결과.
```

![image-20210430002451006](corona_stock.assets/image-20210430002451006.png)



# 상관계수



```python
company_name=list(set(stock_corona['회사이름'].tolist())) # 회사이름 명단.

def correlation(data):
    n=[]
    c=[]
    for i in company_name[:]:
        tmp = data[data['회사이름'].apply(lambda x: x==i)].reset_index(drop=True)
        c.append(tmp[['확진자','종가']].corr().iloc[1,0])
        n.append(i)
        
    result = pd.DataFrame([n,c]).T
    
    result.columns = ['회사이름','상관계수']
    
    result = result.sort_values(by=['상관계수'], ascending=False).reset_index(drop=True)
    
    return result
```





```python
result=correlation(stock_corona)# 실행결과
```

```python
result_domain=pd.merge(left=result, right=stock_corona[['회사이름','업종']].drop_duplicates(), on='회사이름')
```



####  '회사이름', '업종', '상관계수' 엑셀 파일 저장

```python
result_domain.to_excel('주식_코로나_상관계수.xlsx')
```



# 코로나 확진자 현황 그래프



```python
# 한글깨짐을 위한 기본세팅
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
rc('font', family=font_name)
plt.rcParams['axes.unicode_minus'] = False

plt.rcParams['figure.figsize'] = (15,7)
```



#### 누적 확진자 그래프 

```python
plt.plot(range(len(corona)), corona.확진자, color='hotpink')
plt.title('확진자 현황', ) # 제목 붙이기
plt.ylabel('확진자 수')

frame = plt.gca()
frame.axes.get_xaxis().set_visible(False)

plt.text(-3,900,'신천지 2/17', fontsize=13, color='r')
plt.text(-5,-1000,'2월 17일', fontsize=13)
plt.text(18,-1000,'3월', fontsize=13)
plt.text(48,-1000,'4월', fontsize=13)
plt.text(78,-1000,'5월', fontsize=13)
plt.text(16,8100,'콜센터 3/9', fontsize=13, color='r')
plt.text(77,11200,'이태원 5/7', fontsize=13, color='r')
plt.text(97,11700,'쿠팡 5/27', fontsize=13, color='r')
plt.text(115,-1000,'6월 15일', fontsize=13)


```



![image-20210430003014833](corona_stock.assets/image-20210430003014833.png)


# 상관관계가 있는 회사들 살펴보기

```python
domain = list(set(result_domain.업종)) # 업종 리스트.
```

```python
# 업종이 없거나, 상장폐지된 회사 제외.
import math
pre = result_domain[result_domain['업종'].apply(lambda x: x != '없종없음')] # 업종없는 회사 제외
pre = pre[pre['상관계수'].apply(lambda k: math.isnan(k) == False)].reset_index(drop=True)# 거래정지된 회사 제외
```



상관계수 0.4를 기준으로 양/음의 상관관계가 있음을 기준으로 함



```python
positive = pre[pre['상관계수'].apply(lambda x: x >= 0.4)]
negative = pre[pre['상관계수'].apply(lambda x: x <= -0.4)]
```





### 양의 상관관계가 있는 회사

```python
from collections import Counter

tmp=pd.DataFrame([dict(Counter(positive.업종)).keys(), dict(Counter(positive.업종)).values()]).T
tmp.columns=['업종','개수']
tmp.sort_values(by='개수', ascending=False, inplace=True)
tmp.reset_index(drop=True, inplace=True)

bar=plt.bar(tmp.업종, tmp.개수, color='skyblue')
bar[0].set_color('hotpink')
bar[1].set_color('pink')

plt.xticks(rotation=45)
plt.xlim(-1,10.5)

plt.title('양의 상관관계를 가진 상위 업종')
plt.ylabel('개수')
plt.xlabel('업종')
```



![image-20210430003105411](corona_stock.assets/image-20210430003105411.png)



양의 상관관계를 가진 제약회사

```python
tmp = pre[pre['업종'].apply(lambda x: x=='제약')]
tmp[tmp['상관계수']>=0.4]
```

![image-20210430003124224](corona_stock.assets/image-20210430003124224.png)



```python
tmp = pre[pre['업종'].apply(lambda x: x=='제약')]
tmp
```

![image-20210430003144977](corona_stock.assets/image-20210430003144977.png)

 양의 상관관계를 가진 화학회사

```python
tmp = pre[pre['업종'].apply(lambda x: x=='화학')]
tmp[tmp['상관계수']>=0.4]
```

![image-20210430003204694](corona_stock.assets/image-20210430003204694.png)



### 양의 상관관계가 가장 높은 제약회사들과 확진자수 그래프



```
p1=stock_anal[stock_anal['회사이름']=='부광약품'].sort_values(by='날짜',ascending=True)
p2=stock_anal[stock_anal['회사이름']=='녹십자'].sort_values(by='날짜',ascending=True)
p3=stock_anal[stock_anal['회사이름']=='신풍제약'].sort_values(by='날짜',ascending=True)
p4=stock_anal[stock_anal['회사이름']=='셀트리온'].sort_values(by='날짜',ascending=True)
p5=stock_anal[stock_anal['회사이름']=='일양약품'].sort_values(by='날짜',ascending=True)
k1=corona

from sklearn import preprocessing
import numpy as np
def standard(data, column):
    x_array = np.array(data[column])
    stand = preprocessing.normalize([x_array])
    return stand[0]

p1['standard']=standard(p1,'종가')
p2['standard']=standard(p2,'종가')
p3['standard']=standard(p3,'종가')
p4['standard']=standard(p4,'종가')
p5['standard']=standard(p5,'종가')
k1['standard']=standard(k1,'확진자')


plt.plot(range(120), p1.standard)
plt.plot(range(120), p2.standard)
plt.plot(range(120), p3.standard)
plt.plot(range(120), p4.standard)
plt.plot(range(120), p5.standard)
plt.plot(range(120), k1.standard)

plt.legend(['부광약품','녹십자','신풍제약','셀트리온','일양약품','확진자'])
plt.axvline(x=0, ymin=0, ymax=1, color='hotpink',linestyle='--')
plt.axvline(x=20, ymin=0, ymax=1, color='hotpink',linestyle='--')
plt.axvline(x=79, ymin=0, ymax=1, color='hotpink',linestyle='--')
plt.axvline(x=99, ymin=0, ymax=1, color='hotpink',linestyle='--')

```



![image-20210430003230811](corona_stock.assets/image-20210430003230811.png)



### 음의 상관관계가 있는 회사

```python
from collections import Counter

tmp=pd.DataFrame([dict(Counter(negative.업종)).keys(), dict(Counter(negative.업종)).values()]).T
tmp.columns=['업종','개수']
tmp.sort_values(by='개수', ascending=False, inplace=True)
tmp.reset_index(drop=True, inplace=True)

bar=plt.bar(tmp.업종, tmp.개수, color='skyblue')
bar[0].set_color('hotpink')
bar[1].set_color('pink')

plt.xticks(rotation=45)
plt.xlim(-1,10.5)

plt.title('음의 상관관계를 가진 상위 업종')
plt.ylabel('개수')
plt.xlabel('업종')
```

![image-20210430003248179](corona_stock.assets/image-20210430003248179.png)





음의 상관관계를 가진 자동차부품 회사

```python
tmp = pre[pre['업종'].apply(lambda x: x=='자동차부품')]
tmp[tmp['상관계수']<=-0.4]
```

![image-20210430003308121](corona_stock.assets/image-20210430003308121.png)



음의 상관관계를 가진 섬유,의류,신발,호화품 회사

```python
tmp = pre[pre['업종'].apply(lambda x: x=='섬유,의류,신발,호화품')]
tmp[tmp['상관계수']<=-0.4]
```

![image-20210430003331160](corona_stock.assets/image-20210430003331160.png)





### 음의 상관관계가 높은 자동차부품 회사와 확진자 그래프

```python
p1=stock_anal[stock_anal['회사이름']=='일정실업'].sort_values(by='날짜',ascending=True)
p2=stock_anal[stock_anal['회사이름']=='우신시스템'].sort_values(by='날짜',ascending=True)
p3=stock_anal[stock_anal['회사이름']=='금호타이어'].sort_values(by='날짜',ascending=True)
p4=stock_anal[stock_anal['회사이름']=='새론오토모티브'].sort_values(by='날짜',ascending=True)
p5=stock_anal[stock_anal['회사이름']=='상신브레이크'].sort_values(by='날짜',ascending=True)
k1=corona


# from sklearn import preprocessing
import numpy as np
def standard(data, column):
    x_array = np.array(data[column])
    stand = preprocessing.normalize([x_array])
    return stand[0]

p1['standard']=standard(p1,'종가')
p2['standard']=standard(p2,'종가')
p3['standard']=standard(p3,'종가')
p4['standard']=standard(p4,'종가')
p5['standard']=standard(p5,'종가')
k1['standard']=standard(k1,'확진자')


plt.plot(range(120), p1.standard)
plt.plot(range(120), p2.standard)
plt.plot(range(120), p3.standard)
plt.plot(range(120), p4.standard)
plt.plot(range(120), p5.standard)
plt.plot(range(120), k1.standard)

plt.legend(['일정실업','우신시스템','금호타이어','새론오토모티브','상신브레이크','확진자'])
plt.axvline(x=0, ymin=0, ymax=1, color='hotpink',linestyle='--')
plt.axvline(x=20, ymin=0, ymax=1, color='hotpink',linestyle='--')
plt.axvline(x=79, ymin=0, ymax=1, color='hotpink',linestyle='--')
plt.axvline(x=99, ymin=0, ymax=1, color='hotpink',linestyle='--')


```

![image-20210430003359354](corona_stock.assets/image-20210430003359354.png)





# issue day 구간 별로 확진자와 주가 비교

2월 17일 - 신천지 3월 9일 - 구로 콜센터 5월 7일 - 이태원 클럽 5월 27일 - 쿠팡 부천물류센터



#### 이슈 구간 나누기

```

corona_specific = corona 
corona_specific['d'] = corona_specific.index

corona_daegu = corona_specific[corona_specific['d'] < 20200308]
corona_guro= corona_specific[corona_specific['d'].apply(lambda x: x>=20200309 and x<=20200329)]
corona_club= corona_specific[corona_specific['d'].apply(lambda x: x>=20200507 and x<=20200527)]
corona_coopang= corona_specific[corona_specific['d'].apply(lambda x: x>=20200527 and x<=20200616)]

result_daegu=correlation(combine(corona_daegu, stock_anal))
result_guro=correlation(combine(corona_guro,stock_anal))
result_club=correlation(combine(corona_club,stock_anal))
result_coopang=correlation(combine(corona_coopang,stock_anal))
```



### 1. 대구 코로나 2월 17일 후 20 일 동안



```python
final_daegu=pd.merge(left=result_daegu, right=stock_corona[['회사이름','업종']].drop_duplicates(), on='회사이름') # stock data와 병합

final_daegu=final_daegu[final_daegu['업종']!='없종없음']

positive = final_daegu[final_daegu['상관계수'].apply(lambda x: x >= 0.4)]
negative = final_daegu[final_daegu['상관계수'].apply(lambda x: x <= -0.4)]
```



```python
def top_bar_graph(data,num=1):
    from collections import Counter

    tmp=pd.DataFrame([dict(Counter(data.업종)).keys(), dict(Counter(data.업종)).values()]).T
    tmp.columns=['업종','개수']
    tmp.sort_values(by='개수', ascending=False, inplace=True)
    tmp.reset_index(drop=True, inplace=True)

    bar=plt.bar(tmp.업종, tmp.개수, color='skyblue')
    bar[0].set_color('hotpink')
    bar[1].set_color('pink')

    plt.xticks(rotation=45, fontsize=15)
    plt.yticks(fontsize=15)
    plt.xlim(-1,10.5)
    if num ==1:
        plt.title('양의 상관관계를 가진 상위 업종', fontsize= 20)
    else:
        plt.title('음의 상관관계를 가진 상위 업종', fontsize= 20)
    plt.ylabel('개수', fontsize=15)
    plt.xlabel('업종', fontsize=15)
    
top_bar_graph(positive,1)
```



![image-20210430003505375](corona_stock.assets/image-20210430003505375.png)

처음에 제조회사가 종목이 꽤 존재한다. 아직 직격탄을 맞지 않은 상태.



```python
top_bar_graph(negative,0)
```

![image-20210430003528587](corona_stock.assets/image-20210430003528587.png)

빈도 자체는 음의 상관관계에서 훨씬 많이 존재한다.즉 확진자가 늘수록 주가가 떨어지는 기업이 훨씬 많다는 소리.





### 3월 9일 구로 콜센터 이후 20일간



```python
final_guro=pd.merge(left=result_guro, right=stock_corona[['회사이름','업종']].drop_duplicates(), on='회사이름') # stock data와 병합

final_guro=final_guro[final_guro['업종']!='없종없음']

positive = final_guro[final_guro['상관계수'].apply(lambda x: x >= 0.4)]
negative = final_guro[final_guro['상관계수'].apply(lambda x: x <= -0.4)]

top_bar_graph(positive,1)
```

![image-20210430003600629](corona_stock.assets/image-20210430003600629.png)



```python
top_bar_graph(negative,0)
```

![image-20210430003621635](corona_stock.assets/image-20210430003621635.png)



### 3. 5월 7일 이태원 클럽 이후 20일 간

```python
final_club=pd.merge(left=result_club, right=stock_corona[['회사이름','업종']].drop_duplicates(), on='회사이름') # stock data와 병합

final_club=final_club[final_club['업종']!='없종없음']

positive = final_club[final_club['상관계수'].apply(lambda x: x >= 0.4)]
negative = final_club[final_club['상관계수'].apply(lambda x: x <= -0.4)]
```

```python
top_bar_graph(positive,1)
```

![image-20210430003646580](corona_stock.assets/image-20210430003646580.png)

```python
top_bar_graph(negative,0)
```

![image-20210430003702218](corona_stock.assets/image-20210430003702218.png)



### 4. 5월 27일 쿠팡 물류센터 이후 20일 간



```python
final_coopang=pd.merge(left=result_coopang, right=stock_corona[['회사이름','업종']].drop_duplicates(), on='회사이름') # stock data와 병합

final_coopang=final_coopang[final_coopang['업종']!='없종없음']

positive = final_coopang[final_coopang['상관계수'].apply(lambda x: x >= 0.4)]
negative = final_coopang[final_coopang['상관계수'].apply(lambda x: x <= -0.4)]

top_bar_graph(positive,1)
```

![image-20210430003724616](corona_stock.assets/image-20210430003724616.png)

```python
top_bar_graph(negative,0)
```

![image-20210430003741735](corona_stock.assets/image-20210430003741735.png)

#### 계속해서 양의 상관관계에서 제조업이 2위로 등장하는 이유는 우리나라 산업에서 제조업이 차지하는 비중자체가 크기때문인 것으로 보인다. 양/음 둘다 비교하면 빈도 자체가 음의 상관관계가 높은 회사들이 많다. 

#### 양의 상관관계를 갖는 제조업을 살펴보는 것도 의미가 있어 보인다.

```python
tmp=result_domain[result_domain['업종']=='섬유,의류,신발,호화품']
tmp=tmp[tmp['상관계수']>=0.4]
tmp
```

![image-20210430003819329](corona_stock.assets/image-20210430003819329.png)

 ### 위의 회사들은 왜 확진자가 올라감에도 주가가 상승하였는가?

### 이 제약회사는 왜 주가가 하락하였는가?

```python
tmp=result_domain[result_domain['업종']=='제약']
tmp=tmp[tmp['상관계수']<=-0.4]
tmp
```

![image-20210430003903581](corona_stock.assets/image-20210430003903581.png)

 변수하나로 모든 것을 설명할 수 없다. 특히 많은 변수를 동반하는 주식의 경우는 더욱 그렇다. 하지만 구제적인 이슈이고 크리티컬한 영향력을 미친것은 확실하다. 현재 시국으로 보았을 때, 간단한 EDA 를 거쳐 다양한 관점으로의 해석으로 접근하기 좋은 주제인 듯 하다.









