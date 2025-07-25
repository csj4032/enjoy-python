# Enjoy Python - 네이버 블로그 자동화 프로젝트

## 프로젝트 개요
네이버 블로그 자동화를 위한 Python 기반 프로젝트입니다. Selenium을 활용하여 블로그 검색, 좋아요, 댓글 작성, 버디 관리 등의 작업을 자동화합니다.

## 개발 철학 및 원칙
- **TDD 우선**: 모든 기능은 테스트 먼저 작성
- **클린 코드**: 가독성과 유지보수성 최우선
- **모듈화**: 기능별 명확한 분리와 독립성
- **테스트 커버리지 최대화**
- **타입 힌트 적극 활용**: Python 3.12+ 기능 적극 사용
- **비동기 프로그래밍**: asyncio를 통한 고성능 처리
- **예외 처리**: 안전한 오류 처리와 로깅
- **설정 외부화**: 환경변수와 설정 파일 활용
- **문서화 중시**: 각 모듈별 상세한 docstring과 README

## Python 모던 기술 활용
- **Type Hints**: 정적 타입 검사로 코드 품질 향상
- **Async/Await**: 비동기 프로그래밍으로 성능 최적화
- **Dataclasses**: 불변 데이터 클래스 구현
- **Path객체**: pathlib 사용으로 경로 처리 개선
- **Context Managers**: with 문을 통한 리소스 관리
- **F-strings**: 문자열 포맷팅 최적화
- **List/Dict Comprehensions**: 함수형 프로그래밍 스타일
- **Enum Classes**: 상수 관리 개선

## 프로젝트 구조
```
enjoy-python/
├── src/                          # 메인 소스코드
│   ├── blog/                    # 블로그 자동화 모듈
│   │   ├── like_by_*.py        # 좋아요 기능
│   │   ├── reply_by_*.py       # 댓글 기능
│   │   ├── search_for_*.py     # 검색 기능
│   │   └── extract_blog_*.py   # 데이터 추출
│   ├── common/                  # 공통 유틸리티
│   │   ├── llm.py              # LLM 통합 (Gemini, Ollama)
│   │   ├── webs.py             # 웹 자동화 유틸리티
│   │   ├── search.py           # 검색 엔진
│   │   └── utils.py            # 범용 유틸리티
│   ├── config/                  # 설정 관리
│   │   ├── configuration.py    # 메인 설정 클래스
│   │   ├── variables.py        # 환경변수 관리
│   │   └── envs/              # 환경별 설정 파일
│   └── constants.py            # 프로젝트 상수
├── test/                        # 테스트 코드
├── notebook/                    # Jupyter 노트북
└── requirements.txt            # 의존성 관리
```

## 핵심 모듈별 기능

### 1. Blog 자동화 (`src/blog/`)
- **검색 기능**: 
  - `search_for_mobile.py`: 모바일 검색
  - `search_for_pc.py`: PC 검색
- **좋아요 기능**:
  - `like_by_search.py`: 검색 기반 좋아요
  - `like_by_buddy_added.py`: 버디 추가 기반 좋아요
  - `like_by_recommend.py`: 추천 기반 좋아요
- **댓글 기능**:
  - `reply_by_buddy.py`: 버디 댓글
  - `reply_by_url.py`: URL 기반 댓글
- **데이터 추출**:
  - `extract_blog_by_buddy.py`: 버디 블로그 추출
  - `extract_blog_by_url.py`: URL 기반 추출

### 2. 공통 모듈 (`src/common/`)
- **LLM 통합** (`llm.py`): Google Gemini, Ollama 연동
- **웹 자동화** (`webs.py`): Selenium 래퍼 및 유틸리티
- **검색 엔진** (`search.py`): 통합 검색 인터페이스
- **유틸리티** (`utils.py`): 공통 헬퍼 함수

### 3. 설정 관리 (`src/config/`)
- **환경변수 기반 설정**: `.env` 파일 활용
- **브라우저 설정**: Firefox, Edge 프로필 관리
- **API 키 관리**: Naver, Google, X/Twitter API

## 기술 스택
- **Python 3.12+**: 최신 타입 힌트 및 성능 개선
- **Selenium**: 웹 자동화 프레임워크
- **Google Generative AI**: LLM 통합
- **requests**: HTTP 클라이언트
- **beautifulsoup4**: HTML 파싱
- **pandas**: 데이터 처리
- **python-dotenv**: 환경변수 관리
- **pytest**: 테스트 프레임워크
- **faker**: 테스트 데이터 생성

## 코딩 스타일 규칙
- **Type Hints 필수**: 모든 함수와 메서드에 타입 힌트 적용
- **Docstring 작성**: Google 스타일 docstring 사용
- **PEP 8 준수**: 표준 Python 코딩 컨벤션
- **함수형 프로그래밍**: List comprehension, filter, map 적극 활용
- **예외 처리**: 명확한 예외 타입과 메시지
- **로깅 활용**: logging 모듈을 통한 디버깅 정보
- **Context Manager**: 리소스 관리에 with 문 사용
- **비동기 우선**: I/O 작업에 async/await 적용

## 테스트 전략
### 1. 단위 테스트
- **pytest 기반**: 모든 모듈별 독립적 테스트
- **Mock 활용**: 외부 의존성 모킹
- **pytest-mock**: Selenium, API 호출 모킹
- **Coverage 측정**: 코드 커버리지 80% 이상 유지

### 2. 통합 테스트
- **실제 브라우저 테스트**: Selenium을 통한 E2E 테스트
- **API 통합 테스트**: 실제 Naver, Google API 연동 검증
- **데이터 일관성**: 실제 환경과 동일한 조건에서 테스트

### 3. 성능 테스트
- **비동기 처리 검증**: asyncio 기반 동시 실행 테스트
- **메모리 사용량**: 대량 데이터 처리 시 메모리 효율성
- **처리 속도**: 블로그 작업 자동화 성능 측정

## 보안 및 윤리
- **API 키 보안**: 환경변수로 민감 정보 관리
- **Rate Limiting**: API 호출 제한 준수
- **User-Agent 관리**: 적절한 User-Agent 설정
- **로봇 차단 회피**: 인간적인 행동 패턴 모방
- **이용약관 준수**: 네이버 블로그 이용약관 준수

## 설정 관리
```python
# 환경변수 예시
GEMINI_API_KEY=your_gemini_key
NAVER_API_CLIENT_ID=your_naver_client_id
NAVER_API_CLIENT_SECRET=your_naver_secret
FIREFOX_PROFILE_PATH=/path/to/firefox/profile
EDGE_PROFILE_PATH=/path/to/edge/profile
```

## 실행 방법
```bash
# 의존성 설치
pip install -r requirements.txt

# 테스트 실행
pytest test/

# 좋아요 기능 실행
python -m src.blog.like_by_search

# 댓글 기능 실행
python -m src.blog.reply_by_recommend
```

## 향후 개발 계획
- **GUI 인터페이스**: Tkinter/PyQt 기반 사용자 인터페이스
- **스케줄링**: APScheduler를 통한 자동 실행
- **데이터베이스**: SQLite/PostgreSQL 연동으로 작업 이력 관리
- **모니터링**: 로그 분석 및 성능 모니터링 대시보드
- **Docker화**: 컨테이너 기반 배포 환경 구성

## 문제 해결 가이드
- **브라우저 호환성**: Chrome, Firefox, Edge 드라이버 설정
- **Element 찾기 실패**: Selenium 대기 전략 및 재시도 로직
- **API 제한**: Rate limiting 및 백오프 전략
- **메모리 누수**: 브라우저 세션 정리 및 리소스 관리

## 기여 방법
1. 이슈 생성으로 버그 리포트 또는 기능 제안
2. 포크 후 기능 브랜치에서 개발
3. 테스트 코드 작성 및 커버리지 유지
4. Pull Request 생성 시 상세한 변경사항 설명
5. 코드 리뷰 피드백 적극 반영

## 라이선스
MIT License - 자유로운 사용 및 수정 가능