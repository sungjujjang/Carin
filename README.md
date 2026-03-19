# Carin - 택시 동승(카풀) 플랫폼

Carin은 목적지가 같은 사람들끼리 택시를 같이 타고 비용을 절감하며, 대기 오염을 줄이기 위한 카풀/택시 동승 서비스입니다.

## 🚀 프로젝트 개요
- **목적**: 교통비 감소, 여러 자동차로 인해 배출되는 대기 오염 가스 줄이기를 위해 출발/목적지가 같은 사람들끼리 택시 동승(택시팟)을 더 쉽게 하기 위해서 제작되었습니다.
- **목표 고객**: 대학생, 고등학생 등 기숙사에서 대전역과 같이 출발지/목적지가 공통인 사람들.

## ✨ 주요 기능

### 1. 계정 관리
- **로그인/회원가입**: Django의 Auth 모델을 사용한 사용자 인증.
- **마이페이지**: 본인 정보 확인 및 수정 (이름, 비밀번호 등).

### 2. 방 관리 (택시팟)
- **방 생성**: 출발지, 목적지, 최대 인원, 출발 시간 등을 설정하여 방 생성.
- **방 참여/나가기**: 참여 중인 방 관리. 마지막 인원이 나갈 시 방 자동 삭제.
- **현재 방 표시**: 내가 참여 중인 방 정보를 실시간으로 확인.

### 3. 지도 및 부가 기능
- **지도 표시**: Kakao Map API를 사용하여 출발지와 목적지를 시각화.
- **주소 자동 변환**: 좌표(위도, 경도)를 실제 주소로 변환하여 표시.
- **예상 택시 요금**: Kakao Route API를 기반으로 예상 요금을 미리 확인.
- **알림 (WebPush)**: 출발 30분 전 푸시 알림 기능 제공.

## 🛠 기술 스택
- **Backend**: Python 3.x, Django 6.0
- **Database**: SQLite3
- **Frontend**: Vanilla JS (Kakao Map API integration)
- **External API**: Kakao Local API, Kakao Route API
- **Others**: Django WebPush

## 🏁 시작하기

### 1. 필수 프로그램
- Python 3.x
- Django

### 2. 설치 및 실행
```bash
# 가상환경 생성 (선택)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필수 패키지 설치
pip install django requests django-webpush

# 데이터베이스 마이그레이션
python manage.py migrate

# 서버 실행
python manage.py runserver
```

---
*본 서비스는 적법한 선인 개인 택시를 같이 탈 수 있도록 연결해주는 서비스입니다.*
*알림 기능을 사용하기 위해 https 사용이 필요합니당*
