from datetime import datetime, timedelta

def create_comment(topic_id: int, comment_data: CommentCreate, user_id: int) -> dict:

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. 모닥불 상태 조회
        cursor.execute("""
            SELECT id, expires_at, comment_count
            FROM topics
            WHERE id = ?
        """, (topic_id,))
        topic = cursor.fetchone()

        if topic is None:
            raise TopicNotFoundException()

        expires_at = datetime.fromisoformat(topic["expires_at"])
        comment_count = topic["comment_count"]

        # 2. 이미 꺼진 모닥불인지 확인
        if expires_at < datetime.utcnow():
            raise TopicAlreadyExpiredException()

        # 3. 가변 연소율 계산
        if comment_count < 10:
            extend_minutes = 10
        elif comment_count < 50:
            extend_minutes = 5
        elif comment_count < 100:
            extend_minutes = 3
        else:
            extend_minutes = 1

        new_expires_at = expires_at + timedelta(minutes=extend_minutes)

        try:
            # 4. 댓글 INSERT
            cursor.execute("""
                INSERT INTO comments (content, user_id, topic_id, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                comment_data.content,
                user_id,
                topic_id,
                datetime.utcnow().isoformat()
            ))

            comment_id = cursor.lastrowid

            # 5. topic 업데이트 (수명 연장 + comment_count 증가)
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

        # 6. 생성된 댓글 반환
        cursor.execute("""
            SELECT id, content, created_at, user_id, topic_id
            FROM comments
            WHERE id = ?
        """, (comment_id,))

        new_comment = cursor.fetchone()

        return dict(new_comment)
