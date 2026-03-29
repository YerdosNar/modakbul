- # DB:
    - Tables:
        - User:
            - ID        => UUID (Primary Key)
            - username  => char(127)
            - PW        => bcrypt hashing

        - Topic:
            - ID        => UUID (Primary Key)
            - Owner     => User.ID
            - Content   => char(127)
            - Hash (to identify uniqueness)
            - TTL       => LocalTimeDate().now()
            - Current comment number
            - Previous comment number
            - Total comment number

        - Comments:
            - ID        => UUID (Primary Key)
            - Owner     => User.ID
            - Topic     => Topic.ID
            - Content   => char(1023)
- # Functionality:
    - User:
        - Login:
            Enter username, password
        - Create an account:
            - Create a username (required=available),
            - Create a password
        - Create a topic:
            - Choose some topic (required=topic is unique, no duplicates exist)
            - Search for a topic
        - Comment:
            - Leave a comment under a topic (1023 long)

    - Topic:
        - All unique (Hash)
        - Every `Topic` lives up to `TTL`, and when `TTL` expires, then it is deletes including the comments inside the `Topic`.
        - TTL (Time To Live (`LocalTimeDate()`)):\
            When a topic is created, it sets its `ttl = LocalTimeDate().now() + 1 hour`, current comment number to 0. After 1 hour, system checks if there are new comments:
            * If there are new comments, then new TTL is set to `ttl += (totalCommentNumber - currentCommentNumber)` minutes, and `currentCommentNumber = (totalCommentNumber - currentCommentNumber)`.
            * If there are no new comments, then whole `Topic` row is removed with the comments inside it.
        - When a new comment is added, it updates `totalCommentNumber++`

    - Comment:
        - Every comment updates its parent `Topic` TTL by one (one minute).
        - Every comment should be left by an logged in user.
