# unsplash에서 썸네일 이미지 크롤링
# 크롤링을 위한 모듈 import
from selenium import webdriver
import time
import pandas as pd
from selenium.webdriver.common.keys import Keys # 크롤링 중 자동 스크롤 하기 위함

# 이미지 url 읽어서 반환
def readImgUrl(n,col):
    urls = []
    for i in range(1, n): # 1~ n-1까지 반복
        #success = False
        try: # 이미지 태그에서 src 속성값(이미지 url) 읽기
            d = driver.find_element_by_xpath(f'//*[@id="app"]/div/div[2]/div[3]/div/div[1]/div/div/div[{col}]/figure[{i}]/div/div[1]/div/div/a/div/div[2]/div/img').get_attribute("src")
            urls.append(d);
            #success = True
            scrollPage() # 태그 하나 읽고 스크롤 내리기
            time.sleep(1) # 페이지 로딩 시간 기다리기
        except: # 예외 발생 시 현재 이미지 태그 건너뛰기
            continue
            #print(col, 'i : ', i, ', ', success)
    
    return urls

# 스크롤 내리기
def scrollPage(): 
    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
 
# 메인
if __name__=="__main__":
    w = pd.ExcelWriter('./thumbnail.xlsx') # 'thumbnail'이라는 파일명으로 엑셀 파일 작성 예정
    path = 'D:/Workspace/bokzip/크롤링/chromedriver.exe' # 크롬 드라이버 경로 (절대 or 상대 경로 상관 없음)
    driver = webdriver.Chrome(path)
    driver.maximize_window() # 창 최대화
    keywords = {0:'home', 1:'work', 2:'health', 3:'education', 4:'happiness', 5:'cozy', 6:'life'} # {인덱스번호:검색키워드} : 7개 키워드는 unsplash에서 해당 키워드 검색 시 검색결과가 많은 것(디스플레이되는 이미지가 한 컬럼에 대략 100개 이상인 것 )으로 선정
    
    for i in range(len(keywords)):
        urls = []
        url = f'https://unsplash.com/s/photos/{keywords[i]}?orientation=portrait'  # 위 키워드로 검색 및 사진 방향을 세로로 선택한 url
        driver.get(url) # url로 이동
        time.sleep(3) # 페이지 로딩 시간 기다리기
        
        if i < 4: # 중앙부처(국가)의 4대 지원 카테고리에 해당하는 키워드(home, work, health, education)인 경우, 한 키워드당 총 100개의 이미지 읽기, 실제로는 예외(보여지는 화면에서 태그의 부재)발생으로 인해 대략 90개를 가져옴
            urls = readImgUrl(51,2) # 2번컬럼에서 이미지 50개 읽기
            driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME) # 맨위로 스크롤 (다시 처음으로)
            urls += readImgUrl(51,3) # 3번컬럼에서 이미지 50개 읽기
        else: # 그외의 키워드는 지자체(지역별) 지원에 해당하는 썸네일로 간주, 한 키워드당 총 375개의 이미지 읽기, 마찬가지로 예외(보여지는 화면에서 태그의 부재)발생으로 인해 대략 330개를 가져옴
            scrollPage()
            urls = readImgUrl(126,1) # 1번컬럼에서 이미지 125개 읽어오기
            driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
            
            urls += readImgUrl(126,2) # 2번컬럼에서 이미지 125개 읽어오기
            driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)

            urls += readImgUrl(126,3) # 3번컬럼에서 이미지 125개 읽어오기
           
        df = pd.DataFrame( # 엑셀에 크롤링한 데이터를 저장하기 위해 한 키워드 별로 데이터 프레임(표 구조와 비슷) 생성
            {'thumbnail' : urls} # row : 자동 인덱스(0 ~ urls.length - 1), col : thumbnail, value : urls 요소
            )
    
        # 엑셀 시트명 지정(키워드 별로 시트를 구분하기 위함)해서 수집한 데이터(df)를 엑셀로 변환
        sheet_name = keywords[i]
        df.to_excel(w,sheet_name=sheet_name)
        
    time.sleep(1)
    driver.quit() # 크롬창 끄기
    w.save() #엑셀 최종 저장