# 장작 추가 및 가변 연소율 시간 계산 로직
import json
from schemas.comments import CommentCreate
from core.exceptions import TopicNotFoundException, TopicAlreadyExpiredException
from core.similarity import calculate_cosine_similarity
from core.burn_rate import get_new_expires_at
from db.connection import get_db_connection
from datetime import datetime, timezone
from core.config import settings

def create_comment(topic_id: int, comment_data: CommentCreate, user_id: int) -> dict:
    """ 살아있는 모닥불에 새로운 장작(Comment)을 추가하고 시맨틱 산소 감쇠를 적용하여 수명을 연장합니다.

    단일 트랜잭션을 실행하여 데이터 일치성을 확보하여,
    주변 활성 모닥불들과의 시맨틱 유사도를 분석하여 수명 연장 폭을 동적으로 제어합니다.

    Args:
        topic_id (int) : 장작을 넣을 대상 모닥불의 고유 ID
        comment_data (CommentCreate): 추가할 장작의 내용이 담긴 스키마
        user_id (int) 장작을 넣는 사용자의 고유 ID

    Returns:
        dict: DB에 성공적으로 삽입된 장작(댓글)의 상세 레코드 정보.

    Raises:
        TopicNotFoundException: 해당 ID의 모닥불이 DB에 존재하지 않을 경우 발생
        TopicAlreadyExpiredException: 모닥불이 존재하지만 이미 수명이 지나 만료됐거나 '재'인 경우 발생
    """

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. 모닥불 조회 (임베딩 및 아카이브 플래그 포함)
        cursor.execute("""
            SELECT id, content, created_at, expires_at, comment_count, is_ash, embedding
            FROM topics
            WHERE id = ?
        """, (topic_id,))
        topic = cursor.fetchone()

        # 존재하지 않는 경우
        if topic is None:
            raise TopicNotFoundException()

        # SQLite 저장 값 파싱 및 UTC 시간대로 정형화
        created_at = datetime.fromisoformat(topic["created_at"])
        expires_at = datetime.fromisoformat(topic["expires_at"])
        comment_count = topic["comment_count"]
        is_ash = topic["is_ash"]
        embedding_raw = topic["embedding"]

        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        # 2. 이미 만료됐거나 재(is_ash = 1) 상태인 모닥불인지 점검 (지연 삭제 규칙)
        now = datetime.now(timezone.utc)
        if is_ash == 1 or expires_at <= now:
            raise TopicAlreadyExpiredException()


        # 3. 시맨틱 산소(Oxygen Factor) 감쇠 계산
        # topic_similarities 테이블을 활용하여 유사한 주변 모닥불들의 총 댓글 개수(near_comments_sum)를 조회합니다.
        # 기존의 O(N) 루프 돌며 파이썬단에서 코사인 유사도와 JSON 파싱을 수행하는 병목을 인덱스 조회로 대체합니다.
        near_comments_sum = 0
        if embedding_raw:
            try:
                cursor.execute("""
                    SELECT COALESCE(SUM(t.comment_count), 0)
                    FROM topics t
                    WHERE t.expires_at > ?
                        AND t.is_ash = 0
                        AND t.id != ?
                        AND t.id IN (
                            SELECT topic_id_2 FROM topic_similarities WHERE topic_id_1 = ? AND similarity >= ?
                            UNION
                            SELECT topic_id_1 FROM topic_similarities WHERE topic_id_2 = ? AND similarity >= ?
                        )
                """, (now.isoformat(), topic_id, topic_id, settings.SIMILARITY_THRESHOLD, topic_id, settings.SIMILARITY_THRESHOLD))

                row = cursor.fetchone()
                if row:
                    near_comments_sum = row[0]
            except Exception:
                # 안전한 동작을 위해 예외 발생 시 기본값 0 사용
                pass

        oxygen_factor = max(0.3, 1.0 - (near_comments_sum * 0.05))

        # 최종 수명 연장 만료일 산출 (자연 소멸 모델 적용)
        new_expires_at = get_new_expires_at(created_at, expires_at, comment_count, oxygen_factor)

        try:
            # 5. 댓글 INSERT
            cursor.execute("""
                INSERT INTO comments (content, user_id, topic_id, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                comment_data.content,
                user_id,
                topic_id,
                now.isoformat()
            ))

            comment_id = cursor.lastrowid

            # 6. 모닥불 수명 연장 및 댓글 수 갱신 UPDATE
            cursor.execute("""
                UPDATE topics
                SET expires_at = ?, comment_count = comment_count + 1
                WHERE id = ?
            """, (
                new_expires_at.isoformat(),
                topic_id
            ))

            conn.commit()

        except Exception as e:
            conn.rollback()
            raise e

        # 7. 방금 생성된 댓글 반환
        cursor.execute("""
            SELECT id, content, created_at, user_id, topic_id
            FROM comments
            WHERE id = ?
        """, (comment_id,))

        new_comment = cursor.fetchone()

        return dict(new_comment)
