# 🪵 Modakbul (Bonfire) Requirements Specification

**Version:** 1.0.0  
**Last Modified:** 2026-04-11
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
    - ID, Password, and Nickname must be entered without omission.
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
    - Upon providing valid credentials, the server issues and returns an authentication token (or session).

**US-03** : Users can log out of their logged-in account.
- Description:
    - As a : Logged-in member
    - I want to : Securely log out of the service
    - So that : I can protect my account from being stolen by others on my device or environment.
- Acceptance Criteria:
    - The server invalidates the client's authentication token (or session).
    - Upon successful processing, a 200 OK response is returned.

### Epic 2: Bonfire (Topic) Management
- Goal: Users can create hot issues and view a feed of active issues.

**US-04** : Users can light a new bonfire (Topic).
- Description:
    - As a : Logged-in member
    - I want to : Write a new topic or issue in text format
    - So that : I can gather people's interest and reactions.
- Acceptance Criteria:
    - The server must verify if the user is authenticated upon request, blocking unauthenticated requests.
    - When saving the post, the author's User ID must be mapped and saved as a foreign key.
    - An appropriate expiration date (e.g., +1 hour after creation) is automatically set as the initial state value.

**US-05** : Users can view the hottest bonfire feed (entire list).
- Description:
    - As a : All users, including non-logged-in visitors
    - I want to : Check the list of active posts
    - So that : I can see what issues people are discussing the most right now.
- Acceptance Criteria:
    - Anyone can view (GET) the feed regardless of their login status.
    - Filters and returns only data whose expiration date has not passed, applying lazy deletion logic.
    - Returns the list sorted in descending order based on the remaining lifespan.
    - Limits the number of posts returned at once (e.g., 20) or implements pagination (cursor/offset).

**US-06** : Users can view the detailed content and firewood (comments) of a specific bonfire.
- Description:
    - As a : All users, including non-logged-in visitors
    - I want to : View the list of comments attached to a specific bonfire along with the post
    - So that : I can read other people's specific reactions and understand the flow of the conversation.
- Acceptance Criteria:
    - Accessing a post whose expiration date has passed by its ID returns a 404 Not Found or 403 Forbidden.
    - If the post is valid, it returns the main body data along with the list of comments belonging to that bonfire.


### Epic 3: Firewood (Comment) Management
- Goal: Users participate in existing bonfires by leaving opinions, extending their lifespan.

**US-07** : Users can add firewood (Comment) to a bonfire to keep the embers alive.
- Description:
    - As a : Logged-in member
    - I want to : Leave a comment on a specific post
    - So that : I can share my opinions and extend the lifespan of the bonfire so it does not go out.
- Acceptance Criteria:
    - The server must verify if the user is authenticated upon request.
    - When saving the comment, both the author's User ID and the associated Topic ID must be mapped.
    - Comment creation must be rejected (404/403) for bonfires that have already passed their expiration date.
    - Immediately upon successfully saving a comment, the expiration date is extended; however, a variable burn rate is applied based on the accumulated number of comments on the bonfire, gradually decreasing the extended time. (Refer to System Stories for detailed formulas.)

---

## 2. System Stories (Technical Specification)

### Epic 1: User Authentication and Authorization (Auth)
- Goal: Securely verify user identity information on the backend system and establish a token-based authentication environment.

**SYS-01** : User Signup API and Encryption Processing
- Description:
    - As a : Backend Server
    - I want to : Receive user signup requests and securely encrypt the password one-way for storage
    - So that : I can prevent account information leaks and ensure data integrity.
- Acceptance Criteria:
    - Implement the `POST /api/auth/signup` endpoint to validate missing input values.
    - Set a UNIQUE constraint on the `username` column in the `users` table of the DB to block duplicate signups at the DB schema level and return a 409 Conflict error.
    - The input Password must not be stored in plain text and must be hashed using `bcrypt` before saving.
    - Return a 201 Created response upon successful processing.

**SYS-02** : Login Authentication and Token Issuance
- Description:
    - As a : Backend Server
    - I want to : Validate login credentials and issue a JWT (or session)
    - So that : The client can prove its authenticated state in subsequent requests.
- Acceptance Criteria:
    - Implement the `POST /api/auth/login` endpoint to compare with DB information.
    - Return 401 Unauthorized if they do not match.
    - If they match, the server generates and returns an authentication token (or session ID) containing access permissions.

**SYS-03** : Logout and Token Invalidation
- Description:
    - As a : Backend Server
    - I want to : Invalidate the existing authentication token/session upon a client's logout request
    - So that : I can block unauthorized abnormal access at the server level.
- Acceptance Criteria:
    - Implement the `POST /api/auth/logout` endpoint.
    - Delete the corresponding session from the server-side session store, or in the case of JWT, induce client-side deletion and perform blacklist processing if necessary, returning 200 OK.

### Epic 2: Bonfire (Topic) Management
- Goal: Handle the creation of volatile data and efficient data retrieval based on lazy deletion.

**SYS-04** : Bonfire Creation and Initial Lifespan Assignment
- Description:
    - As a : System
    - I want to : Receive post creation requests from authenticated users, set an initial lifespan, and save it in the DB
    - So that : I can start the lifecycle of a volatile post.
- Acceptance Criteria:
    - Preemptively validate token validity through middleware or Dependency Injection (`Depends()`) before reaching the Controller.
    - Map the User ID extracted from the token as a foreign key during data insertion.
    - Automatically calculate and insert the default value for the `expires_at` column as '+1 hour' based on the current server time (`datetime.utcnow()`).

**SYS-05** : Lazy Deletion-based Feed Fetching and Pagination
- Description:
    - As a : System
    - I want to : Filter expired data at the query level when fetching the post list and return paginated results
    - So that : I can provide only valid data and prevent database overload and memory excess.
- Acceptance Criteria:
    - When `GET /api/topics` is called, add a `WHERE expires_at > current_time` condition to the query to exclude logically deleted data.
    - Apply `ORDER BY expires_at DESC` sorting to the query.
    - Enforce the `LIMIT 20 OFFSET ?` clause to implement pagination, and apply an Index to the `expires_at` column for query performance.

**SYS-06** : Bonfire Detail and Associated Firewood (Comment) JOIN Query
- Description:
    - As a : System
    - I want to : Load the post body and associated comment list together when querying a specific post ID, and re-verify expiration
    - So that : I can securely combine and provide only the detailed information of valid posts to the client.
- Acceptance Criteria:
    - When `GET /api/topics/{topic_id}` is called, immediately raise a 404 or 403 exception if the `expires_at` of the retrieved object is in the past compared to the current server time.
    - If valid, load the bonfire body data and the associated data from the `comments` table using a JOIN or dual queries, and return the response object.

### Epic 3: Firewood (Comment) Management and System Maintenance

**SYS-07** : Firewood Addition and Variable Burn Rate Algorithm Application
- Description:
    - As a : System (Algorithm Logic)
    - I want to : Incrementally decrease the lifespan extension time upon comment addition based on the accumulated number of comments on the bonfire
    - So that : I can prevent permanent lifespan extension (abusing) of specific posts and guarantee transaction consistency.
- Acceptance Criteria:
    - The comment INSERT query and the bonfire table's `expires_at` UPDATE query must be bundled into a 'single transaction' to allow rollbacks.
    - Upon comment registration, query the accumulated number of comments (`comment_count`) of the corresponding bonfire, calculate the time according to a designated formula (e.g., +10 mins for 0~9, +5 mins for 10~49, etc.), and update it.
    - Apply Row Lock at the DB level or an atomic update query to prevent concurrency issues (Race Condition).

**SYS-08** : Physical Garbage Collector (Background Optimization)
- Description:
    - As a : Background Scheduler
    - I want to : Periodically perform a Hard Delete on expired bonfire data
    - So that : I can prevent DB space waste caused by accumulated dummy data and keep the system optimized.
- Acceptance Criteria:
    - Periodically execute the `DELETE FROM topics WHERE expires_at < current_time` query through a background job (e.g., APScheduler).
    - Configure the `ON DELETE CASCADE` option during DB schema design so that when a bonfire is deleted, its linked firewood (comment) data is automatically deleted in batches.


---

## 3. Tech Stack

- **Language:** Python 3.10.20
- **Framework:** FastAPI
- **Database:** SQLite3
- **DB Access:** Python sqlite3 built-in module
- **Authentication:** passlib[bcrypt], PyJWT
- **IDE:** VSCode
- **Version Control:** Git / Github
- **Environment:** Python venv

---

## 4. Directory Structure
```
modakbul_backend/
├── main.py              # Entry point for running the FastAPI app (starts scheduler, etc.)
├── api/                 # API Endpoint (Router)
│   ├── dependencies.py  #   Common Functions like token validation, logged-in user identification (Depends)
│   └── routers/
│       ├── auth.py         # POST /auth/signup, /auth/login, etc.
│       ├── topics.py       # GET /topics, POST /topics, etc.
│       └── comments.py     # POST /topics/{id}/comments, etc.
├── crud/                # DB Access & Business Logic (Repository+Service)
│   ├── auth.py             # Raw queries for user creation and retrieval
│   ├── topics.py           # Raw queries including bonfire creation, lazy deletion filtering
│   └── comments.py         # Firewood addtiion and variable burn rate time calculation logic
├── schemas/             # Pydantic data validation models
│   ├── auth.py             # Signup input/output forms
│   ├── topics.py           # Bonfire creation input/output forms
│   └── comments.py         # Firewood input/output forms
├── db/                  # Database infrastructure setup
│   ├── connection.py       # Utility returning sqlite3 DB connection object
│   └── init_db.py          # Initialization script collecting CREATE TABLE raw queries
├── core/                # Security and environment configurations
│   ├── config.py           # Constant management like JWT secret key, expiration time
│   └── security.py         # bcrypt hashing functions, JWT creation functions, etc.
└── jobs/                # Background jobs
    └── scheduler.py        # APScheduler (Expired bonfire physical deletion logic)
```