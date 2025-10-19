#!/bin/bash

# Plan Visibility 변경 테스트 스크립트
# 사용법: ./test_plan_visibility.sh

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Plan Visibility 테스트 ===${NC}\n"

# 환경 변수 설정
BASE_URL="http://localhost:8000"

# 1. JWT 토큰 입력받기
echo -e "${YELLOW}1. JWT 토큰을 입력하세요:${NC}"
read -r JWT_TOKEN

if [ -z "$JWT_TOKEN" ]; then
    echo -e "${RED}오류: JWT 토큰이 필요합니다.${NC}"
    exit 1
fi

# 2. Plan ID 입력받기
echo -e "\n${YELLOW}2. 변경할 Plan ID를 입력하세요:${NC}"
read -r PLAN_ID

if [ -z "$PLAN_ID" ]; then
    echo -e "${RED}오류: Plan ID가 필요합니다.${NC}"
    exit 1
fi

# 3. 공개 여부 선택
echo -e "\n${YELLOW}3. 공개 여부를 선택하세요:${NC}"
echo "1) public (공개)"
echo "2) private (비공개)"
read -r CHOICE

case $CHOICE in
    1)
        VISIBILITY="public"
        ;;
    2)
        VISIBILITY="private"
        ;;
    *)
        echo -e "${RED}오류: 1 또는 2를 선택해주세요.${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}=== 요청 정보 ===${NC}"
echo "URL: ${BASE_URL}/api/plan/visibility"
echo "Plan ID: ${PLAN_ID}"
echo "Visibility: ${VISIBILITY}"
echo "Token: ${JWT_TOKEN:0:20}..."

# 4. API 호출
echo -e "\n${YELLOW}=== API 호출 중... ===${NC}\n"

RESPONSE=$(curl -s -w "\n%{http_code}" -X PATCH "${BASE_URL}/api/plan/visibility" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -d "{
    \"plan_id\": \"${PLAN_ID}\",
    \"visibility\": \"${VISIBILITY}\"
  }")

# 응답 파싱
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo -e "${GREEN}HTTP Status Code: ${HTTP_CODE}${NC}"
echo -e "${GREEN}Response Body:${NC}"
echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"

# 5. 결과 판단
echo ""
if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✅ 성공: Plan의 공개 여부가 ${VISIBILITY}로 변경되었습니다.${NC}"
elif [ "$HTTP_CODE" -eq 401 ]; then
    echo -e "${RED}❌ 실패: 인증이 필요합니다. (JWT 토큰 확인)${NC}"
elif [ "$HTTP_CODE" -eq 403 ]; then
    echo -e "${RED}❌ 실패: 권한이 없습니다. (Plan의 소유자가 아닙니다)${NC}"
elif [ "$HTTP_CODE" -eq 404 ]; then
    echo -e "${RED}❌ 실패: Plan을 찾을 수 없습니다.${NC}"
else
    echo -e "${RED}❌ 실패: 서버 오류 (${HTTP_CODE})${NC}"
fi

echo -e "\n${YELLOW}=== 테스트 완료 ===${NC}"
