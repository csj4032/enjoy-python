# Enjoy Python Project

## 프로젝트 개요
Enjoy Python 프로젝트는 Selenium을 활용하여 네이버 블로그와 관련된 다양한 작업을 자동화하는 Python 기반 애플리케이션입니다. 이 프로젝트는 블로그 검색, 좋아요 추가, 댓글 작성 등 여러 기능을 제공합니다.

## 디렉토리 구조

```
README.md
requirements.txt
requirements-test.txt
pyproject.toml
pytest.ini
netebook/
    blog/
        buddy.ipynb
        like.ipynb
        views.ipynb
src/
    __init__.py
    async_gather.py
    compression.py
    blog/
        __init__.py
        add_buddy_search.py
        extract_blog_by_buddy.py
        extract_blog_by_url.py
        like_by_buddy_added.py
        like_by_recommend.py
        like_by_search.py
        reply_by_buddy.py
        reply_by_buddy_added.py
        reply_by_recommend.py
        reply_by_url.py
        search_for_mobile.py
        search_for_pc.py
    common/
        __init__.py
        llm.py
        search.py
        webs.py
    config/
        __init__.py
        configuration.py
        variables.py
        envs/
test/
    __init__.py
    test_async_gather.py
    test_configuration.py
    test_kafka_consumer.py
    test_ollama.py
    test_pandas_join.py
    test_search.py
    test_thread_coroutine.py
    test_webs.py
    test_x.py
    test_yield.py
thumbnails/
    designPattern_template_method_pattern.png
```

### 주요 디렉토리 및 파일 설명

- **`netebook/`**: Jupyter Notebook 파일을 포함하며, 데이터 분석 및 프로토타이핑에 사용됩니다.
- **`src/`**: 주요 애플리케이션 코드가 포함된 디렉토리입니다.
  - `blog/`: 블로그 관련 작업(좋아요, 댓글, 검색 등)을 처리하는 모듈.
  - `common/`: 공통 유틸리티 함수 및 클래스.
  - `config/`: 설정 관련 모듈.
- **`test/`**: 테스트 코드가 포함된 디렉토리로, 프로젝트의 안정성을 보장합니다.
- **`thumbnails/`**: 프로젝트와 관련된 이미지 파일.

## 주요 기능

1. **블로그 검색**
   - `search_for_mobile.py`, `search_for_pc.py`를 통해 네이버 블로그 게시물을 검색합니다.

2. **좋아요 추가**
   - `like_by_search.py`, `like_by_buddy_added.py`, `like_by_recommend.py` 등을 사용하여 블로그 게시물에 "좋아요"를 추가합니다.

3. **댓글 작성**
   - `reply_by_buddy.py`, `reply_by_buddy_added.py`, `reply_by_recommend.py`, `reply_by_url.py` 등을 통해 블로그 게시물에 댓글을 작성합니다.

4. **블로그 데이터 추출**
   - `extract_blog_by_buddy.py`, `extract_blog_by_url.py`를 사용하여 블로그 데이터를 수집합니다.

## 의존성

- Python 3.10 이상
- Selenium
- 기타 의존성은 `requirements.txt`에 명시되어 있습니다.

## 설치 및 실행 방법

1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **프로젝트 실행**
   ```bash
   python blog/like_by_search.py
   ```

## 테스트

테스트 코드는 `test/` 디렉토리에 위치하며, `pytest`를 사용하여 실행할 수 있습니다.

```bash
pytest test/
```

## 기여 방법

1. 이슈를 생성하여 버그를 보고하거나 새로운 기능을 제안합니다.
2. 포크를 생성하고 변경 사항을 커밋한 후 Pull Request를 생성합니다.

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.
