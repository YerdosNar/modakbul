# 📝 Git Commit Message

이 커밋 메시지는 빈 문자열 유효성 검증 테스트 케이스들을 추가한 뒤 작업 사항을 기록하기 위한 권장 Git 커밋 메시지 본문입니다.

```git
test: 빈 문자열 유효성 검사 우회를 검증하는 TDD baseline 테스트 코드 추가

- 빈 문자열 및 공백 데이터가 API 유입 단에서 422 에러로 차단되지 않는 취약점을 검증하기 위해 각 쓰기/삭제 도메인에 TDD baseline 실패 테스트 케이스 추가
- tests/auth/test_signup.py: 빈 필드로 회원 가입 시도 시 422 에러가 발생하는지 검증하는 test_signup_empty_fields_fail 추가
- tests/auth/test_withdraw.py: 빈 비밀번호로 회원 탈퇴 시도 시 422 에러가 발생하는지 검증하는 test_user_withdrawal_empty_password_fail 추가
- tests/topics/test_create_topic.py: 빈 본문으로 모닥불 생성 시도 시 422 에러가 발생하는지 검증하는 test_create_topic_empty_fields_fail 추가
- tests/comments/test_create_comment.py: 빈 내용으로 장작(댓글) 투척 시도 시 422 에러가 발생하는지 검증하는 test_add_comment_empty_fields_fail 추가
- docs/testing/testing_guide.md: 총 테스트 케이스 수량(40개) 조정 및 TDD baseline 통계 리포트 예시(36 Passed, 4 Failed) 갱신

Note: 해당 테스트 코드들은 현재 서버 로직에 빈 문자열 검증 장치가 구현되지 않아 의도적으로 pytest 실패(FAILED)를 발생시킵니다. 이후 fix 브랜치에서 로직 개선 완료 시 모두 성공(PASSED)으로 전환될 예정입니다.
```
