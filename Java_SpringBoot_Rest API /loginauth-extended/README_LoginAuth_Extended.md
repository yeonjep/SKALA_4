# The following practice code is intended for educational purposes only. For contact : audit@korea.ac.kr, Sungryel Lim Ph.D

# This practice code is not a completed commercial version but has been developed for educational purposes; supplementation is required depending on the deployment objective for use as a commercial service.

# LoginAuth Board Extended

기존 Spring Boot JWT Cookie 인증 게시판을 확장하여 다음 기능을 추가한 프로젝트입니다.

# REST는 Representational State Transfer의 약자입니다. 특정 기술이 아니라 "자원을 이렇게 다루자"는 설계 원칙(아키텍처 스타일)입니다.

post부터는 REST API 방식이라고 볼 수 있습니다.

REST API에서 자주 쓰는 HTTP 메서드들을 정리하면 다음과 같습니다.

# GET 조회 :

자원을 읽어올 때 사용합니다. 서버의 상태를 변경하지 않는 게 원칙입니다.

# POST 생성 :

새로운 자원을 만들 때 사용합니다. 실행할 때마다 새 자원이 계속 생겨나므로, 같은 요청을 여러 번 보내면 결과가 매번 달라집니다. (비멱등, non-idempotent)

# PUT 전체 수정(교체) :

자원 전체를 새로운 내용으로 통째로 교체할 때 사용합니다. 같은 요청을 여러 번 보내도 결과가 동일합니다. (멱등, idempotent)

# PATCH 부분 수정 :

자원의 일부 필드만 수정할 때 사용합니다. PUT과 달리 지정한 필드만 바꾸고 나머지는 유지합니다.

# DELETE 삭제 :

자원을 제거할 때 사용합니다. 이미 삭제된 걸 다시 삭제 요청해도 결과적으로 "없음" 상태는 동일하므로 멱등으로 간주됩니다.

# HEAD :

GET과 동일하지만 응답 본문(body) 없이 헤더만 받습니다. 자원이 존재하는지, 크기가 얼마인지만 확인하고 싶을 때 사용합니다.

# OPTIONS :

해당 URL에서 어떤 메서드들을 지원하는지 확인할 때 사용합니다. CORS(교차 출처 요청) 처리 시 브라우저가 자동으로 먼저 보내는 사전 요청(preflight)에 주로 쓰입니다.

\*참고 : 멱등성(idempotency)은 같은 요청을 한 번 보내든 여러 번 반복해서 보내든, 결과적으로 서버의 상태가 동일하게 유지되는 성질을 말합니다.
핵심은 "결과 상태" 즉, 요청을 여러 번 보내도 최종적으로 자원의 상태가 똑같으면 멱등입니다. (매번 완전히 똑같은 응답이 와야 한다는 뜻은 아닙니다.)

PostController가 REST의 핵심 원칙들을 그대로 따르고 있습니다.

GET /api/posts > 목록 조회
GET /api/posts/{id} > 단건 조회
POST /api/posts > 생성
PUT /api/posts/{id} > 수정
DELETE /api/posts/{id} > 삭제

이번에 추가된 것

- 댓글(Comment)
- 게시글 좋아요(PostLike)
- 게시글 검색·필터·정렬·페이징(Post Search)

CommentController도 REST의 핵심 원칙들을 그대로 따르고 있습니다.

GET /api/posts/{postId}/comments > 목록 조회
POST /api/posts/{postId}/comments > 생성
PUT /api/posts/{postId}/comments/{commentId} > 수정3  
DELETE /api/posts/{postId}/comments/{commentId} > 삭제

PostLikeController 역시 REST의 핵심 원칙들을 그대로 따르고 있습니다.

GET /api/posts/{postId}/likes > 좋아요 상태 조회
POST /api/posts/{postId}/likes > 좋아요 등록
DELETE /api/posts/{postId}/likes > 좋아요 취소

## 실행 환경

- Java 21
- Spring Boot 4.1.0
- MariaDB
- Gradle

## 테이블 추가

```text
posts
  │
  ├── 1 : N ── comments
  │
  └── 1 : N ── post_likes


                    +-----------+
                    |   users   |
                    +-----------+
                    | id        |
                    | username  |
                    | password  |
                    +-----------+
                           │
           writes          │          writes
      ┌──────────────────────────────────────┐
      │                                      │
      ▼                                      ▼

+----------------+     1       N     +----------------+
|     posts      |──────────────────>|    comments    |
+----------------+                   +----------------+
| id             |                   | id             |
| user_id        |                   | post_id        |
| title          |                   | user_id        |
| content        |                   | content        |
| view_count     |                   +----------------+
+----------------+
        │
        │
        │ 1
        │
        └──────────────────────► +----------------+
                                 |   post_likes   |
                                 +----------------+
                                 | id             |
                                 | post_id        |
                                 | user_id        |
                                 +----------------+
```

````sql
/* 1. 게시글 조회수 컬럼 추가 */

ALTER TABLE posts
    ADD COLUMN IF NOT EXISTS view_count BIGINT NOT NULL DEFAULT 0
        AFTER writer;

/* 2. 댓글 테이블 생성 */

CREATE TABLE IF NOT EXISTS comments
(
    id          BIGINT NOT NULL AUTO_INCREMENT,
    post_id     BIGINT NOT NULL,
    writer      VARCHAR(50) NOT NULL,
    content     TEXT NOT NULL,

    created_at  TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at  TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    INDEX idx_comments_post_id (post_id),
    INDEX idx_comments_writer (writer),
    INDEX idx_comments_created_at (created_at),

    CONSTRAINT fk_comments_post
        FOREIGN KEY (post_id)
        REFERENCES posts (id)
        ON DELETE CASCADE
);

/* 3. 게시글 좋아요 테이블 생성 */

CREATE TABLE IF NOT EXISTS post_likes
(
    id          BIGINT NOT NULL AUTO_INCREMENT,
    post_id     BIGINT NOT NULL,
    username    VARCHAR(50) NOT NULL,

    created_at  TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    /*
     * 같은 사용자가 같은 게시글에
     * 좋아요를 중복 등록하지 못하도록 제한
     */
    UNIQUE KEY uk_post_likes_post_username (
        post_id,
        username
    ),

    INDEX idx_post_likes_post_id (post_id),
    INDEX idx_post_likes_username (username),

    CONSTRAINT fk_post_likes_post
        FOREIGN KEY (post_id)
        REFERENCES posts (id)
        ON DELETE CASCADE
);

기본 DB 설정:

```text
jdbc:mariadb://localhost:53301/sql_db
root / SqlDba-1
````

환경 변수로 변경할 수 있습니다.

```bash
export DB_URL='jdbc:mariadb://localhost:53301/sql_db'
export DB_USER='root'
export DB_PASSWORD='SqlDba-1'
export JWT_SECRET='32자 이상의 충분히 긴 비밀키'
```

## 디렉토리 구조 추가/정리

```text
loginauth
├── auth
│   ├── domain
│   ├── dto
│   ├── exception
│   ├── repository
│   ├── service
│   └── web
├── post
│   ├── domain
│   ├── dto
│   ├── exception
│   ├── repository
│   ├── service
│   └── web
├── comment (추가)
│   ├── domain
│   ├── dto
│   ├── exception
│   ├── repository
│   ├── service
│   └── web
├── like (추가)
│   ├── domain
│   ├── dto
│   ├── exception
│   ├── repository
│   ├── service
│   └── web
└── global
    ├── config
    ├── exception
    ├── security
    └── web
```

## 실행

```bash
./gradlew clean bootJar
java -jar build/libs/loginauth-extended-0.0.1-SNAPSHOT.jar
```

브라우저:

```text
http://localhost:9999/login.html
```

## 산출물-문서 도구

Swagger UI를 사용하기 위해서는, build.gralde에 다음을 별도로 추가하여야 합니다.

implementation 'org.springdoc:springdoc-openapi-starter-webmvc-ui:3.0.3'

이어서 다음으로 접속 http://localhost:9999/swagger-ui/index.html

## 패키지 구조

```text
loginauth
├── auth
├── post
├── comment
├── like
└── global
```

검색·필터·페이징은 독립 테이블이 필요한 도메인이 아니므로 `post` 도메인의 조회 기능으로 구현했습니다.

## 주요 API

### 인증

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/check`
- `POST /api/auth/logout`

### 게시글

- `GET /api/posts`
- `GET /api/posts/{postId}`
- `POST /api/posts`
- `PUT /api/posts/{postId}`
- `DELETE /api/posts/{postId}`

검색 예시:

```text
GET /api/posts?keyword=spring&searchType=titleContent&writer=test&sort=likes&page=0&size=10
```

### 댓글

- `GET /api/posts/{postId}/comments`
- `POST /api/posts/{postId}/comments`
- `PUT /api/posts/{postId}/comments/{commentId}`
- `DELETE /api/posts/{postId}/comments/{commentId}`

### 좋아요

- `GET /api/posts/{postId}/likes`
- `POST /api/posts/{postId}/likes`
- `DELETE /api/posts/{postId}/likes`

좋아요는 `(post_id, username)` 유일성 제약으로 중복 등록을 방지합니다.
