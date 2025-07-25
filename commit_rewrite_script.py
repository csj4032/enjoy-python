#!/usr/bin/env python3
"""
Git 커밋 메시지 표준화 스크립트
기존 커밋 메시지를 분석하여 표준 포맷으로 변환
"""

import re
import subprocess
import sys

def analyze_commit_message(message):
    """커밋 메시지를 분석하여 적절한 타입과 스코프, 제목을 반환"""
    
    # 한국어 메시지 매핑
    korean_patterns = {
        r'프로젝트?\s*초기화?|project\s*init': ('feat', 'project', 'initialize project structure'),
        r'URL\s*별\s*블로그\s*추출': ('feat', 'blog', 'add URL-based blog extraction functionality'),
        r'설정\s*변경|설정\s*코드\s*변경': ('config', 'config', 'update configuration settings'),
        r'소소한\s*코드\s*수정': ('refactor', 'core', 'minor code improvements'),
        r'블로그\s*주소\s*추가': ('feat', 'config', 'add blog URL configurations'),
        r'예외처리\s*수정': ('fix', 'core', 'improve exception handling'),
        r'코파일러\s*리팩토링': ('refactor', 'core', 'apply copilot refactoring suggestions'),
        r'작업\s*내용.*설명': ('docs', 'project', 'add work description documentation'),
        r'함수\s*파라미터.*접미사': ('refactor', 'core', 'add underscore suffix to function parameters'),
        r'포맷팅\s*개선.*로그\s*메시지': ('style', 'core', 'improve code formatting and log messages'),
        r'수정\s*내용\s*반영': ('refactor', 'core', 'apply code modifications'),
        r'함수\s*분리.*리팩토링': ('refactor', 'core', 'refactor functions with improved naming and type hints'),
        r'클릭\s*인터셉트.*해결': ('fix', 'web', 'resolve click intercept issues and update type hints'),
        r'UnexpectedAlertPresentException.*처리': ('fix', 'web', 'handle UnexpectedAlertPresentException in web automation'),
    }
    
    # 영어 패턴 매핑
    english_patterns = {
        r'project\s*init': ('feat', 'project', 'initialize project structure'),
        r'add.*type\s*hint': ('feat', 'types', 'add comprehensive type hints'),
        r'refactor.*type\s*hint': ('refactor', 'types', 'update type hints'),
        r'simplify.*code': ('refactor', 'core', 'simplify code structure'),
        r'remove.*verbose.*comment': ('style', 'core', 'remove verbose comments and improve code style'),
        r'replace\s*print.*logging': ('refactor', 'logging', 'replace print statements with proper logging'),
        r'add.*missing.*libraries': ('feat', 'deps', 'add missing library dependencies'),
        r'extract.*posts.*data': ('refactor', 'data', 'extract posts data to configuration'),
        r'update.*post.*loading': ('refactor', 'blog', 'update post loading with new meta structure'),
        r'ensure.*ignored': ('fix', 'config', 'ensure proper gitignore configuration'),
        r'reduce.*sleep.*duration': ('perf', 'blog', 'reduce sleep duration for improved processing speed'),
        r'add.*git.*push': ('feat', 'config', 'add git push command and project documentation'),
        r'comprehensive.*compression': ('feat', 'test', 'add comprehensive compression library tests'),
        r'modernize.*type.*hints': ('feat', 'types', 'modernize type hints to Python 3.12 syntax'),
        r'centralize.*constants': ('refactor', 'config', 'centralize constants management'),
        r'improve.*project.*structure': ('refactor', 'project', 'improve project structure and dependency management'),
        r'InvalidSessionIdException': ('fix', 'web', 'handle InvalidSessionIdException in web automation'),
        r'enable.*headless.*mode': ('config', 'web', 'enable headless mode for browser automation'),
        r'consolidate.*exception': ('refactor', 'error', 'consolidate exception handling'),
        r'increase.*scroll.*range': ('refactor', 'web', 'increase scroll range in web automation'),
        r'streamline.*buddy': ('refactor', 'blog', 'streamline buddy processing logic'),
        r'adjust.*sleep.*durations': ('refactor', 'perf', 'adjust sleep durations and expand scroll range'),
        r'blog.*extraction': ('feat', 'blog', 'add blog extraction functionality'),
        r'llm.*integration': ('feat', 'ai', 'implement LLM integration for comment generation'),
        r'enhance.*error.*handling': ('refactor', 'error', 'enhance error handling in web scraping'),
        r'rename.*get_neighbor': ('refactor', 'blog', 'rename get_neighbor to get_buddies'),
        r'replies.*buddies': ('feat', 'blog', 'add functionality to process replies to buddies'),
        r'enhance.*get_buddies': ('refactor', 'blog', 'enhance get_buddies function with customizable selector'),
        r'streamline.*buddy.*retrieval': ('refactor', 'blog', 'streamline buddy retrieval logic'),
        r'implement.*like_post': ('feat', 'blog', 'implement like_post function for liking posts'),
        r'expected_conditions.*alias': ('refactor', 'web', 'update expected_conditions references to use alias'),
        r'test.*cases': ('test', 'core', 'add and update test cases'),
        r'remove.*git.*cache': ('chore', 'git', 'remove git cache and re-add files'),
        r'unit.*tests.*google': ('test', 'api', 'add unit tests for Google Trends and Naver search'),
        r'merge.*branch': ('merge', 'git', 'merge branch changes'),
        r'handle.*alert': ('fix', 'web', 'handle unexpected alert exceptions'),
        r'detailed.*descriptions.*test': ('test', 'docs', 'add detailed descriptions to test cases'),
    }
    
    message_lower = message.lower()
    
    # 한국어 패턴 체크
    for pattern, (commit_type, scope, subject) in korean_patterns.items():
        if re.search(pattern, message, re.IGNORECASE):
            return commit_type, scope, subject
    
    # 영어 패턴 체크
    for pattern, (commit_type, scope, subject) in english_patterns.items():
        if re.search(pattern, message_lower):
            return commit_type, scope, subject
    
    # 기본 타입 추론
    if any(word in message_lower for word in ['fix', '수정', 'bug', '버그', 'error', '오류']):
        return 'fix', 'core', f'fix issues in {message[:50]}'
    elif any(word in message_lower for word in ['feat', '기능', 'add', '추가', 'implement']):
        return 'feat', 'core', f'add new functionality - {message[:50]}'
    elif any(word in message_lower for word in ['refactor', '리팩토링', 'improve', '개선']):
        return 'refactor', 'core', f'refactor code - {message[:50]}'
    elif any(word in message_lower for word in ['test', '테스트']):
        return 'test', 'core', f'add/update tests - {message[:50]}'
    elif any(word in message_lower for word in ['docs', '문서', 'doc']):
        return 'docs', 'core', f'update documentation - {message[:50]}'
    elif any(word in message_lower for word in ['chore', '설정', 'config']):
        return 'chore', 'config', f'update configuration - {message[:50]}'
    else:
        return 'refactor', 'core', f'code improvements - {message[:50]}'

def format_commit_message(commit_type, scope, subject):
    """표준 커밋 메시지 포맷으로 변환"""
    return f"{commit_type}({scope}): {subject}"

def main():
    """메인 실행 함수"""
    # 모든 커밋 해시와 메시지 가져오기
    result = subprocess.run(
        ['git', 'log', '--pretty=format:%H|%s', '--reverse'],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print("Git 로그를 가져올 수 없습니다.")
        sys.exit(1)
    
    commits = []
    for line in result.stdout.strip().split('\n'):
        if '|' in line:
            hash_part, message = line.split('|', 1)
            commit_type, scope, subject = analyze_commit_message(message)
            new_message = format_commit_message(commit_type, scope, subject)
            commits.append((hash_part, message, new_message))
    
    # 결과 출력
    print("커밋 메시지 변환 결과:")
    print("=" * 80)
    for hash_part, old_msg, new_msg in commits:
        print(f"Hash: {hash_part[:8]}")
        print(f"Old:  {old_msg}")
        print(f"New:  {new_msg}")
        print("-" * 80)

if __name__ == "__main__":
    main()