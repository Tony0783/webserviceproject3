from flask import Flask, jsonify, request
from flasgger import Swagger
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
from bson import ObjectId
from flask_cors import CORS

load_dotenv()  # .env 파일 로드


app = Flask(__name__)
CORS(app)  # CORS 설정 추가

swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Saramin Crawling API",
        "description": "API Documentation for Saramin Crawling",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Bearer token. Example: 'Bearer {token}'"
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ]
})

# MongoDB 연결 설정
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client.job_data  # job_data 데이터베이스 선택

# 각 컬렉션 선택
jobs_collection = db.jobs
users_collection = db.users
applications_collection = db.applications
bookmarks_collection = db.bookmarks
companies_collection = db.companies
job_categories_collection = db.job_categories
logs_collection = db.logs
skills_collection = db.skills

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

@app.route('/')
def home():
    return "Saramin Crawling API", 200

# 데이터 삽입 전 존재 여부 확인 후 삽입
if applications_collection.count_documents({}) == 0:
    applications_data = [
        {
            "_id": ObjectId(),
            "user_id": ObjectId(),  # 사용자 ID
            "job_id": ObjectId(),   # 채용 공고 ID
            "applied_at": datetime.utcnow()
        },
    ]
    applications_collection.insert_many(applications_data)

if bookmarks_collection.count_documents({}) == 0:
    bookmarks_data = [
        {
            "_id": ObjectId(),
            "user_id": ObjectId(),  # 사용자 ID
            "job_id": ObjectId(),   # 채용 공고 ID
            "bookmarked_at": datetime.utcnow()
        },
    ]
    bookmarks_collection.insert_many(bookmarks_data)

if companies_collection.count_documents({}) == 0:
    companies_data = [
        {
            "_id": ObjectId(),
            "name": "(주)바르존",  # 회사 이름
            "industry": "IT",
            "location": "서울",
            "website": "http://example.com"
        },
    ]
    companies_collection.insert_many(companies_data)

if job_categories_collection.count_documents({}) == 0:
    job_categories_data = [
        {
            "_id": ObjectId(),
            "name": "개발자",
            "description": "소프트웨어 개발과 관련된 직무"
        },
    ]
    job_categories_collection.insert_many(job_categories_data)

if jobs_collection.count_documents({}) == 0:
    jobs_data = [
        {
            "_id": ObjectId(),
            "title": "Product Owner",
            "company": "(주)바르존",
            "location": "서울",
            "category_id": ObjectId(),  # job_categories의 ID 참조
            "deadline": "12.26(녹)"
        },
    ]
    jobs_collection.insert_many(jobs_data)

if logs_collection.count_documents({}) == 0:
    logs_data = [
        {
            "_id": ObjectId(),
            "user_id": ObjectId(),  # 사용자 ID
            "action": "로그인",
            "timestamp": datetime.utcnow(),
            "description": "사용자가 로그인했습니다."
        },
    ]
    logs_collection.insert_many(logs_data)

if skills_collection.count_documents({}) == 0:
    skills_data = [
        {
            "_id": ObjectId(),
            "name": "Python",
            "level": "Intermediate"
        },
        {
            "_id": ObjectId(),
            "name": "JavaScript",
            "level": "Advanced"
        },
    ]
    skills_collection.insert_many(skills_data)

# JWT 인증 미들웨어
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token is missing"}), 403

        # "Bearer "를 제거하고 실제 토큰만 가져오기
        if "Bearer " in token:
            token = token.split(" ")[1]

        try:
            # JWT 디코드하여 유효성 검증
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user = users_collection.find_one({"_id": ObjectId(payload['user_id'])})
            if not user:
                return jsonify({"error": "Invalid token"}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 403

        return f(user, *args, **kwargs)
    return decorated

# 채용 공고 전체 조회 API (검색, 필터링 및 페이지네이션 추가)
@app.route('/jobs', methods=['GET'])
def get_jobs():
    """
    채용 공고 조회 API
    ---
    parameters:
      - name: company
        in: query
        type: string
        description: 회사명으로 필터링
      - name: title
        in: query
        type: string
        description: 직무명으로 검색
      - name: page
        in: query
        type: integer
        default: 1
        description: 페이지 번호
      - name: size
        in: query
        type: integer
        default: 10
        description: 페이지 크기
    responses:
      200:
        description: 채용 공고 목록 조회 성공
        schema:
          type: object
          properties:
            jobs:
              type: array
              items:
                type: object
                properties:
                  company:
                    type: string
                    description: 회사 이름
                  title:
                    type: string
                    description: 채용 공고 제목
                  deadline:
                    type: string
                    description: 채용 공고 마감일
            total:
              type: integer
              description: 전체 채용 공고 수
            page:
              type: integer
              description: 현재 페이지 번호
            size:
              type: integer
              description: 현재 페이지의 공고 개수
            total_pages:
              type: integer
              description: 총 페이지 수
    """
    company = request.args.get('company')
    title = request.args.get('title')
    page = int(request.args.get('page', 1))  # 페이지 번호, 기본값은 1
    size = int(request.args.get('size', 10))  # 페이지 크기, 기본값은 10
    sort_by = request.args.get('sort_by', 'deadline')  # 정렬 기준 필드, 기본값은 'deadline'
    order = request.args.get('order', 'asc')  # 정렬 방식, 기본값은 '오름차순'

    query = {}
    if company:
        query['company'] = company
    if title:
        query['title'] = {"$regex": title, "$options": "i"}

    sort_order = 1 if order == 'asc' else -1

    total_jobs = jobs_collection.count_documents(query)
    jobs = list(
        jobs_collection.find(query, {"_id": 0})
        .sort(sort_by, sort_order)
        .skip((page - 1) * size)
        .limit(size)
    )

    response = {
        "jobs": jobs,
        "total": total_jobs,
        "page": page,
        "size": size,
        "total_pages": (total_jobs + size - 1) // size
    }

    return jsonify(response), 200

# 채용 공고 추천 API
@app.route('/jobs/recommend', methods=['GET'])
@token_required
def recommend_jobs(user):
    """
    채용 공고 추천 API
    ---
    responses:
      200:
        description: 추천된 채용 공고 목록
        schema:
          type: object
          properties:
            recommended_jobs:
              type: array
              items:
                type: object
                properties:
                  company:
                    type: string
                    description: 회사 이름
                  title:
                    type: string
                    description: 채용 공고 제목
    """
    bookmarked_jobs = user.get('bookmarks', [])

    if not bookmarked_jobs:
        return jsonify({"message": "No bookmarks found for recommendations"}), 200

    recommendations = set()
    for job_id in bookmarked_jobs:
        job = jobs_collection.find_one({"_id": ObjectId(job_id)})
        if job:
            company = job.get('company')
            title = job.get('title')

            similar_jobs = jobs_collection.find(
                {"$or": [
                    {"company": company},
                    {"title": {"$regex": title, "$options": "i"}}
                ],
                 "_id": {"$ne": ObjectId(job_id)}}
            )

            for similar_job in similar_jobs:
                recommendations.add(similar_job["_id"])

    recommended_jobs = list(jobs_collection.find({"_id": {"$in": list(recommendations)}}, {"_id": 0}))

    return jsonify({"recommended_jobs": recommended_jobs}), 200

# 회원 가입 API
@app.route('/auth/register', methods=['POST'])
def register():
    """
    회원 가입 API
    ---
    parameters:
      - name: email
        in: body
        type: string
        required: true
        description: 사용자 이메일 주소
      - name: name
        in: body
        type: string
        required: true
        description: 사용자 이름
      - name: password
        in: body
        type: string
        required: true
        description: 사용자 비밀번호
    responses:
      201:
        description: 회원 가입 성공
      400:
        description: 잘못된 요청 (필수 필드 누락 또는 이메일 중복)
    """
    data = request.json
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if not email or not name or not password:
        return jsonify({"error": "Missing required fields"}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 400

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user = {
        "email": email,
        "name": name,
        "password": hashed_pw,
        "bookmarks": []
    }
    users_collection.insert_one(user)

    return jsonify({"message": "User registered successfully"}), 201

# 로그인 API
@app.route('/auth/login', methods=['POST'])
def login():
    """
    로그인 API
    ---
    parameters:
      - name: email
        in: body
        type: string
        required: true
        description: 사용자의 이메일 주소
      - name: password
        in: body
        type: string
        required: true
        description: 사용자의 비밀번호
    responses:
      200:
        description: 로그인 성공
        schema:
          type: object
          properties:
            token:
              type: string
              description: JWT 인증 토큰
      400:
        description: 잘못된 요청 (이메일이나 비밀번호 누락)
      401:
        description: 인증 실패 (이메일 또는 비밀번호 불일치)
    """
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = users_collection.find_one({"email": email})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({"error": "Invalid email or password"}), 401

    payload = {
        "user_id": str(user["_id"]),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    return jsonify({"token": token}), 200

# 북마크 API들
@app.route('/bookmarks/<job_id>', methods=['POST'])
@token_required
def add_bookmark(user, job_id):
    """
    북마크 추가 API
    ---
    parameters:
      - name: job_id
        in: path
        type: string
        required: true
        description: 북마크하려는 채용 공고의 ID
    responses:
      200:
        description: 북마크 추가 성공
      400:
        description: 이미 북마크된 경우
      403:
        description: 인증 실패
    """
    if job_id in user.get('bookmarks', []):
        return jsonify({"error": "Job is already bookmarked"}), 400

    users_collection.update_one({"_id": user["_id"]}, {"$push": {"bookmarks": job_id}})
    return jsonify({"message": "Job bookmarked successfully"}), 200

@app.route('/bookmarks/<job_id>', methods=['DELETE'])
@token_required
def remove_bookmark(user, job_id):
    """
    북마크 제거 API
    ---
    parameters:
      - name: job_id
        in: path
        type: string
        required: true
        description: 제거하려는 북마크의 ID
    responses:
      200:
        description: 북마크 제거 성공
      404:
        description: 북마크에 없는 경우
      403:
        description: 인증 실패
    """
    result = users_collection.update_one({"_id": user["_id"]}, {"$pull": {"bookmarks": job_id}})
    if result.modified_count == 0:
        return jsonify({"error": "Job not found in bookmarks"}), 404

    return jsonify({"message": "Job removed from bookmarks"}), 200

@app.route('/bookmarks', methods=['GET'])
@token_required
def get_bookmarks(user):
    """
    북마크 조회 API
    ---
    responses:
      200:
        description: 사용자의 북마크 목록 조회 성공
        schema:
          type: object
          properties:
            bookmarked_jobs:
              type: array
              items:
                type: object
                properties:
                  company:
                    type: string
                    description: 회사 이름
                  title:
                    type: string
                    description: 채용 공고 제목
    """
    job_ids = user.get('bookmarks', [])
    bookmarked_jobs = list(jobs_collection.find({"_id": {"$in": [ObjectId(job_id) for job_id in job_ids]}}, {"_id": 0}))
    return jsonify({"bookmarked_jobs": bookmarked_jobs}), 200

# 프로필 조회 API
@app.route('/auth/profile', methods=['GET'])
@token_required
def profile(user):
    """
    회원 프로필 조회 API
    ---
    responses:
      200:
        description: 회원 프로필 조회 성공
        schema:
          type: object
          properties:
            email:
              type: string
              description: 사용자 이메일
            name:
              type: string
              description: 사용자 이름
            bookmarks:
              type: array
              items:
                type: string
                description: 북마크된 채용 공고 ID
    """
    user_data = {
        "email": user["email"],
        "name": user["name"],
        "bookmarks": user.get("bookmarks", [])
    }
    return jsonify(user_data), 200

# 채용 공고 추가, 수정, 삭제 API
@app.route('/jobs', methods=['POST'])
@token_required
def add_job(user):
    """
    채용 공고 추가 API
    ---
    parameters:
      - name: title
        in: body
        type: string
        required: true
        description: 채용 공고 제목
      - name: company
        in: body
        type: string
        required: true
        description: 회사 이름
      - name: deadline
        in: body
        type: string
        required: true
        description: 마감일
    responses:
      201:
        description: 채용 공고 추가 성공
      400:
        description: 잘못된 요청 (필수 필드 누락)
    """
    new_job = request.json
    if new_job and 'title' in new_job and 'company' in new_job and 'deadline' in new_job:
        jobs_collection.insert_one(new_job)
        return jsonify({"message": "Job added successfully"}), 201
    else:
        return jsonify({"error": "Invalid job data"}), 400

@app.route('/jobs/<job_id>', methods=['PUT'])
@token_required
def update_job(user, job_id):
    """
    채용 공고 수정 API
    ---
    parameters:
      - name: job_id
        in: path
        type: string
        required: true
        description: 수정하려는 채용 공고의 ID
      - name: title
        in: body
        type: string
        description: 채용 공고 제목 (수정할 내용)
      - name: company
        in: body
        type: string
        description: 회사 이름 (수정할 내용)
      - name: deadline
        in: body
        type: string
        description: 마감일 (수정할 내용)
    responses:
      200:
        description: 채용 공고 수정 성공
      400:
        description: 잘못된 요청 (수정할 내용 누락)
      404:
        description: 채용 공고를 찾을 수 없음
    """
    updated_data = request.json
    if not updated_data:
        return jsonify({"error": "Missing update data"}), 400

    result = jobs_collection.update_one({"_id": ObjectId(job_id)}, {"$set": updated_data})
    if result.matched_count == 0:
        return jsonify({"error": "Job not found"}), 404

    return jsonify({"message": "Job updated successfully"}), 200

@app.route('/jobs/<job_id>', methods=['DELETE'])
@token_required
def delete_job(user, job_id):
    """
    채용 공고 삭제 API
    ---
    parameters:
      - name: job_id
        in: path
        type: string
        required: true
        description: 삭제하려는 채용 공고의 ID
    responses:
      200:
        description: 채용 공고 삭제 성공
      404:
        description: 채용 공고를 찾을 수 없음
    """
    result = jobs_collection.delete_one({"_id": ObjectId(job_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Job not found"}), 404

    return jsonify({"message": "Job deleted successfully"}), 200

# 지원하기 기능
@app.route('/apply/<job_id>', methods=['POST'])
@token_required
def apply_job(user, job_id):
    """
    채용 공고 지원 API
    ---
    parameters:
      - name: job_id
        in: path
        type: string
        required: true
        description: 지원하려는 채용 공고의 ID
    responses:
      200:
        description: 채용 공고 지원 성공
      400:
        description: 이미 지원한 경우
    """
    if job_id in user.get('applications', []):
        return jsonify({"error": "Already applied for this job"}), 400

    users_collection.update_one({"_id": user["_id"]}, {"$push": {"applications": job_id}})
    return jsonify({"message": "Job application submitted successfully"}), 200

# 지원 취소 기능
@app.route('/apply/<job_id>', methods=['DELETE'])
@token_required
def cancel_application(user, job_id):
    """
    지원 취소 API
    ---
    parameters:
      - name: job_id
        in: path
        type: string
        required: true
        description: 취소하려는 지원의 ID
    responses:
      200:
        description: 지원 취소 성공
      404:
        description: 지원 내역을 찾을 수 없음
    """
    if job_id not in user.get('applications', []):
        return jsonify({"error": "No application found for this job"}), 404

    users_collection.update_one({"_id": user["_id"]}, {"$pull": {"applications": job_id}})
    return jsonify({"message": "Job application cancelled successfully"}), 200

# 지원 내역 조회 기능
@app.route('/applications', methods=['GET'])
@token_required
def view_applications(user):
    """
    지원 내역 조회 API
    ---
    responses:
      200:
        description: 사용자의 지원 내역 조회 성공
        schema:
          type: object
          properties:
            applications:
              type: array
              items:
                type: object
                properties:
                  company:
                    type: string
                    description: 회사 이름
                  title:
                    type: string
                    description: 채용 공고 제목
    """
    job_ids = user.get('applications', [])
    applications = list(jobs_collection.find({"_id": {"$in": [ObjectId(job_id) for job_id in job_ids]}}, {"_id": 0}))
    
    return jsonify({"applications": applications}), 200

# 서버 실행
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
