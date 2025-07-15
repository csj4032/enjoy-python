#!/usr/bin/env python3
"""
개별 커밋을 보존하면서 머지 커밋만 제거하는 선형화 스크립트
"""

import subprocess
import sys

def run_git_command(cmd):
    """Git 명령 실행"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running: {cmd}")
        print(f"Error: {result.stderr}")
        return None, result.returncode
    return result.stdout.strip(), 0

def linearize_preserving_commits():
    """커밋을 보존하면서 선형화"""
    print("🔄 개별 커밋을 보존하면서 선형화합니다...")
    
    # 백업 브랜치 생성
    print("💾 백업 브랜치 생성...")
    run_git_command("git branch backup-linear-preserve")
    
    # 모든 커밋을 시간순으로 가져오기 (머지 커밋 제외)
    print("📋 모든 non-merge 커밋 수집...")
    output, _ = run_git_command("git log --no-merges --reverse --format='%H|%s|%an|%ae|%ad' --date=iso")
    
    if not output:
        print("❌ 커밋을 찾을 수 없습니다.")
        return False
    
    commits = []
    for line in output.split('\n'):
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 5:
                commits.append({
                    'hash': parts[0],
                    'message': parts[1],
                    'author_name': parts[2],
                    'author_email': parts[3],
                    'date': parts[4]
                })
    
    print(f"📊 수집된 커밋: {len(commits)}개")
    
    # 새로운 orphan 브랜치 생성
    print("🌱 새로운 선형 브랜치 생성...")
    _, ret_code = run_git_command("git checkout --orphan linear-preserved")
    if ret_code != 0:
        print("❌ orphan 브랜치 생성 실패")
        return False
    
    # 첫 번째 커밋부터 차례대로 체리픽
    for i, commit in enumerate(commits):
        print(f"🍒 체리픽 중... ({i+1}/{len(commits)}) {commit['hash'][:8]}: {commit['message'][:50]}...")
        
        # 이전 브랜치로 돌아가서 해당 커밋의 변경사항 가져오기
        run_git_command("git checkout backup-linear-preserve")
        
        # 해당 커밋의 변경사항을 패치로 추출
        output, ret_code = run_git_command(f"git show {commit['hash']} --format='' --name-only")
        if ret_code == 0 and output:
            # 변경된 파일들을 새 브랜치에 적용
            run_git_command("git checkout linear-preserved")
            
            # 해당 커밋의 전체 상태를 가져오기
            run_git_command(f"git checkout backup-linear-preserve -- .")
            run_git_command("git add .")
            
            # 원본 커밋 정보로 커밋 생성
            commit_cmd = f'''git commit --author="{commit['author_name']} <{commit['author_email']}>" --date="{commit['date']}" -m "{commit['message']}"'''
            _, ret_code = run_git_command(commit_cmd)
            
            if ret_code != 0:
                print(f"⚠️ 커밋 {commit['hash'][:8]} 적용 실패, 건너뜀")
                continue
    
    # main 브랜치를 새로운 선형 히스토리로 교체
    print("🔄 main 브랜치 업데이트...")
    run_git_command("git checkout main")
    run_git_command("git reset --hard linear-preserved")
    run_git_command("git branch -D linear-preserved")
    
    print("✅ 선형화 완료!")
    return True

def smart_linearize():
    """더 똑똑한 선형화 방법"""
    print("🧠 스마트 선형화 시작...")
    
    # filter-branch를 사용하여 머지 커밋만 제거
    print("🔧 filter-branch로 머지 커밋 제거...")
    
    # 머지 커밋을 일반 커밋으로 변환하는 스크립트
    filter_script = '''#!/bin/bash
if [ $(git rev-list --count --merges $GIT_COMMIT..$GIT_COMMIT) -eq 1 ]; then
    # 머지 커밋인 경우 첫 번째 부모만 유지
    git rev-parse $GIT_COMMIT^1
else
    # 일반 커밋인 경우 그대로 유지
    cat
fi
'''
    
    # 임시 파일에 스크립트 저장
    with open('/tmp/linearize_filter.sh', 'w') as f:
        f.write(filter_script)
    
    subprocess.run(['chmod', '+x', '/tmp/linearize_filter.sh'])
    
    try:
        # filter-branch 실행
        cmd = 'FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --parent-filter "/tmp/linearize_filter.sh" --tag-name-filter cat -- --all'
        output, ret_code = run_git_command(cmd)
        
        if ret_code == 0:
            print("✅ 머지 커밋 제거 성공!")
            return True
        else:
            print(f"❌ filter-branch 실패: {output}")
            return False
    finally:
        # 임시 파일 정리
        subprocess.run(['rm', '-f', '/tmp/linearize_filter.sh'])

def main():
    """메인 실행"""
    print("🚀 커밋 보존 선형화 시작")
    print("=" * 40)
    
    # 방법 1: filter-branch 시도
    success = smart_linearize()
    
    if not success:
        print("\n🔄 대안 방법 시도...")
        # 방법 2: 수동 체리픽 시도
        success = linearize_preserving_commits()
    
    if success:
        print("\n🎉 선형화 성공!")
        
        # 결과 확인
        print("\n📊 결과 확인:")
        output, _ = run_git_command("git log --oneline --graph -10")
        if output:
            for line in output.split('\n'):
                print(f"  {line}")
        
        output, _ = run_git_command("git rev-list --count HEAD")
        print(f"\n📈 총 커밋 개수: {output}")
        
        output, _ = run_git_command("git log --merges --oneline")
        if not output:
            print("✅ 머지 커밋 없음 - 완전한 선형 히스토리")
        else:
            print(f"⚠️ 여전히 머지 커밋 존재: {len(output.split())}")
    else:
        print("\n❌ 선형화 실패")

if __name__ == "__main__":
    main()