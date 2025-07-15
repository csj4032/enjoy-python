#!/usr/bin/env python3
"""
강력한 선형화 - 모든 머지 커밋을 완전히 제거
"""

import subprocess
import tempfile
import os

def run_git_command(cmd):
    """Git 명령 실행"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running: {cmd}")
        print(f"Error: {result.stderr}")
        return None, result.returncode
    return result.stdout.strip(), 0

def force_linearize():
    """강제 선형화"""
    print("💪 강제 선형화 시작...")
    
    # 백업 생성
    print("💾 최종 백업 생성...")
    run_git_command("git branch backup-final-before-linearize")
    
    # 모든 non-merge 커밋을 시간순으로 추출
    print("📋 non-merge 커밋 추출...")
    output, _ = run_git_command("git rev-list --no-merges --reverse HEAD")
    
    if not output:
        print("❌ 커밋을 찾을 수 없습니다.")
        return False
    
    commit_hashes = output.strip().split('\n')
    print(f"📊 추출된 커밋: {len(commit_hashes)}개")
    
    # 새로운 orphan 브랜치 생성
    print("🌱 새 브랜치 생성...")
    run_git_command("git checkout --orphan temp-linear")
    run_git_command("git rm -rf .")
    
    # 첫 번째 커밋부터 하나씩 체리픽
    for i, commit_hash in enumerate(commit_hashes):
        print(f"🍒 체리픽 ({i+1}/{len(commit_hashes)}): {commit_hash[:8]}...")
        
        # 커밋 정보 가져오기
        message_output, _ = run_git_command(f"git log -1 --format='%s' {commit_hash}")
        author_output, _ = run_git_command(f"git log -1 --format='%an <%ae>' {commit_hash}")
        date_output, _ = run_git_command(f"git log -1 --format='%ad' --date=iso {commit_hash}")
        
        if i == 0:
            # 첫 번째 커밋: 전체 상태를 복사
            run_git_command(f"git checkout {commit_hash} -- .")
            run_git_command("git add .")
            
            commit_cmd = f'git commit --author="{author_output}" --date="{date_output}" -m "{message_output}"'
            _, ret_code = run_git_command(commit_cmd)
            
            if ret_code != 0:
                print(f"❌ 첫 번째 커밋 {commit_hash[:8]} 생성 실패")
                return False
        else:
            # 나머지 커밋: 체리픽 시도
            _, ret_code = run_git_command(f"git cherry-pick {commit_hash}")
            
            if ret_code != 0:
                # 체리픽 실패 시 수동으로 적용
                print(f"⚠️ 체리픽 실패, 수동 적용: {commit_hash[:8]}")
                
                # 체리픽 중단
                run_git_command("git cherry-pick --abort")
                
                # 해당 커밋의 상태를 직접 적용
                run_git_command(f"git checkout {commit_hash} -- .")
                run_git_command("git add .")
                
                commit_cmd = f'git commit --author="{author_output}" --date="{date_output}" -m "{message_output}"'
                _, ret_code = run_git_command(commit_cmd)
                
                if ret_code != 0:
                    print(f"❌ 수동 커밋 {commit_hash[:8]} 실패")
                    continue
    
    # main 브랜치를 새로운 선형 히스토리로 교체
    print("🔄 main 브랜치 교체...")
    run_git_command("git checkout main")
    run_git_command("git reset --hard temp-linear")
    run_git_command("git branch -D temp-linear")
    
    print("✅ 강제 선형화 완료!")
    return True

def main():
    """메인 실행"""
    print("🚀 강제 선형화 시작")
    print("=" * 30)
    
    success = force_linearize()
    
    if success:
        print("\n🎉 선형화 성공!")
        
        # 최종 검증
        print("\n📊 최종 결과:")
        
        # 머지 커밋 확인
        output, _ = run_git_command("git log --merges --oneline")
        if not output:
            print("✅ 머지 커밋 없음 - 완전한 선형 히스토리")
        else:
            merge_count = len([line for line in output.split('\n') if line.strip()])
            print(f"⚠️ 여전히 머지 커밋 {merge_count}개 존재")
        
        # 커밋 개수
        output, _ = run_git_command("git rev-list --count HEAD")
        print(f"📈 총 커밋 개수: {output}")
        
        # 그래프 구조
        print("\n🌳 최종 브랜치 구조:")
        output, _ = run_git_command("git log --oneline --graph -15")
        if output:
            for line in output.split('\n'):
                print(f"  {line}")
        
        print(f"\n💾 백업: backup-final-before-linearize 브랜치에서 이전 상태 확인 가능")
        
    else:
        print("\n❌ 선형화 실패")

if __name__ == "__main__":
    main()