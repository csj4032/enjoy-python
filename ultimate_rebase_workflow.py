#!/usr/bin/env python3
"""
최종 완벽한 리베이스 워크플로우 구현
모든 머지 커밋 제거, 모든 한국어 메시지 영어로 표준화, 완전한 선형 히스토리
"""

import subprocess
import sys
import os

def run_git_command(cmd):
    """Git 명령 실행"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

def get_all_commits():
    """모든 non-merge 커밋 정보 수집"""
    cmd = "git log --no-merges --reverse --format='%H|%an|%ae|%ad|%s' --date=iso"
    output, ret_code = run_git_command(cmd)
    
    if ret_code != 0:
        return []
    
    commits = []
    for line in output.split('\n'):
        if '|' in line and line.strip():
            parts = line.split('|', 4)
            if len(parts) >= 5:
                commits.append({
                    'hash': parts[0],
                    'author_name': parts[1],
                    'author_email': parts[2], 
                    'date': parts[3],
                    'message': parts[4]
                })
    
    return commits

def standardize_korean_message(message):
    """한국어 커밋 메시지를 영어 표준 포맷으로 변환"""
    
    # 직접 매핑
    direct_mappings = {
        'feat : URL 별 블로그 추출': 'feat(blog): add URL-based blog extraction functionality',
        'chore : 소소한 설정 변경': 'chore(config): minor configuration changes',
        'chore : 예외처리 수정': 'fix(error): improve exception handling',
        'chore : 블로그 주소 추가': 'feat(config): add blog URL configurations',
        'refactor: 함수 파라미터 _접미사 추가': 'refactor(core): add underscore suffix to function parameters',
        '함수 파라미터 _접미사 추가': 'refactor(core): add underscore suffix to function parameters',
        'refactor(core): 작업 내용에 대한 설명': 'docs(project): add work description documentation',
        'fix(core): 코드 정리: 포맷팅 개선 및 로그 메시지 수정': 'style(core): improve code formatting and log messages',
        'refactor(core): 함수 분리, 파라미터 네이밍 개선, 타입 명시, 코드 간결화 및 전역변수 혼동 방지 등 리팩토링': 'refactor(core): improve functions with better naming and type hints',
        'refactor(core): 코드 개선: 클릭 인터셉트 문제 해결, 함수 타입 힌트 최신화, 파라미터 명명 규칙 적용': 'fix(web): resolve click intercept issues and update type hints',
        'feat(core): 코드 개선: UnexpectedAlertPresentException 예외 처리 추가 및 타입 힌트 업데이트': 'fix(web): handle UnexpectedAlertPresentException in web automation'
    }
    
    # 직접 매핑 확인
    if message in direct_mappings:
        return direct_mappings[message]
    
    # 부분 매핑 확인
    for korean_part, english_message in direct_mappings.items():
        if korean_part in message:
            return english_message
    
    # 이미 영어 표준 포맷인지 확인
    if message.startswith(('feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'perf', 'build', 'ci', 'revert')):
        return message
    
    # 패턴 기반 변환
    import re
    
    # 한국어 문자 포함 확인
    has_korean = any('\uac00' <= char <= '\ud7af' for char in message)
    
    if has_korean:
        # 키워드 기반 분류
        message_lower = message.lower()
        
        if any(word in message for word in ['함수', '파라미터', '타입', '리팩토링', '개선', '분리']):
            return f'refactor(core): improve code structure and type hints'
        elif any(word in message for word in ['예외', '처리', '오류', '에러']):
            return f'fix(error): improve exception handling'
        elif any(word in message for word in ['설정', '구성', '환경']):
            return f'config(setup): update configuration settings'
        elif any(word in message for word in ['추가', '기능', '구현']):
            return f'feat(core): add new functionality'
        elif any(word in message for word in ['수정', '변경', '업데이트']):
            return f'refactor(core): update and improve code'
        elif any(word in message for word in ['포맷', '스타일', '정리']):
            return f'style(core): improve code formatting'
        elif any(word in message for word in ['테스트', '검증']):
            return f'test(core): add or update tests'
        elif any(word in message for word in ['문서', '설명', '주석']):
            return f'docs(project): update documentation'
        else:
            return f'refactor(core): code improvements'
    
    # 영어지만 표준 포맷이 아닌 경우
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['fix', 'bug', 'error', 'issue']):
        return f'fix(core): {message[:60]}'
    elif any(word in message_lower for word in ['add', 'implement', 'create']):
        return f'feat(core): {message[:60]}'
    elif any(word in message_lower for word in ['refactor', 'improve', 'update', 'enhance']):
        return f'refactor(core): {message[:60]}'
    elif any(word in message_lower for word in ['test', 'spec']):
        return f'test(core): {message[:60]}'
    elif any(word in message_lower for word in ['doc', 'readme', 'comment']):
        return f'docs(project): {message[:60]}'
    elif any(word in message_lower for word in ['style', 'format', 'lint']):
        return f'style(core): {message[:60]}'
    elif any(word in message_lower for word in ['config', 'setting', 'env']):
        return f'config(setup): {message[:60]}'
    else:
        return f'refactor(core): {message[:60]}'

def create_ultimate_linear_history():
    """최종 완벽한 선형 히스토리 생성"""
    print("🚀 최종 완벽한 리베이스 워크플로우 시작")
    print("=" * 60)
    
    # 백업 생성
    print("💾 최종 백업 브랜치 생성...")
    run_git_command("git branch ultimate-backup-main")
    
    # 모든 커밋 수집
    print("📋 모든 non-merge 커밋 수집...")
    commits = get_all_commits()
    
    if not commits:
        print("❌ 커밋을 찾을 수 없습니다.")
        return False
    
    print(f"📊 수집된 커밋: {len(commits)}개")
    
    # 임시 브랜치에서 작업
    print("🌱 새로운 임시 브랜치 생성...")
    run_git_command("git checkout -b temp-ultimate-linear")
    
    # 첫 번째 커밋부터 순차적으로 처리
    processed_commits = []
    
    for i, commit in enumerate(commits):
        print(f"🔄 처리 중... ({i+1}/{len(commits)}) {commit['hash'][:8]}")
        
        # 원본 브랜치로 돌아가서 해당 커밋 체크아웃
        run_git_command("git checkout ultimate-backup-main")
        
        # 해당 커밋의 파일 상태 가져오기
        run_git_command(f"git checkout {commit['hash']} -- .")
        
        # 임시 브랜치로 돌아가기
        run_git_command("git checkout temp-ultimate-linear")
        
        # 파일 추가
        run_git_command("git add -A")
        
        # 변경사항 확인
        status_output, _ = run_git_command("git status --porcelain")
        
        if not status_output and i > 0:  # 첫 번째 커밋이 아니고 변경사항이 없으면 건너뛰기
            print(f"  ⏭️ 변경사항 없음, 건너뜀")
            continue
        
        # 메시지 표준화
        standardized_message = standardize_korean_message(commit['message'])
        
        # 커밋 생성
        commit_cmd = f'''git commit --author="{commit['author_name']} <{commit['author_email']}>" --date="{commit['date']}" -m "{standardized_message}"'''
        _, ret_code = run_git_command(commit_cmd)
        
        if ret_code == 0:
            processed_commits.append({
                'original': commit,
                'standardized_message': standardized_message
            })
            print(f"  ✅ {standardized_message[:50]}...")
        else:
            print(f"  ⚠️ 커밋 생성 실패")
    
    # main 브랜치를 새로운 히스토리로 교체
    print("🔄 main 브랜치를 새로운 선형 히스토리로 교체...")
    run_git_command("git checkout main")
    run_git_command("git reset --hard temp-ultimate-linear")
    run_git_command("git branch -D temp-ultimate-linear")
    
    print(f"✅ {len(processed_commits)}개 커밋 처리 완료!")
    return True

def setup_perfect_rebase_workflow():
    """완벽한 리베이스 워크플로우 설정"""
    print("⚙️ 완벽한 리베이스 워크플로우 설정...")
    
    configs = [
        "git config pull.rebase true",
        "git config rebase.autoStash true",
        "git config rebase.autoSquash true", 
        "git config rebase.updateRefs true",
        "git config merge.ff only",
        "git config branch.autosetupmerge always",
        "git config branch.autosetuprebase always",
        "git config rebase.abbreviateCommands true",
        "git config core.editor 'echo'"  # 자동으로 리베이스 편집 건너뛰기
    ]
    
    for config in configs:
        run_git_command(config)
    
    print("✅ 리베이스 워크플로우 설정 완료")

def final_verification():
    """최종 검증"""
    print("\n📊 최종 검증 결과")
    print("=" * 50)
    
    # 총 커밋 수
    output, _ = run_git_command("git rev-list --count HEAD")
    print(f"📈 총 커밋 개수: {output}")
    
    # 머지 커밋 확인
    output, _ = run_git_command("git log --merges --oneline")
    if not output:
        print("✅ 머지 커밋 없음 - 완전한 선형 히스토리")
    else:
        merge_count = len([line for line in output.split('\n') if line.strip()])
        print(f"❌ 여전히 머지 커밋 존재: {merge_count}개")
    
    # 한국어 커밋 확인
    output, _ = run_git_command("git log --pretty=format:'%s'")
    if output:
        korean_commits = []
        for message in output.split('\n'):
            if any('\uac00' <= char <= '\ud7af' for char in message):
                korean_commits.append(message)
        
        if korean_commits:
            print(f"❌ 한국어 커밋 메시지 {len(korean_commits)}개 발견")
            for msg in korean_commits[:3]:
                print(f"  - {msg}")
        else:
            print("✅ 한국어 커밋 메시지 없음")
    
    # 최근 커밋 표시
    print("\n📝 최근 10개 커밋:")
    output, _ = run_git_command("git log --oneline -10")
    if output:
        for line in output.split('\n'):
            print(f"  {line}")
    
    # 리베이스 설정 확인
    print("\n⚙️ 리베이스 설정:")
    configs = ['pull.rebase', 'rebase.autoStash', 'merge.ff']
    for config in configs:
        value, _ = run_git_command(f"git config {config}")
        print(f"  {config}: {value if value else 'not set'}")

def main():
    """메인 실행"""
    success = create_ultimate_linear_history()
    
    if success:
        setup_perfect_rebase_workflow()
        final_verification()
        print("\n🎉 최종 완벽한 리베이스 워크플로우 구현 성공!")
    else:
        print("\n❌ 리베이스 워크플로우 구현 실패")

if __name__ == "__main__":
    main()