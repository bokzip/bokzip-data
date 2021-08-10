# 크롤링을 위한 모듈 import
from selenium import webdriver
import time
import pandas as pd
from selenium.webdriver.common.keys import Keys # 크롤링 중 자동 스크롤 하기 위함

# 복지 상세 조회 페이지에서 내용 전체 읽기
def readFullContent(cnt, idx):
    for item in range(1,21): # 한 페이지당 20개의 리스트가 존재 // 21
        print(idx+item)
        
        for i in range(cnt):
            try: # 더보기가 있는 경우 클릭
                driver.find_element_by_xpath(f'//*[@id="dvMoreList"]/a').click()
                time.sleep(1)
            except:
                print('error1')
                break
        try:
            # 하나의 복지 정보를 클릭
            d = driver.find_element_by_xpath(f'//*[@id="moreList"]/li[{idx+item}]/a/span')
            titles.append(d.text) # 복지정보 클릭 전 타이틀 저장
            d.click() # 복지정보 클릭
            time.sleep(1)
            urls.append(driver.current_url) # 페이지 로딩 시간 기다리기
            # 지자체명 읽기
            category_name = driver.find_element_by_xpath(f'//*[@id="frm"]/div/div[1]/div[1]/div/strong').text
            categories.append(category_name)
                
            # 상세 내용 읽기
            d = driver.find_element_by_xpath(f'//*[@id="frm"]/div/div[1]/div[3]')
            time.sleep(1)
            refineData(d.text) # 읽은 데이터를 db에 넣기 위해 정제
            driver.back() # 뒤로 가기
        except:
            print('error2')
            break


# 데이터 정제(db에 넣기 위함)
def refineData(fullContent):
    test = fullContent.split('\n') # 내용을 모두 가져왔기 때문에 줄바꿈 단위로 내용 분할해서 한 라인 씩 배열의 요소로 저장
    # 배열 요소 중 <br>태그 값(빈문자열)을 제거
    for _ in test :
        try:
            test.remove('')
        except:
            break
            
    # 단락 구분을 위한 슬라이싱 준비 (슬라이싱을 범위를 구하기 위해 소제목 인덱스 찾기)        
    try :
        contentIdx = test.index("서비스 내용") # "서비스 내용"(소제목)이 시작하는 위치
    except:
        contentIdx = -1 # # "서비스 내용"이 없는 경우 인덱스를 -1로 설정
                
    try :
        howToIdx = test.index("서비스 이용 및 신청방법") # "서비스 이용 및 신청방법 단락"이 시작하는 위치
    except:
        howToIdx = -1
    try :
        docIdx = test.index("서식/자료") # "서식/자료 단락"이 시작하는 위치
    except:
        docIdx = -1
    try :
        contactIdx = test.index("문의") # "문의" 단락이 시작하는 위치
    except:
        contactIdx = -1
    try :
        siteIdx = test.index("사이트") # "사이트" 단락이 시작하는 위치
    except:
        siteIdx = -1
    try :
        lawIdx = test.index("근거법령") # "근거법령" 단락이 시작하는 위치
    except:
        lawIdx = -1
            
    '''
        # 소제목을 제외하고 내용만 각 배열에 추가
    '''
    try:
        targets.append('\n'.join(test[1:contentIdx])) # 서비스 대상
        contents.append('\n'.join(test[contentIdx+1:howToIdx])) # 서비스 내용
        howToApply.append('\n'.join(test[howToIdx+1:docIdx])) # 서비스 이용 및 신청방법
        
        # 문의(문의 뒤에 보통 사이트가 나오는데, 사이트가 없는 경우는 근거법령이 나옴)
        if siteIdx != -1:
            contacts.append('\n'.join(test[contactIdx+1:siteIdx])) # 문의
        else:
            contacts.append('\n'.join(test[contactIdx+1:lawIdx])) # 문의
    except:
        print('error3')

# 메인
if __name__=="__main__":
    w = pd.ExcelWriter('./bokji_local.xlsx') # '지자체복지'이라는 파일명으로 엑셀 파일 작성 예정
    path = 'D:/Workspace/bokzip/크롤링/chromedriver.exe' # 크롬 드라이버 경로 (절대 or 상대 경로 상관 없음)
    driver = webdriver.Chrome(path)
    url = 'http://m.bokjiro.go.kr/welInfo/retrieveLcgWelInfoList.do?searchIntClId=&searchCtgId=&welInfSno=&pageGb=1&pageIndex=1&pageUnit=5' # 크롤링할 페이지의 url
    driver.get(url)
    time.sleep(1) # 페이지 로딩 시간 기다리기
    
    # 지자체 클릭
    driver.find_element_by_xpath(f'//*[@id="page"]/div[3]/div[2]/fieldset/div/div[1]/div/select/option[2]').click() # 주체기관(중앙기관, 중앙기관+지자체, 지자체) 중 지자체 클릭
    time.sleep(1) 
    
    # 100개씩 보기 클릭 
    #driver.find_element_by_xpath(f'//*[@id="pageUnit"]/option[3]').click() # 페이지 전환을 줄이기 위함 (default : 10개씩 보기)
    #time.sleep(1)
    
    for area in range(2,4): # 17개(서울 ~ 제주) 지역 선택 // 19
        titles = [] # 타이틀
        categories = [] # 지역명
        urls = [] # 상세조회 url
        targets = [] # 서비스 대상
        contents = [] # 서비스 내용
        howToApply = [] # 신청 방법
        contacts = [] # 문의 
        # 지역 클릭 (서울 : 2, ..., 제주 : 18)
        d = driver.find_element_by_xpath(f'//*[@id="searchSidoCode"]/option[{area}]')
        sheetName = d.text # 엑셀 파일의 시트명으로 지역명으로 설정
        d.click()
        time.sleep(1)
            
        # 장애인 버튼 클릭  
        driver.find_element_by_xpath(f'//*[@id="page"]/div[2]/div/div[2]/div[1]/div[1]/div/button').click() # 장애인 버튼 클릭 전 select box를 열기 위해 화살표버튼을 클릭
        driver.find_element_by_xpath(f'//*[@id="chb07"]').click() # 장애인 버튼 클릭
        time.sleep(1)
            
        # 검색 클릭
        driver.find_element_by_xpath(f'//*[@id="btnGo"]').click()
        time.sleep(1)
        
        for more in range(7): # 모바일 url의 경우 20개씩 보여주고 더보기 버튼이 나옴 복지정보 건수 131개로 가장 많은 경기도를 기준으로 더보기 버튼 7번 눌러야함 //121
            readFullContent(more, more*20) # 1페이지의 100개의 리스트에 대해 상세 조회 페이지 내용 읽음
            #driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            #driver.find_element_by_xpath(f'//*[@id="dvMoreList"]/a').click()
            #time.sleep(2)
            
        # 엑셀에 크롤링한 데이터를 저장하기 위해 데이터 프레임(표 구조와 비슷) 생성
        df = pd.DataFrame(
        {'title' : titles,
        'category' : categories,
        'qpplyUrl' : urls,
        'target' : targets,
        'description' : contents,
        'howToApply' : howToApply,
        'contact' : contacts},
        )
            
        # 현재 지역명을 시트명으로 지정(지역별로 시트를 구분하기 위해)해서 수집한 데이터(df)를 엑셀로 변환
        df.to_excel(w,sheet_name=sheetName)
    
    time.sleep(1)
    driver.quit() # 크롬창 끄기
    w.save() # 엑셀에 최종 저장