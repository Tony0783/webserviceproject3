from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import concurrent.futures
import logging
from selenium.common.exceptions import WebDriverException

# 로그 설정
logging.basicConfig(filename='crawl.log', level=logging.ERROR)

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않고 실행
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36")

# ChromeDriver 경로 설정
chrome_service = Service("C:\\Program Files\\chromedriver.exe")

# 크롤링할 데이터 저장할 리스트
job_list = []
existing_urls = set()

# 크롤링 함수 정의
def crawl_page(page_url):
    try:
        # WebDriver 객체를 각 작업에서 새로 생성
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        driver.get(page_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.item')))
        
        # 페이지 소스 가져와서 파싱
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # 채용 공고 목록 가져오기
        jobs = soup.select('li.item')
        
        for job in jobs:
            # 공고 제목 추출
            title_element = job.select_one('strong.tit')
            title = title_element.text.strip().encode('utf-8', 'ignore').decode('utf-8') if title_element else "제목 정보 없음"
            
            # 회사명 추출
            company_element = job.select_one('span.corp')
            company = company_element.text.strip().encode('utf-8', 'ignore').decode('utf-8') if company_element else "회사 정보 없음"

            # 마감일 추출
            deadline_element = job.select_one('span.date')
            deadline = deadline_element.text.strip().encode('utf-8', 'ignore').decode('utf-8') if deadline_element else "마감일 정보 없음"

            # 데이터 유효성 검사 및 추가
            if isinstance(title, str) and isinstance(company, str) and isinstance(deadline, str):
                job_data = {
                    "title": title,
                    "company": company,
                    "deadline": deadline
                }
                job_list.append(job_data)

    except WebDriverException as e:
        logging.error(f"페이지 접근 실패: {e}")
    finally:
        driver.quit()  # 드라이버 종료

# 병렬 처리 및 크롤링 시작
page_urls = [f"https://www.saramin.co.kr/zf_user/jobs/list/job-category?page={i}" for i in range(1, 6)]  # 첫 5개의 페이지
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(crawl_page, page_urls)

# 최소 100개 이상의 공고가 수집되지 않았을 때 재시도
retry_count = 0
while len(job_list) < 100 and retry_count < 3:
    print(f"100개 이상의 공고를 수집하기 위해 재시도 중... (현재 수집 수: {len(job_list)})")
    retry_count += 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(crawl_page, page_urls)

# 크롤링한 데이터 JSON 파일로 저장
with open('saramin_jobs.json', 'w', encoding='utf-8') as json_file:
    json.dump(job_list, json_file, ensure_ascii=False, indent=4)

print(f"크롤링 완료. 총 {len(job_list)}개의 채용 정보를 수집했습니다.")
