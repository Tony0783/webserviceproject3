# 프로젝트 설명
이 프로젝트는 Saramin 데이터를 이용한 구직 관련 웹 서비스입니다. MongoDB를 사용하여 데이터를 저장하고, Flask를 이용해 백엔드를 구성하였으며 JCloud에 배포되었습니다.

---

## 목차
1. [요구 사항](#요구-사항)
2. [설치 및 실행 방법](#설치-및-실행-방법)
3. [빌드 명령어](#빌드-명령어)
4. [API 문서](#api-문서)
5. [기타 정보](#기타-정보)

---

## 요구 사항
- Python: 3.9 이상
- MongoDB: 6.0 이상
- Flask: 최신 버전
- 의존성: `requirements.txt` 파일에 명시

## 설치 및 실행 방법

### 1. 가상환경 설정 및 패키지 설치


# 가상환경 생성 및 활성화
```bash
cd ~/python\ 크롤러\ 실습/ 
source ~/venv/bin/activate
```  

# 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. MongoDB 데이터 추가
```bash
mongorestore --host localhost --port 8080 --db job_data --dir ~/backup/job_data/
```

### 서버 실행
다음 명령어로 Flask 서버를 실행합니다:

```bash
nohup authbind --deep flask run --host=0.0.0.0 --port=443 &
```

### 4. 배포된 서버 접속
JCloud 서버에 배포된 서비스에 접속합니다:

- **URL:** `http://113.198.66.75:17021/`

---

## API 문서
API에 대한 자세한 설명은 Swagger UI를 통해 확인할 수 있습니다. 

- **Swagger URL:** `http://113.198.66.75:17021/apidocs/#/`

API 엔드포인트
프로젝트에서 제공하는 API 엔드포인트 목록은 다음과 같습니다:


1. 지원 내역 조회 API
설명: 사용자의 지원 내역을 조회합니다.

2. 지원 취소 API 
설명: 특정 채용 공고에 대한 지원을 취소합니다
요청 경로 변수: job_id (지원 취소할 공고 ID)

3. 채용 공고 지원 API
설명: 특정 채용 공고에 지원합니다.

4. 로그인 API

설명: 사용자가 로그인합니다.

{
  "email": "user@example.com",
  "password": "password123"
}
응답 예시:
{
  "token": "jwt_token_here"
}
5. 회원 프로필 조회 API

설명: 로그인한 사용자의 프로필 정보를 조회합니다.

6. 회원 가입 API

설명: 새로운 사용자를 등록합니다.
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "password123"
}
{
  "message": "User registered successfully"
}

7. 북마크 조회 API

설명: 사용자가 저장한 북마크 목록을 조회합니다.

8. 북마크 제거 API

설명: 특정 채용 공고를 북마크에서 삭제합니다.

9. 북마크 추가 API

설명: 특정 채용 공고를 북마크에 추가합니다.


10. 채용 공고 조회 API

설명: 모든 채용 공고를 조회합니다.

11. 채용 공고 추천 API

설명: 사용자에게 추천되는 채용 공고를 제공합니다.

12. 채용 공고 추가 API

설명: 새로운 채용 공고를 추가합니다.

13. 채용 공고 삭제 API

설명: 특정 채용 공고를 삭제합니다.

14. 채용 공고 수정 API

설명: 특정 채용 공고를 수정합니다.


---

## 기타 정보
프로젝트에 대한 추가 정보는 `README.md` 파일이나 해당 프로젝트의 GitHub 페이지를 참조하세요.
