#!/bin/bash

# Git 히스토리 전체 다시 쓰기 스크립트
# 매우 위험한 작업이므로 백업 먼저 생성

echo "Git 히스토리 전체 다시 쓰기를 시작합니다..."
echo "현재 브랜치를 백업합니다..."

# 백업 브랜치 생성
git branch backup-before-rewrite

# filter-branch를 사용하여 커밋 메시지 다시 쓰기
git filter-branch --msg-filter '
    case "$GIT_COMMIT" in
        afaf542*) echo "feat(project): initialize project structure" ;;
        ed9ecf3*) echo "feat(blog): add URL-based blog extraction functionality" ;;
        1b667d8*) echo "chore(config): update configuration settings" ;;
        78ac37e*) echo "refactor(core): minor code improvements" ;;
        09e0b94*) echo "refactor(core): minor code improvements" ;;
        bc7c611*) echo "refactor(core): minor code improvements" ;;
        c264cdb*) echo "refactor(core): minor code improvements" ;;
        684dcc2*) echo "chore(config): update configuration settings" ;;
        4a42bf1*) echo "feat(config): add blog URL configurations" ;;
        91fdb95*) echo "feat(config): add blog URL configurations" ;;
        ff50afa*) echo "fix(core): improve exception handling" ;;
        c0c4bb7*) echo "refactor(core): apply copilot refactoring suggestions" ;;
        dd39f61*) echo "feat(types): add parameter and return type hints to search methods" ;;
        36a6aff*) echo "feat(types): add type hints to thumbnail generation function" ;;
        b95733e*) echo "feat(types): add type hints to buddy like methods" ;;
        014cbfd*) echo "docs(project): add work description documentation" ;;
        3da8787*) echo "refactor(core): add underscore suffix to function parameters" ;;
        388256a*) echo "refactor(core): simplify code by removing unnecessary variables" ;;
        9aee84a*) echo "style(core): improve code formatting and log messages" ;;
        a6bf7f0*) echo "refactor(core): apply code modifications" ;;
        c3cb185*) echo "refactor(core): improve functions with better naming and type hints" ;;
        184454f*) echo "fix(web): resolve click intercept issues and update type hints" ;;
        80cb867*) echo "refactor(core): minor code improvements" ;;
        45006e5*) echo "fix(web): handle UnexpectedAlertPresentException in web automation" ;;
        d5dd2c8*) echo "merge: merge branch main from origin" ;;
        1284902*) echo "fix(web): handle UnexpectedAlertPresentException in search" ;;
        1061325*) echo "test(docs): add detailed descriptions to test cases" ;;
        726f1b5*) echo "test(project): update test cases and project structure" ;;
        766ea87*) echo "chore(git): remove git cache and re-add files" ;;
        496f36b*) echo "test(api): add unit tests for Google Trends and Naver search" ;;
        520ceb5*) echo "feat(ai): implement LLM integration for comment generation" ;;
        6941f7f*) echo "fix(web): enhance error handling in web scraping and adjust scrolling" ;;
        2ed3662*) echo "refactor(blog): rename get_neighbor to get_buddies" ;;
        f6e3d4e*) echo "feat(blog): add functionality to process replies to buddies" ;;
        ecf828b*) echo "refactor(blog): enhance get_buddies function with customizable selector" ;;
        081df4d*) echo "refactor(blog): streamline buddy retrieval with type hints" ;;
        893b86d*) echo "merge: merge branch main from origin" ;;
        75364ed*) echo "feat(blog): implement like_post function for liking posts" ;;
        ec22ebb*) echo "refactor(web): update expected_conditions references to use alias ec" ;;
        583680d*) echo "feat(blog): add blog extraction functionality and update scripts" ;;
        72a24d7*) echo "refactor(error): improve error handling and logging in buddy addition" ;;
        eb1050a*) echo "refactor(blog): adjust scrolling range and clean up buddy search" ;;
        933078d*) echo "refactor(blog): update buddy retrieval logic and enhance scrolling" ;;
        ee6a078*) echo "refactor(blog): remove unused functions and streamline buddy processing" ;;
        910da3d*) echo "refactor(blog): remove unused parse_buddy_by_added function" ;;
        1eb7a8f*) echo "config(web): enable headless mode for all browser options" ;;
        dbcf7be*) echo "fix(web): add handling for InvalidSessionIdException in get_posts" ;;
        cf59c00*) echo "refactor(error): consolidate exception handling in post liking" ;;
        3bc6d72*) echo "refactor(web): increase scroll range and update blog link" ;;
        7e874cb*) echo "refactor(blog): streamline add_buddy_process and enhance error handling" ;;
        adbbda2*) echo "perf(blog): adjust sleep durations and expand scroll range" ;;
        91f1f04*) echo "fix(web): add handling for InvalidSessionIdException in buddy search" ;;
        c21efcc*) echo "refactor(project): improve project structure and dependency management" ;;
        8ac7571*) echo "feat(types): add comprehensive type hints to improve code quality" ;;
        2160901*) echo "feat(types): modernize type hints to Python 3.12 syntax" ;;
        4c487ef*) echo "refactor(config): centralize constants management for better maintainability" ;;
        45480e2*) echo "feat(test): add comprehensive compression library tests" ;;
        44c9dad*) echo "refactor(test): simplify compression tests to focus on performance" ;;
        969ff69*) echo "style(core): simplify code style and remove verbose comments" ;;
        444d218*) echo "refactor(logging): replace print with logging for better output control" ;;
        71962c5*) echo "feat(deps): add missing libraries to requirements.txt" ;;
        ff22a53*) echo "refactor(data): extract posts data to config.json for maintainability" ;;
        d431ce7*) echo "refactor(blog): update post loading with new meta structure and logging" ;;
        8bfd87d*) echo "fix(config): ensure src/config/meta/ is ignored in .gitignore" ;;
        d25fc64*) echo "feat(config): add configuration files and update function type hints" ;;
        cd73d10*) echo "perf(blog): reduce sleep duration for improved processing speed" ;;
        22eb7f7*) echo "feat(config): add git push command and create project documentation" ;;
        *) cat ;;  # 매칭되지 않는 커밋은 원본 메시지 유지
    esac
' -- --all

echo "Git 히스토리 다시 쓰기가 완료되었습니다."
echo "백업 브랜치: backup-before-rewrite"