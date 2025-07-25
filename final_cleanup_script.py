#!/usr/bin/env python3
"""
최종 정리 스크립트 - 완전한 선형 히스토리와 영어 메시지로 통일
"""

import subprocess
import sys
import os

def run_git_command(cmd):
    """Git 명령어 실행"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

def force_linear_english_history():
    """강제로 선형 영어 히스토리 생성"""
    
    print("🚀 최종 완전 정리 시작")
    print("=" * 50)
    
    # 백업 생성
    print("💾 최종 백업 생성...")
    run_git_command("git branch final-backup-main")
    
    # 임시 브랜치 생성 및 초기화
    print("🌱 완전히 새로운 브랜치 생성...")
    run_git_command("git checkout --orphan clean-final-branch")
    run_git_command("git rm -rf .")
    
    # 커밋 순서대로 파일 상태 수집 및 영어 메시지로 커밋
    commits_data = [
        ("project init", "feat(project): initialize project structure"),
        ("URL 별 블로그 추출", "feat(blog): add URL-based blog extraction functionality"),
        ("소소한 설정 변경", "chore(config): minor configuration changes"),
        ("소소한 코드 수정", "refactor(core): minor code improvements"),
        ("예외처리 수정", "fix(error): improve exception handling"),
        ("블로그 주소 추가", "feat(config): add blog URL configurations"),
        ("코파일러 리팩토링", "refactor(core): apply copilot refactoring suggestions"),
        ("타입 힌트 추가", "feat(types): add comprehensive type hints"),
        ("함수 파라미터 접미사", "refactor(core): add underscore suffix to function parameters"),
        ("코드 간결화", "refactor(core): simplify code structure"),
        ("포맷팅 개선", "style(core): improve code formatting and log messages"),
        ("클릭 인터셉트 해결", "fix(web): resolve click intercept issues and update type hints"),
        ("예외 처리 개선", "fix(web): handle UnexpectedAlertPresentException in web automation"),
        ("테스트 케이스 추가", "test(core): add detailed descriptions to test cases"),
        ("LLM 통합", "feat(ai): implement LLM integration for comment generation"),
        ("웹 스크래핑 오류 처리", "fix(web): enhance error handling in web scraping"),
        ("버디 기능 개선", "refactor(blog): rename get_neighbor to get_buddies"),
        ("댓글 기능 추가", "feat(blog): add functionality to process replies to buddies"),
        ("버디 검색 개선", "refactor(blog): enhance get_buddies function with customizable selector"),
        ("좋아요 기능 구현", "feat(blog): implement like_post function for liking posts"),
        ("조건 참조 업데이트", "refactor(web): update expected_conditions references"),
        ("블로그 추출 기능", "feat(blog): add blog extraction functionality"),
        ("오류 처리 및 로깅", "refactor(error): improve error handling and logging"),
        ("스크롤 범위 조정", "refactor(web): adjust scrolling range"),
        ("버디 검색 로직", "refactor(blog): update buddy retrieval logic"),
        ("미사용 함수 제거", "refactor(blog): remove unused functions"),
        ("헤드리스 모드 활성화", "config(web): enable headless mode for browser automation"),
        ("세션 예외 처리", "fix(web): add handling for InvalidSessionIdException"),
        ("예외 처리 통합", "refactor(error): consolidate exception handling"),
        ("스크롤 범위 증가", "refactor(web): increase scroll range"),
        ("버디 프로세스 간소화", "refactor(blog): streamline buddy processing"),
        ("수면 시간 조정", "perf(blog): adjust sleep durations for better performance"),
        ("프로젝트 구조 개선", "refactor(project): improve project structure and dependency management"),
        ("타입 힌트 현대화", "feat(types): modernize type hints to Python 3.12 syntax"),
        ("상수 관리 중앙화", "refactor(config): centralize constants management"),
        ("압축 라이브러리 테스트", "test(libs): add comprehensive compression library tests"),
        ("코드 스타일 단순화", "style(core): simplify code style and remove verbose comments"),
        ("로깅으로 교체", "refactor(logging): replace print statements with proper logging"),
        ("누락 라이브러리 추가", "feat(deps): add missing libraries to requirements.txt"),
        ("포스트 데이터 추출", "refactor(data): extract posts data to config.json"),
        ("포스트 로딩 업데이트", "refactor(blog): update post loading with new meta structure"),
        ("gitignore 설정", "fix(config): ensure proper gitignore configuration"),
        ("설정 파일 추가", "feat(config): add configuration files and update function signatures"),
        ("처리 속도 개선", "perf(blog): reduce sleep duration for improved processing speed"),
        ("문서 및 명령어 추가", "feat(config): add git push command and create project documentation")
    ]
    
    # 실제 커밋에서 파일 상태를 가져와서 순차적으로 적용
    print("📋 원본 커밋 히스토리에서 파일 상태 수집...")
    cmd = "git log final-backup-main --no-merges --reverse --format='%H|%s' --all"
    output, _ = run_git_command(cmd)
    
    if not output:
        print("❌ 커밋을 가져올 수 없습니다.")
        return False
    
    actual_commits = []
    for line in output.split('\n'):
        if '|' in line and line.strip():
            hash_part, message = line.split('|', 1)
            actual_commits.append((hash_part.strip(), message.strip()))
    
    print(f"📊 실제 커밋: {len(actual_commits)}개")
    
    # 각 커밋을 영어 메시지로 재생성
    for i, (commit_hash, original_message) in enumerate(actual_commits):
        if i >= 50:  # 너무 많은 커밋 처리 방지
            break
            
        print(f"🔄 처리 중... ({i+1}/{min(len(actual_commits), 50)}) {commit_hash[:8]}")
        
        # 해당 커밋의 파일 상태 가져오기
        run_git_command("git checkout final-backup-main")
        run_git_command(f"git checkout {commit_hash} -- . 2>/dev/null || true")
        run_git_command("git checkout clean-final-branch")
        
        # 파일 추가
        run_git_command("git add -A")
        
        # 변경사항 확인
        status_output, _ = run_git_command("git status --porcelain")
        if not status_output and i > 0:
            print(f"  ⏭️ 변경사항 없음, 건너뜀")
            continue
        
        # 영어 메시지 생성
        english_message = get_english_message(original_message, i)
        
        # 커밋 생성
        _, ret_code = run_git_command(f'git commit -m "{english_message}"')
        
        if ret_code == 0:
            print(f"  ✅ {english_message[:50]}...")
        else:
            print(f"  ⚠️ 커밋 실패: {english_message[:30]}...")
    
    # main 브랜치 교체
    print("🔄 main 브랜치를 새로운 히스토리로 교체...")
    run_git_command("git checkout main")
    run_git_command("git reset --hard clean-final-branch")
    run_git_command("git branch -D clean-final-branch")
    
    return True

def get_english_message(original_message, index):
    """원본 메시지를 영어로 변환"""
    
    # 직접 매핑
    direct_mappings = {
        'project init': 'feat(project): initialize project structure',
        'feat : URL 별 블로그 추출': 'feat(blog): add URL-based blog extraction functionality',
        'chore : 소소한 설정 변경': 'chore(config): minor configuration changes',
        'chore : 소소한 코드 수정': 'refactor(core): minor code improvements',
        'chore : 예외처리 수정': 'fix(error): improve exception handling',
        'chore : 블로그 주소 추가': 'feat(config): add blog URL configurations',
        'chore : 코파일러 리팩토링 지시': 'refactor(core): apply copilot refactoring suggestions',
        'refactor: 함수 파라미터 _접미사 추가': 'refactor(core): add underscore suffix to function parameters',
        'chore : 소소한 설정 코드 변경': 'config(setup): update configuration settings'
    }
    
    # 직접 매핑 확인
    if original_message in direct_mappings:
        return direct_mappings[original_message]
    
    # 부분 매핑
    for korean_part, english_msg in direct_mappings.items():
        if korean_part in original_message:
            return english_msg
    
    # 이미 영어 표준 포맷이면 그대로 반환
    if original_message.startswith(('feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'perf')):
        return original_message
    
    # 키워드 기반 분류
    message_lower = original_message.lower()
    
    if any(word in original_message for word in ['함수', '파라미터', '타입', '리팩토링']):
        return f'refactor(core): improve code structure and type hints (#{index+1})'
    elif any(word in original_message for word in ['예외', '처리', '오류']):
        return f'fix(error): improve exception handling (#{index+1})'
    elif any(word in original_message for word in ['설정', '구성']):
        return f'config(setup): update configuration settings (#{index+1})'
    elif any(word in original_message for word in ['추가', '기능']):
        return f'feat(core): add new functionality (#{index+1})'
    elif any(word in original_message for word in ['수정', '변경']):
        return f'refactor(core): update and improve code (#{index+1})'
    elif any(word in original_message for word in ['테스트']):
        return f'test(core): add or update tests (#{index+1})'
    elif any(word in message_lower for word in ['add', 'implement']):
        return f'feat(core): {original_message[:50]} (#{index+1})'
    elif any(word in message_lower for word in ['fix', 'handle']):
        return f'fix(core): {original_message[:50]} (#{index+1})'
    elif any(word in message_lower for word in ['refactor', 'improve', 'update']):
        return f'refactor(core): {original_message[:50]} (#{index+1})'
    elif any(word in message_lower for word in ['test']):
        return f'test(core): {original_message[:50]} (#{index+1})'
    else:
        return f'refactor(core): code improvements (#{index+1})'

def final_verification():
    """최종 검증"""
    print("\n📊 최종 검증")
    print("=" * 40)
    
    # 총 커밋 수
    output, _ = run_git_command("git rev-list --count HEAD")
    print(f"📈 총 커밋 개수: {output}")
    
    # 머지 커밋 확인
    output, _ = run_git_command("git log --merges --oneline")
    if not output:
        print("✅ 머지 커밋 없음 - 완전한 선형 히스토리")
    else:
        print(f"❌ 머지 커밋 {len(output.split())}개 존재")
    
    # 한국어 커밋 확인
    output, _ = run_git_command("git log --pretty=format:'%s'")
    korean_count = 0
    if output:
        for message in output.split('\n'):
            if any('\uac00' <= char <= '\ud7af' for char in message):
                korean_count += 1
    
    if korean_count == 0:
        print("✅ 한국어 커밋 메시지 없음")
    else:
        print(f"❌ 한국어 커밋 메시지 {korean_count}개 존재")
    
    # 최근 커밋 표시
    print("\n📝 최근 10개 커밋:")
    output, _ = run_git_command("git log --oneline -10")
    if output:
        for line in output.split('\n'):
            print(f"  {line}")

def main():
    """메인 실행"""
    success = force_linear_english_history()
    
    if success:
        final_verification()
        print("\n🎉 최종 완전 정리 완료!")
        print("- 완전한 선형 히스토리")
        print("- 모든 커밋 메시지 영어로 통일")
        print("- 머지 커밋 완전 제거")
    else:
        print("\n❌ 정리 실패")

if __name__ == "__main__":
    main()