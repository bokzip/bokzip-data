# 분류별 검색 > 장애인 복지 검색결과 데이터 크롤링
# 크롤링을 위한 모듈 import
from selenium import webdriver
import time
import pandas as pd

#w = pd.ExcelWriter('./bokji_center.xlsx') # 'bokji_center'라는 파일명으로 엑셀 파일 작성 예정
path = 'D:/Workspace/bokzip/크롤링/chromedriver.exe' # 크롬 드라이버 경로 (절대 or 상대 경로 상관 없음)
driver = webdriver.Chrome(path)
url = 'http://bokjiro.go.kr/welInfo/retrieveWelInfoBoxList.do' # 크롤링할 페이지의 url
driver.get(url) # url로 이동
time.sleep(1) # 페이지 로딩 시간 기다리기

# db 컬럼명과 동일, db에 없는 컬럼은 새로 추가해야할 컬럼
titles = [] # 타이틀
categories = [] # 생활, 고용, 건강, 교육 분야에 해당
urls = [] # 상세 페이지 url
targets = [] # 서비스 대상
criterias = [] # 선정 기준
contents = [] # 서비스 내용
howToApply = [] # 신청 방법
contacts = [] # 문의
sites = [] # 사이트

# 장애인 버튼 클릭
driver.find_element_by_xpath(f'//*[@id="catCenterColor"]/li[1]/a').click()
time.sleep(1)

# 분야별 버튼 클릭 (생활 : 28, 고용 : 29, 건강 : 30, 교육 : 31) 
for category in range(28,32):
    d = driver.find_element_by_xpath(f'//*[@id="link_0{category}"]')
    category_name = d.text # 현재 분야를 category_name에 저장, categories에 저장하기 위함
    d.click()
    time.sleep(1)
    
    # 50개씩 보기 클릭 (*)
    driver.find_element_by_xpath(f'//*[@id="pageUnit"]/option[2]').click()
    time.sleep(1)
    
    # 확인 버튼 클릭
    driver.find_element_by_xpath(f'//*[@id="contents"]/div[3]/div[2]/div[2]/fieldset/a/span')click()
    time.sleep(2)
    
    # 복지 정보 가져오기
    for item in range(1,40): # 한 분야 당 한 페이지에서 50개의 복지 아이템이 보여지도록 설정(*)했으나, 최대 40건을 넘지 않음(생활지원 복지가 가장 많으며, 건수는 36건임. 넉넉하게 40으로 잡음)
        try:
            # 아이템 클릭
            d = driver.find_element_by_xpath(f'//*[@id="contents"]/div[4]/ul/li[{item}]/div/dl/dt/a')
            titles.append(d.text) # 아이템 클릭 전 아이템의 타이틀을 저장
            d.click()
            time.sleep(1)
            categories.append(category_name) # 위에서 저장한 category명을 저장
            urls.append(driver.current_url) # 상세 페이지 url을 저장
            
            # 상세 내용 읽기, 데이터 없는 경우 예외처리(None값 넣기)
            # 지원 대상 (target)
            try:
                targets.append(driver.find_element_by_xpath('//*[@id="backup"]/div[1]/div/ul/li[1]/ul').text)
            except:
                targets.append(None)     
            # 선정기준 
            try:
                criterias.append(driver.find_element_by_xpath('//*[@id="backup"]/div[1]/div/ul/li[2]/ul').text)
            except:
                criterias.append(None)
            # 지원내용 (content)
            try:
                contents.append(driver.find_element_by_xpath('//*[@id="backup"]/div[2]/div/ul/li/ul').text)
            except:
                contents.append(None)
            # 신청방법 (howToApply)
            try:
                howToApply.append(driver.find_element_by_xpath('//*[@id="backup"]/div[3]/div/ul[1]/li[1]/ul').text)
            except:
                howToApply.append(None)  
            # 문의처 (contact)
            try:
                contacts.append(driver.find_element_by_xpath('//*[@id="contents"]/div[4]/div[2]/div/div/ul/li[1]/ul').text)
            except:
                contacts.append(None)
            # 관련사이트 (site)
            try:
                sites.append(driver.find_element_by_xpath('//*[@id="contents"]/div[4]/div[2]/div/div/ul/li[2]/ul').text)
            except:
                sites.append(None)  
            
            time.sleep(2)
            driver.back() # 뒤로 가기
            
        except:
            break

# 엑셀에 크롤링한 데이터를 저장하기 위해 데이터 프레임(표 구조와 비슷) 생성
df = pd.DataFrame(
    {'title' : titles,
     'category' : categories,
     'qpplyUrl' : urls,
     'target' : targets,
     'criteria' : criterias,
     'content' : contents,
     'howToApply' : howToApply,
     'contact' : contacts,  
     'site' : sites},
    )
    
# 카테고리명으로 시트명 지정(카테고리별로 시트를 구분 위함)해서 수집한 데이터(df)를 엑셀에 저장하기
df.to_csv('bokji_center.csv', encoding='cp949')
# df.to_excel(w)
time.sleep(1)
driver.quit() # 크롬 창 끄기
#w.save() #엑셀에 데이터 저장