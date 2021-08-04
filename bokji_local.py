# 지역별 검색 > 장애인 > 지역(17개) > 지자체 복지 검색결과 데이터 크롤링
# 크롤링을 위한 모듈 import
from selenium import webdriver
import time
import pandas as pd

# 복지 상세 조회 페이지에서 내용 전체 읽기
def readFullContent():
    for item in range(1,101): # 한 페이지당 100개의 리스트가 존재
        try:
            # 지자체
            category_name = driver.find_element_by_xpath(f'//*[@id="contents"]/div[4]/ul/li[{item}]/div/dl/dt/span[2]').text
            categories.append(category_name)
            
            # 하나의 복지 정보를 클릭
            d = driver.find_element_by_xpath(f'//*[@id="contents"]/div[4]/ul/li[{item}]/div/dl/dt/a')
            titles.append(d.text) # 복지정보 클릭 전 타이틀 저장
            d.click() # 복지정보 클릭
            time.sleep(1) 
            urls.append(driver.current_url) # 페이지 로딩 시간 기다리기
            
            # 상세 내용 읽기
            d = driver.find_element_by_xpath(f'//*[@id="contents"]/div[3]/div[1]')
            refineData(d.text) # 읽은 데이터를 db에 넣기 위해 정제
            
            time.sleep(2)
            driver.back() # 뒤로 가기
        except:
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
    targets.append('\n'.join(test[1:contentIdx])) # 서비스 대상
    contents.append('\n'.join(test[contentIdx+1:howToIdx])) # 서비스 내용
    howToApply.append('\n'.join(test[howToIdx+1:contactIdx])) # 서비스 이용 및 신청방법
    
    # 사이트 존재 여부에 따른 예외처리 (다른 항목들은 모두 존재하고 사이트만 없는 경우가 있음)
    if siteIdx != -1: # 사이트가 존재하는 경우
        contacts.append('\n'.join(test[contactIdx+1:siteIdx])) # 문의
        sites.append('\n'.join(test[siteIdx+1:lawIdx])) # 사이트
    else: # 사이트가 존재하지 않는 경우
        sites.append(None) # None 값 넣기
        contacts.append('\n'.join(test[contactIdx+1:lawIdx])) # 문의

# 메인
if __name__=="__main__":
    w = pd.ExcelWriter('./bokji_local.xlsx') # 'bokji_local'이라는 파일명으로 엑셀 파일 작성 예정
    path = 'D:/Workspace/bokzip/크롤링/chromedriver.exe' # 크롬 드라이버 경로 (절대 or 상대 경로 상관 없음)
    driver = webdriver.Chrome(path)
    url = 'http://bokjiro.go.kr/welInfo/retrieveLcgWelInfoList.do' # 크롤링할 페이지의 url
    driver.get(url)
    time.sleep(1) # 페이지 로딩 시간 기다리기
    
    # 장애인 버튼 클릭  
    driver.find_element_by_xpath(f'//*[@id="contents"]/div[2]/div[1]/div/fieldset/div/a').click() # 장애인 버튼 클릭 전 select box를 열기 위해 화살표버튼을 클릭
    driver.find_element_by_xpath(f'//*[@id="contents"]/div[2]/div[1]/div/fieldset/div/div/div/ul/li[7]/label').click() # 장애인 버튼 클릭
    time.sleep(1)
    
    # 지자체 클릭
    driver.find_element_by_xpath(f'//*[@id="searchCnDivCd"]/option[2]').click() # 주체기관(중앙기관, 중앙기관+지자체, 지자체) 중 지자체 클릭
    time.sleep(1)
    
    # 100개씩 보기 클릭 
    driver.find_element_by_xpath(f'//*[@id="pageUnit"]/option[3]').click() # 페이지 전환을 줄이기 위함 (default : 10개씩 보기)
    time.sleep(1)
    
    for area in range(2,19): # 17개(서울 ~ 제주) 지역 선택
        titles = [] # 타이틀
        categories = [] # 지역명
        urls = [] # 상세조회 url
        targets = [] # 서비스 대상
        contents = [] # 서비스 내용
        howToApply = [] # 신청 방법
        contacts = [] # 문의
        sites = [] # 관련 사이트
    
        # 지역 클릭 (서울 : 2, ..., 제주 : 18)
        d = driver.find_element_by_xpath(f'//*[@id="searchSidoCode"]/option[{area}]')
        sheetName = d.text # 엑셀 파일의 시트명으로 지역명으로 설정
        d.click()
        time.sleep(1)
        
        # 검색 클릭
        driver.find_element_by_xpath(f'//*[@id="contents"]/div[2]/div[1]/div/fieldset/a/span').click()
        time.sleep(1)
        
        readFullContent() # 1페이지의 100개의 리스트에 대해 상세 조회 페이지 내용 읽음
      
        try: # 2페이지가 있는 경우 2페이지를 클릭
            driver.find_element_by_xpath(f'//*[@id="contents"]/div[4]/div/a/span').click()
            time.sleep(1)
            readFullContent()
        except:
            time.sleep(1)
        
        # 엑셀에 크롤링한 데이터를 저장하기 위해 데이터 프레임(표 구조와 비슷) 생성
        df = pd.DataFrame(
        {'title' : titles,
         'category' : categories,
         'qpplyUrl' : urls,
         'target' : targets,
         'content' : contents,
         'howToApply' : howToApply,
         'contact' : contacts,  
         'site' : sites},
        )
        
        # 현재 지역명을 시트명으로 지정(지역별로 시트를 구분하기 위해)해서 수집한 데이터(df)를 엑셀로 변환
        df.to_excel(w,sheet_name=sheetName)
    
    time.sleep(1)
    driver.quit() # 크롬창 끄기
    w.save() # 엑셀에 최종 저장