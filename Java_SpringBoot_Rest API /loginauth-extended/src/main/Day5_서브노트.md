# Day 5 서브노트 — REST API 도메인 확장(댓글·좋아요·검색)과 애플리케이션 컨테이너화

**학습 목표**: REST API의 HTTP 메서드 전체 체계와 멱등성 개념을 이해하고, 기존 게시판 도메인 위에 댓글·좋아요·검색 기능을 동일한 패턴으로 확장. 또한 완성된 애플리케이션을 도커 이미지로 빌드·실행하며 컨테이너 기반 배포 구조를 이해.

**실습 대상**: `loginauth-extended` 프로젝트(댓글/좋아요 도메인 신규 추가, `posts` 테이블 확장), 그리고 이를 도커화한 `loginauth-extended-app` 이미지

**진행 방식**: 제공받은 리드미와 실습 코드를 기반으로 DB 테이블을 직접 추가하고, 로컬 실행과 도커 빌드 진행

---

## 1. REST API의 HTTP 메서드 전체 정리와 멱등성

REST(Representational State Transfer)는 특정 기술이 아니라 "자원을 이렇게 다루자"는 설계 원칙(아키텍처 스타일)이다. `post`부터는 이 REST API 방식을 그대로 따른다.

| 메서드  | 용도                                                        | 멱등성           |
| ------- | ----------------------------------------------------------- | ---------------- |
| GET     | 자원 조회. 서버 상태를 변경하지 않는 게 원칙                | 멱등             |
| POST    | 새로운 자원 생성. 보낼 때마다 새 자원이 계속 생김           | 비멱등           |
| PUT     | 자원 전체를 새 내용으로 통째로 교체                         | 멱등             |
| PATCH   | 자원의 일부 필드만 수정, 나머지는 유지                      | 상황에 따라 다름 |
| DELETE  | 자원 제거. 이미 삭제된 걸 또 지워도 결과는 "없음"으로 동일  | 멱등             |
| HEAD    | GET과 동일하지만 응답 본문 없이 헤더만 반환                 | 멱등             |
| OPTIONS | 해당 URL이 지원하는 메서드 확인. CORS preflight에 주로 사용 | 멱등             |

멱등성(idempotency): 같은 요청을 한 번 보내든 여러 번 반복해서 보내든, 결과적으로 서버의 상태가 동일하게 유지되는 성질. "매번 완전히 똑같은 응답이 온다"는 뜻이 아니라, "여러 번 반복해도 자원의 최종 상태가 똑같다"는 뜻이다.

---

## 2. 오늘 추가된 도메인: 댓글·좋아요·검색

기존 `PostController`가 REST 원칙을 그대로 따르고 있었던 것처럼, 오늘 추가된 `CommentController`, `PostLikeController`도 동일한 패턴을 반복한다.

### 인증

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/check`
- `POST /api/auth/logout`

### 게시글

- `GET /api/posts` — 목록 조회
- `GET /api/posts/{postId}` — 단건 조회
- `POST /api/posts` — 생성
- `PUT /api/posts/{postId}` — 수정
- `DELETE /api/posts/{postId}` — 삭제

검색·필터·정렬·페이징은 별도 테이블이 필요한 독립 도메인이 아니므로, `post` 도메인의 조회 기능 안에서 쿼리 파라미터 조합으로 구현됨.

```text
GET /api/posts?keyword=spring&searchType=titleContent&writer=test&sort=likes&page=0&size=10
```

### 댓글 (신규)

- `GET /api/posts/{postId}/comments` — 목록 조회
- `POST /api/posts/{postId}/comments` — 생성
- `PUT /api/posts/{postId}/comments/{commentId}` — 수정
- `DELETE /api/posts/{postId}/comments/{commentId}` — 삭제

### 좋아요 (신규)

- `GET /api/posts/{postId}/likes` — 좋아요 상태 조회
- `POST /api/posts/{postId}/likes` — 좋아요 등록
- `DELETE /api/posts/{postId}/likes` — 좋아요 취소

좋아요는 수정(PUT)이 존재하지 않는다.

---

## 3. 테이블 구조 확장

```text
posts
  │
  ├── 1 : N ── comments
  │
  └── 1 : N ── post_likes
```

`posts`에 `view_count`(조회수) 컬럼을 추가하고, `comments`와 `post_likes` 두 테이블을 신규 생성했다. 두 테이블 모두 `post_id`에 외래키(`ON DELETE CASCADE`)를 걸어, 게시글이 삭제되면 그 글에 달린 댓글·좋아요도 함께 삭제되도록 했다. `post_likes`는 `(post_id, username)` 조합에 유니크 제약을 걸어 같은 사용자가 같은 글에 중복으로 좋아요를 등록하지 못하게 제한했다.

```sql
/* 게시글 조회수 컬럼 추가 */
ALTER TABLE posts
    ADD COLUMN IF NOT EXISTS view_count BIGINT NOT NULL DEFAULT 0
        AFTER writer;

/* 댓글 테이블 생성 */
CREATE TABLE IF NOT EXISTS comments
(
    id          BIGINT NOT NULL AUTO_INCREMENT,
    post_id     BIGINT NOT NULL,
    writer      VARCHAR(50) NOT NULL,
    content     TEXT NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_comments_post_id (post_id),
    CONSTRAINT fk_comments_post FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
);

/* 게시글 좋아요 테이블 생성 */
CREATE TABLE IF NOT EXISTS post_likes
(
    id          BIGINT NOT NULL AUTO_INCREMENT,
    post_id     BIGINT NOT NULL,
    username    VARCHAR(50) NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_post_likes_post_username (post_id, username),
    CONSTRAINT fk_post_likes_post FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
);
```

---

## 4. 디렉토리 구조 확장

```text
loginauth
├── auth
│   ├── domain / dto / exception / repository / service / web
├── post
│   ├── domain / dto / exception / repository / service / web
├── comment (신규)
│   ├── domain / dto / exception / repository / service / web
├── like (신규)
│   ├── domain / dto / exception / repository / service / web
└── global
    ├── config / exception / security / web
```

`comment`, `like` 패키지가 새로 추가되었고, 내부 구조는 기존 `auth`, `post`와 동일하다.

---

## 5. 애플리케이션 컨테이너화

지금까지는 DB(MariaDB)만 도커 컨테이너로 실행되었고, 스프링 부트 애플리케이션은 항상 로컬(맥북)에서 `./gradlew bootRun` 또는 `java -jar`로 직접 실행했으나, 오늘은 애플리케이션 자체를 도커 이미지로 빌드하고 컨테이너로 실행했다.

**개념 정리**

- `Dockerfile` — 이미지를 만드는 설계 지시서(레시피)
- `Image` — 그 레시피를 `docker build`로 실행해서 만들어진, 실행에 필요한 모든 것(Java 실행 환경 + jar 파일)이 포함된 읽기 전용 결과물(설계도)
- `Container` — 그 이미지를 `docker run`으로 실행해서 만들어진 인스턴스

`Dockerfile`(.java 소스) → `Image`(.class) → `Container`(new로 생성한 객체)에 대응한다.

**Dockerfile 핵심 단계 (멀티스테이지 빌드)**

- 1단계(`builder`): `gradlew`, `build.gradle` 등을 복사하고 `RUN ./gradlew clean bootJar`로 실행 가능한 jar를 빌드한다.
- 2단계(`stage-1`): 1단계에서 만든 jar 파일만 가벼운 이미지에 옮겨 담아 최종 이미지 용량을 줄인다.
- `ENTRYPOINT ["java", ..., "-jar", "/app/application.jar"]`로 컨테이너가 시작될 때 자동으로 이 jar를 실행하도록 지정한다.

---

## 6. 트러블슈팅

| 문제                                      | 원인                                         | 해결                             |
| ----------------------------------------- | -------------------------------------------- | -------------------------------- |
| MySQL Workbench `No database selected`    | 쿼리 실행 전 활성 스키마 미지정              | 스크립트 앞에 `USE sql_db;` 추가 |
| `docker buildx build requires 1 argument` | 명령어 줄바꿈 없이 겹쳐 입력됨               | 명령어 재입력                    |
| 컨테이너에서 DB 접속 실패 우려            | 컨테이너 안 `localhost`는 자기 자신을 가리킴 | `host.docker.internal:3379` 사용 |
