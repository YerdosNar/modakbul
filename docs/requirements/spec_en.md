# 🪵 Modakbul (Bonfire) Requirements Specification

**Version:** 1.1.0  
**Last Modified:** 2026-06-07  
**Project Nature:** Real-time volatile anonymous community backend API  

---

## 1. User Stories

### Epic 1: User Authentication and Authorization (Auth)
- Goal: Visitors can sign up, log in, and become authenticated users of the service.

**US-01** : Users can sign up for the service.
- Description:
    - As a : Visitor
    - I want to : Sign up by entering information such as ID and Password
    - So that : I can create my own account and participate in the Modakbul service.
- Acceptance Criteria:
    - ID, Password, and Nickname must be entered without omission. (Empty spaces alone are rejected.)
    - If a signup attempt is made with an already existing ID, a 409 Conflict error is returned.
    - Passwords must not be stored in plain text in the DB and must be hashed (e.g., using bcrypt).
    - Upon success, a signup completion response is returned with a 201 Created status.

**US-02** : Users can log in with their created account.
- Description:
    - As a : Registered member
    - I want to : Log in with my account credentials
    - So that : I can gain authenticated user permissions, such as lighting a bonfire or adding firewood.
- Acceptance Criteria:
    - If the ID is unregistered or the Password is incorrect, a 401 Unauthorized is returned.
    - Upon providing valid credentials, the server issues and returns a JWT access token.

**US-03** : Users can log out of their logged-in account.
- Description:
    - As a : Logged-in member
    - I want to : Securely log out of the service
    - So that : I can protect my account from being stolen by others on my device or environment.
- Acceptance Criteria:
    - Since JWT is a stateless token format, the server returns a successful response (200 OK) that guides the client to delete the token locally.

---

### Epic 2: Bonfire (Topic) Management
- Goal: Users can create hot issues and view a feed of active issues.

**US-04** : Users can light a new bonfire (Topic).
- Description:
    - As a : Logged-in member
    - I want to : Write a new topic or issue in text format
    - So that : I can gather people's interest and reactions.
- Acceptance Criteria:
    - The server must verify if the user is authenticated upon request, blocking unauthenticated requests.
    - Input values must not be empty or composed entirely of whitespace characters, and must satisfy the length limit.
    - When saving the topic, the author's User ID must be mapped as a foreign key, and a 128-dimensional semantic embedding vector must be calculated and saved alongside it.
    - An appropriate expiration date (e.g., +1 hour after creation) is automatically set as the initial state value.

**US-05** : Users can view the hottest bonfire feed (entire list).
- Description:
    - As a : All users, including non-logged-in visitors
    - I want to : Check the list of active posts
    - So that : I can see what issues people are discussing the most right now.
- Acceptance Criteria:
    - Anyone can view (GET) the feed regardless of their login status.
    - Filters and returns only data whose expiration date has not passed (`is_ash = 0` and `expires_at > now`), applying lazy deletion logic.
    - Returns 200 OK with a default limit of 20 items, supporting limit/offset query parameter pagination.

**US-06** : Users can view the detailed content and firewood (comments) of a specific bonfire.
- Description:
    - As a : All users, including non-logged-in visitors
    - I want to : View the list of comments attached to a specific bonfire along with the post
    - So that : I can read other people's specific reactions and understand the flow of the conversation.
- Acceptance Criteria:
    - Detailed lookup is allowed for both active bonfires and expired ones that have been migrated to the archive tables (`ash_topics`). For expired ones, the response returns with `is_ash = 1` status.
    - Querying a topic ID that does not exist in either active or archive tables returns a 404 Not Found.
    - The list of comments returned within the details supports limit/offset pagination.

---

### Epic 3: Firewood (Comment) Management and Activity
- Goal: Users participate in existing bonfires by leaving opinions, extending their lifespan, and viewing user activity profiles.

**US-07** : Users can add firewood (Comment) to a bonfire to keep the embers alive.
- Description:
    - As a : Logged-in member
    - I want to : Leave a comment on a specific post
    - So that : I can share my opinions and extend the lifespan of the bonfire so it does not go out.
- Acceptance Criteria:
    - The server must verify if the user is authenticated upon request.
    - Comment creation must be rejected (403 Forbidden) for bonfires that are already expired or marked as ash (`is_ash = 1`).
    - Immediately upon successfully saving a comment, the expiration date is updated according to the variable burn-rate and oxygen decay formulas.

**US-08** : Users can view a specific user's public profile and recent activities.
- Description:
    - As a : All users
    - I want to : View a specific user's basic info along with their recently written topics and comments
    - So that : I can understand their recent interests and activity flow.
- Acceptance Criteria:
    - Querying an unregistered user ID returns 404 Not Found.
    - Upon success, returns the user info summary, recent topics list, and recent comments list combined in a single JSON payload.

---

## 2. System Stories (Technical Specification)

### Epic 1: User Authentication and Authorization (Auth)

**SYS-01** : User Signup API and Encryption Processing
- Implement the `POST /api/auth/signup` endpoint and validate input formats using Pydantic.
- Set a UNIQUE constraint on the `username` column in the `users` table to block duplicate signups at the DB schema level, returning 409 Conflict if violated.
- Passwords must be hashed using the `bcrypt` library before being stored in the database `password_hash` field.

**SYS-02** : Login Authentication and Token Issuance
- Implement the `POST /api/auth/login` endpoint to validate credentials.
- Return 401 Unauthorized if they do not match; otherwise, issue a state-less JWT access token.

**SYS-03** : Logout and User Withdrawal
- `POST /api/auth/logout`: Provide a successful response guiding the client to discard the JWT.
- `DELETE /api/auth/me`: Perform user withdrawal for the currently logged-in account. Verifies password correctness, returns 401 if incorrect, and physically deletes the user from the DB. DB `ON DELETE CASCADE` constraints automatically delete all associated topics and comments.

---

### Epic 2: Bonfire (Topic) Management

**SYS-04** : Bonfire Creation, Semantic Analysis, and Lifespan Assignment
- Implement the `POST /api/topics/` endpoint to spawn a new bonfire.
- Extract a 128-dimensional L2-normalized unit vector (virtual embedding) from the text content and store it as a JSON string in the database.
- Calculate cosine similarities against all other active topics, storing relations exceeding `SIMILARITY_THRESHOLD` into the `topic_similarities` table.
- Set the initial lifespan (`expires_at`) to `now + 1 hour`.

**SYS-05** : Lazy Deletion Filtering and Feed Pagination
- When `GET /api/topics/` is called, filter records using `expires_at > now AND is_ash = 0` in the SQL query to return only active data.
- When `GET /api/topics/ashes` is called, return expired bonfires feed using a UNION ALL query combining `ash_topics` and expired active topics.

**SYS-06** : Bonfire Detail and Join Archiving
- When `GET /api/topics/{topic_id}` is called, check both the active `topics` table and the archived `ash_topics` table.
- If the topic is archived or expired, retrieve its comments from the `ash_comments` table and mark `is_ash = 1` in the response payload.

---

### Epic 3: Firewood (Comment) Management and System Maintenance

**SYS-07** : Comment Creation & Oxygen Decay Variable Burn-Rate System
- Bundle comment insertion and topic lifespan extension into a single DB transaction to guarantee rollback safety.
- **Variable Burn-Rate:** The lifespan extension decays exponentially as comments accumulate:
  $$\text{extension\_seconds} = \text{BASE\_MINUTES} \times 60 \times (\text{DECAY\_RATE}^{\text{comment\_count}})$$
- **Oxygen Depletion:** Decreases the extension rate based on comment counts of semantically similar active topics (`near_comments_sum` where cosine similarity $\ge$ `SIMILARITY_THRESHOLD`):
  $$\text{oxygen\_factor} = \max(0.3, 1.0 - (\text{near\_comments\_sum} \times 0.05))$$
- The final lifespan extension is as follows, with a 10-second minimum safety limit:
  $$\text{final\_seconds} = \max(10.0, \text{extension\_seconds} \times \text{oxygen\_factor})$$

**SYS-08** : 2-Phase Chunked Garbage Collection (Archiving)
- **Phase 1 (Logical Lock):** Flag expired topics as `is_ash = 1`. This takes $<1\text{ms}$ and immediately locks the topic, preventing new comments or feeds visibility.
- **Phase 2 (Physical Chunk Migration & Throttling):** Fetch locked topics in batches of size `ARCHIVE_BATCH_SIZE`, copy them into `ash_topics`/`ash_comments` tables, and physically purge them from active tables. Apply `ARCHIVE_THROTTLE_INTERVAL` sleep between loops to prevent database lock starvation.

**SYS-09** : SQLite WAL Mode and Validation Hardening
- Initialize the SQLite database with `PRAGMA journal_mode = WAL` to enhance concurrency.
- Harden the input validation layer by stripping whitespace and rejecting empty inputs across all write endpoints.

---

## 3. Tech Stack

- **Language:** Python 3.10.20
- **Framework:** FastAPI
- **Database:** SQLite3 (WAL mode enabled)
- **DB Access:** Python built-in `sqlite3` module (Raw SQL queries)
- **Authentication:** passlib[bcrypt], PyJWT (Stateless token auth)
- **Background Scheduler:** APScheduler (2-phase background archiving collector)
- **Testing Tools:** pytest, httpx

---

## 4. Directory Structure
```
modakbul/
├── main.py                 # FastAPI entry point & APScheduler configuration
├── api/                    # API Routing Layer
│   ├── dependencies.py     # Shared dependency injection (Depends)
│   └── routers/
│       ├── auth.py         # Login, signup, and account withdrawal endpoints
│       ├── topics.py       # Bonfire creation and feed lookup endpoints
│       ├── comments.py     # Comment/firewood creation endpoints
│       └── users.py        # Integrated user profile endpoint
├── services/               # Business Logic Layer
│   ├── auth_service.py     # Password hashing, validation, and token generation logic
│   ├── topic_service.py    # Similarity calculations and feed formatting logic
│   ├── comment_service.py  # Oxygen decay and variable burn-rate math logic
│   └── user_service.py     # User profile and recent activities compilation logic
├── repositories/           # Data Access Layer
│   ├── auth_repository.py  # Raw SQL queries for user CRUD
│   ├── topic_repository.py # Raw SQL queries for topic CRUD & similarity mapping
│   ├── comment_repository.py # Raw SQL queries for comment insertion & near activity summing
│   └── user_repository.py  # Raw SQL queries for user profiles and user activity lookups
├── schemas/                # Pydantic DTO validation models
│   ├── auth.py             # Signup, withdrawal, and token response schemas
│   ├── topics.py           # Topic requests and responses schemas
│   ├── comments.py         # Comment requests and responses schemas
│   └── users.py            # Integrated profile response schema
├── db/                     # DB Connection and Schema definition
│   ├── connection.py       # Connection pool and context manager
│   └── init_db.py          # WAL mode initialization and database schema setup
├── core/                   # Shared configurations & core utility algorithms
│   ├── config.py           # Environment variables configuration
│   ├── exceptions.py       # Global FastAPI exception handlers
│   ├── burn_rate.py        # Variable burn rate and minimum extension calculations
│   ├── similarity.py       # Cosine similarity calculations
│   └── embedding_utils.py  # 128-dimensional unit vector generator
├── jobs/                   # Background jobs definitions
│   └── scheduler.py        # 2-phase archiving garbage collector implementation
└── tests/                  # Pytest-based isolated test suite
```