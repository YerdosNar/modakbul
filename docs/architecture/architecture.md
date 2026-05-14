- # DB:
    - Tables:
        - users:
            - id                => Primary Key Auto Increment
            - username          => VARCHAR(31)
            - password_hash     => bcrypt hashing (60)

        - topics:
            - ID            => Primary Key Auto Increment
            - user_id       => References users (id)
            - content       => VARCHAR(127)
            - comment_count => INTEGER DEFAULT 0
            - expires_at    => DATETIME NOT NULL
            - created_at    => DATETIME DEFAULT CURRENT_TIMESTAMP

        - comments:
            - ID        => Primary key Auto Increment
            - user_id   => References users (id)
            - topic_id  => References topics (id)
            - content   => VARCHAR(1023)

- # Functionality:
    - User:
        - Login:
            Enter username(32), password(63?), nickname(32)
        - Create an account:
            - Create a username (required=available),
            - Create a password
        - Create a topic:
            - Choose some topic (required=topic is unique, no duplicates exist)
            - Search for a topic
        - Comment:
            - Leave a comment under a topic (1023 long)

    - Topic:
        - Every `Topic` lives up to `expires_at`, and when `expires_at` expires, then it is deletes including the comments inside the `Topic`.
        - expires_at (`DATETIME DEFAULT CURRENT_TIMESTAMP + 1 hour`):\
            When a topic is created, it sets its `CURRENT_TIMESTAMP + 1 hour`, current comment number to 0. After 1 hour, system checks if there are new comments:
            * If there are new comments, then new TTL is set to `expires_at += 60` minutes.
            * If there are no new comments, then whole `Topic` row is removed with the comments inside it.
        - When a new comment is added, it updates `comment_count++`

    - Comment:
        - Every comment updates its parent `Topic` expires_at by one (one minute).
        - Every comment should be left by an logged in user.

- # ENDPOINTS:
    - Users:
        - **POST**: `/api/auth/signup`: Create a new account
        - **POST**: `/api/auth/login`: Authenticate
        - **POST**: `/api/auth/logout`: Logout

    - Topics:
        - **POST**: `/api/topics`: Start a new campfire (`user_id` required)
        - **GET**: `/api/topics`: List all active, unexpired campfires (support paging)
        - **GET**: `/api/topics/{topic_id}`: Retrieve a specific topic by ID

    - Comments:
        - **POST**: `/topics/{topic_id}/comments`: Add a comment to existing topic
