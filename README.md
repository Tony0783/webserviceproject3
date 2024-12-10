# webserviceproject3
이 프로젝트는 Saramin 데이터를 이용한 구직 관련 웹 서비스입니다. MongoDB를 사용하여 데이터를 저장하고, Flask를 이용해 백엔드를 구성하였으며 JCloud에 배포되었습니다.

목차
요구 사항
설치 및 실행 방법
빌드 명령어
API 문서
기타 정보
요구 사항
Python: 3.9 이상
MongoDB: 6.0 이상
Flask: 최신 버전
의존성: requirements.txt 파일에 명시
설치 및 실행 방법
1. 프로젝트 복제
GitHub에서 프로젝트를 클론합니다:

bash
코드 복사
git clone <GitHub_Repository_URL>
cd <프로젝트_폴더>
2. 가상환경 설정 및 패키지 설치
bash
코드 복사
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
3. MongoDB 데이터 복원
로컬 MongoDB에 데이터를 복원하려면:

bash
코드 복사
mongorestore --host localhost --port 27017 --db job_data --dir ./backup/job_data/
4. 서버 실행
다음 명령어로 서버를 실행합니다:

bash
코드 복사
nohup authbind --deep flask run --host=0.0.0.0 --port=443 &
