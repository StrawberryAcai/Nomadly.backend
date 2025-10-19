# Plan Visibility API 테스트 가이드

## 🎯 테스트 방법

### 방법 1: 인터랙티브 스크립트 사용 (추천)

```bash
./test_plan_visibility.sh
```

스크립트 실행 후 다음을 입력하세요:
1. JWT 토큰 (로그인 시 받은 토큰)
2. Plan ID (변경할 plan의 UUID)
3. 공개 여부 (1: public, 2: private)

---

### 방법 2: 직접 curl 명령어 사용

#### ✅ Private으로 변경 (비공개)
```bash
curl -X PATCH "http://localhost:8000/api/plan/visibility" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "plan_id": "YOUR_PLAN_ID_HERE",
    "visibility": "private"
  }'
```

#### ✅ Public으로 변경 (공개)
```bash
curl -X PATCH "http://localhost:8000/api/plan/visibility" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "plan_id": "YOUR_PLAN_ID_HERE",
    "visibility": "public"
  }'
```

---

### 방법 3: 상세 정보 포함 (디버깅용)
```bash
curl -v -X PATCH "http://localhost:8000/api/plan/visibility" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "plan_id": "YOUR_PLAN_ID_HERE",
    "visibility": "private"
  }'
```

---

## 📝 예상 응답

### ✅ 성공 (200 OK)
```json
{
  "plan_id": "123e4567-e89b-12d3-a456-426614174000",
  "visibility": "public",
  "success": true
}
```

### ❌ 실패 사례

#### 1. 인증 없음 (401 Unauthorized)
```json
{
  "detail": "Authorization required"
}
```

#### 2. 권한 없음 (403 Forbidden)
```json
{
  "detail": "You are not the owner of this plan"
}
```

#### 3. Plan 없음 (404 Not Found)
```json
{
  "detail": "Plan not found"
}
```

#### 4. 서버 오류 (500 Internal Server Error)
```json
{
  "detail": "Failed to update visibility: ..."
}
```

---

## 🔑 JWT 토큰 얻는 방법

### 로그인 API 호출
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your_email@example.com",
    "password": "your_password"
  }'
```

응답에서 `access_token` 또는 `token` 필드의 값을 사용하세요.

---

## 🧪 테스트 시나리오

### 1. 기본 테스트
```bash
# 1) Plan 생성
curl -X POST "http://localhost:8000/api/plan" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{...plan_data...}'

# 2) 생성된 plan_id로 private → public 변경
curl -X PATCH "http://localhost:8000/api/plan/visibility" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "plan_id": "CREATED_PLAN_ID",
    "visibility": "public"
  }'
```

### 2. 권한 테스트 (다른 사용자의 plan 변경 시도)
```bash
# 다른 사용자 토큰으로 변경 시도 → 403 에러 예상
curl -X PATCH "http://localhost:8000/api/plan/visibility" \
  -H "Authorization: Bearer ANOTHER_USER_TOKEN" \
  -d '{
    "plan_id": "SOMEONE_ELSE_PLAN_ID",
    "visibility": "public"
  }'
```

### 3. 유효하지 않은 plan_id 테스트
```bash
curl -X PATCH "http://localhost:8000/api/plan/visibility" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "plan_id": "00000000-0000-0000-0000-000000000000",
    "visibility": "public"
  }'
```

---

## 🌐 Swagger UI에서 테스트

1. 브라우저에서 `http://localhost:8000/docs` 접속
2. 우측 상단 **Authorize** 🔓 버튼 클릭
3. JWT 토큰 입력 (Bearer 접두사 없이)
4. **PATCH /api/plan/visibility** 엔드포인트 찾기
5. **Try it out** 클릭
6. Request body 입력:
   ```json
   {
     "plan_id": "your-plan-id",
     "visibility": "public"
   }
   ```
7. **Execute** 클릭

---

## 🛠️ 트러블슈팅

### 문제: "Authorization required"
- JWT 토큰이 누락되었거나 형식이 잘못됨
- 해결: `Authorization: Bearer <token>` 헤더 확인

### 문제: "You are not the owner of this plan"
- 다른 사용자의 plan을 변경하려고 시도
- 해결: 본인이 생성한 plan의 ID 사용

### 문제: "Invalid token: user_id not found"
- JWT 토큰에 user_id 정보가 없음
- 해결: 로그인 API로 새 토큰 발급

### 문제: Connection refused
- 서버가 실행 중이 아님
- 해결: `python main.py` 또는 `uvicorn main:app --reload` 실행

---

## 📊 데이터베이스 확인

```sql
-- Plan의 현재 공개 여부 확인
SELECT id, private, author, start_date, end_date 
FROM plan 
WHERE id = 'YOUR_PLAN_ID';

-- 특정 사용자의 모든 plan 확인
SELECT id, private, start_date, end_date 
FROM plan 
WHERE author = 'USER_ID'
ORDER BY start_date DESC;
```

---

## 🔍 로그 확인

```bash
# 서버 로그에서 에러 확인
tail -f logs/server.log

# 또는 uvicorn 실행 시 콘솔에서 직접 확인
```
