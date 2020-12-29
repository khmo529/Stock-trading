import requests as rq #요청하기
from bs4 import BeautifulSoup #파싱
import re #숫자만 분리
import sys #종료
from datetime import datetime #time은 시간 datetime은 날짜
import time
import random
import sqlite3
print("\t모의 주식 프로그램에 오신것을 환영합니다")
conn = sqlite3.connect("./rank.db")
cursor = conn.cursor()
                                                                                                    #db만들기
cursor.execute("create table if not exists RANKER (name char(10), num int)")
conn.commit()
total_money=int(1000000)
total_count=int(0)
#순위별로보기
while True:
    today = datetime.now()
    myDate =('%s년-%s월-%s일 기준' % (today.year, today.month, today.day))
    myTime = time.strftime('%H시%M분%S초\n')
    print('\t\t',myDate)
    print('\t\t',myTime)
    top_url = "https://finance.naver.com/sise/"    #네이버 주식 검색순위 1~10위 가져오기
    res = rq.get(top_url)
    soup = BeautifulSoup(res.text, 'lxml')

    def re_list(): #리스트 뿌려주기
        for i in range(10):
            lis = soup.select('#popularItemList > li')[i].text
            i+=1
            print(lis)
    re_list()
    print("=============================")
    print("**1~10위 이외의 숫자를 입력하면 종료됩니다**")    #1~10위 정보 가져오기
    rank=int(input("몇 위의 정보를 가지고 올까요? (1~10위만 가능) : "))
        
    if 0>rank or rank>10 :    #1~10위 아니면 종료
        print('\n프로그램을 종료합니다\n안녕히가세요')
        break
    lis = soup.select('#popularItemList > li')[int(rank)-1].text 
                                                #순위 넣기
    numbers = re.findall("\d+", lis)
    price=int(numbers[1]+numbers[2])
    p= re.compile("[^.0-9]")        #. 0~9 제외하고 split으로 리스트화
    lischar=''.join(p.findall(lis)) #반환할때 '' 사이에 값으로 반환 여기는 아무것도 없으니까 전부 그냥 반
    lischar_split=(lischar.split(','))        #company는 기업 이름만
    company=lischar_split[0]        #price는 가격
    print("\n=============================")
    print(company,"의 정보를 가져왔습니다")
    print(company,"의 현재가는",price,"원 입니다")
#거래
    while True:
        print("=============================")
        r=random.randrange(-10,11)                   #랜덤으로 값 바꿔주는 라인
        price=price+price*r/100
        profit=(total_money+price*total_count)-1000000
        profitper=float(profit/1000000*100)
        cursor.execute("select * from RANKER order by num desc")
        rk = cursor.fetchall()
        c=1
        for i in rk:
            print('현재',c,"위 ,","이름 :",i[0],", 이익 :",int(i[1]),"원")
            break
        print("(보유중인 돈%d원)\n(보유중인 수량%d개)\n(현재이익%d원)\n(현재이익율%dpoint)\n1=랜덤돌리기\n2=구매\n3=판매\n4=종목최초가격다시보기\n5=종료(종목선택으로돌아갑니다)"%(total_money,total_count,profit,profitper))
        menu=int(input("메뉴를 선택하세요(1~5) 입력 : "))
        print("\n===================")
        if menu==1: #가격보기
            print('',company+"의 가격은 "+str(price)+"원")
            print('\t',r,"%변동")
            continue
        elif price==0:
            print("파산했습니다..")
            break
        elif menu==2: #구매하기
            print('\n',company+"의 가격은 "+str(price)+"원")
            print('\t',r,"퍼센트변동")
            count=int(input("수량을 선택해주세요(0개면 메뉴로) : "))
            if int(total_money)>=int(count*price):
                total_count+=count
                total_money=total_money-(count*price)
                print("\n%d개를 구매했습니다\n총보유수량 : %d\n잔액 : %d"%(count,total_count,total_money))
                continue
            elif count==0:
                continue
            elif int(total_money)>=int(total_money):
                print("구매수량이 보유금액을 초과합니다")
                continue
        elif menu==3: #판매하기
            print('\n',company+"의 가격은 "+str(price)+"원")
            print('\t',r,"퍼센트변동")
            print("====================")
            count=int(input("수량을 선택해주세요(0개면 메뉴로) : "))
            if count>total_count:
                print("판매수량을 초과했습니다")
                continue
            elif count==0:
                continue
            elif int(total_count)>=int(count):
                total_count-=count
                total_money=total_money+(count*price)
                print("\n%d개를 판매했습니다\n총보유수량 : %d\n잔액 : %d"%(count,total_count,total_money))
                continue
        elif menu==4: #리스트 다시보기
            print('\n')
            re_list()
            continue
        elif menu==5: #종료        
            break
        elif menu>4 or menu<1:
            print("\n!!!!!!!!!!!!!!!그런 메뉴없습니다!!!!!!!!!!!!!!!!!!!!!\n")
            continue
        
#순위
while True:
    last=int(input("\n1=순위보기\n2=순위추가\n3=순위삭제\n4=종료\n입력 : "))
    if last==1:
        cursor.execute("select * from RANKER order by num desc")
        rk = cursor.fetchall()
        print(rk[0])
        c=1
        for i in rk:
            print(c,"위 ,","이름 :",i[0],", 이익 :",int(i[1]),"원")
            c+=1
        print("=====================")
        continue
    elif last==2:
        print("\n수익률 순위를 등록합니다")
        your_name=input("이름을 입력하세요 : ")
        cursor.execute("insert into RANKER values(?, ?)", (your_name, profit))
        conn.commit()
        continue
    elif last==3:
        print("\n순위를 삭제합니다")
        your_name=input("이름을 입력하세요 : ")
        cursor.execute("delete from RANKER where name=(?)",(your_name,))
        conn.commit()
        continue
    elif last==4:
        print("\n프로그램을 종료합니다 \n이용해주셔서 감사합니다 ^^")     
        break
cursor.close()
conn.close()


