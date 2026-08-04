# The following practice code is intended for educational purposes only. For contact :  audit@korea.ac.kr, Sungryel Lim Ph.D

# This practice code is not a completed commercial version but has been developed for educational purposes; supplementation is required depending on the deployment objective for use as a commercial service.

# 참고-프리뷰(preview)로 보기 (다시 돌아오려면, 해당 내용을 더블 클릭)
맥북 :
⌘ + Shift + V - 마크다운 프리뷰를 현재 탭에서 열기
⌘ + K 다음 V - 프리뷰를 옆으로(Side by Side) 열기

윈도우 :
Ctrl + Shift + V - 마크다운 프리뷰 열기
Ctrl + K 다음 V - 프리뷰를 옆으로(Side by Side) 열기

# LoginAuth 게시판 확장 모듈

기존 `loginauth-springboot` 프로젝트의 JWT Cookie 인증 구조를 유지하면서 게시판 도메인을 추가하는 확장본입니다.

## 추가 구조

```text
loginauth/post
├── domain/Post.java
├── dto/PostCreateRequest.java
├── dto/PostUpdateRequest.java
├── dto/PostResponse.java
├── repository/PostRepository.java
├── service/PostService.java
├── web/PostController.java
└── exception
    ├── PostNotFoundException.java
    └── PostAccessDeniedException.java
```

## 게시판 API

  Method   URL                 설명
  -------- ------------------- -------------
  GET      `/api/posts`        게시글 목록
  GET      `/api/posts/{id}`   게시글 상세
  POST     `/api/posts`        게시글 작성
  PUT      `/api/posts/{id}`   게시글 수정
  DELETE   `/api/posts/{id}`   게시글 삭제

## 테이블 추가 (게시판)

```sql
CREATE TABLE IF NOT EXISTS posts
(
    id          BIGINT NOT NULL AUTO_INCREMENT,
    title       VARCHAR(200) NOT NULL,
    content     TEXT NOT NULL,
    writer      VARCHAR(50) NOT NULL,

    created_at  TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at  TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    INDEX idx_posts_writer (writer),
    INDEX idx_posts_created_at (created_at)
);
```

## 적용 순서

1. `src/main/java/loginauth/post` 폴더를 기존 프로젝트의 동일 위치에 복사합니다.
2. `src/main/resources/static` 아래의 게시판 HTML/JS/CSS 파일을 복사합니다.
3. `schema-posts.sql` 내용을 기존 `schema.sql` 뒤에 추가합니다.
4. `build.gradle.patch.txt`를 참고해 Spring Data JPA 의존성을 추가합니다.
5. `SecurityConfig.patch.txt`를 참고해 게시판 경로를 인증 대상으로 설정합니다.
6. 기존 `home.html`에서 `/board.html` 링크를 추가합니다.


## 순수 Java vs Spring Boot

  항목        순수 Java        Spring Boot
  ----------- ---------------- ----------------------------
  웹 서버     HttpServer       Embedded Tomcat
  HTML 제공   직접 파일 응답   resources/static 자동 제공
  API         HttpHandler      Controller
  DI          없음             Spring IoC

## 핵심 개념

Spring Boot는 순수 Java에서 반복 구현하는 웹 서버 기능을 자동화한
프레임워크입니다.

## 산출물-문서 도구

Swagger UI를 사용하기 위해서는, build.gralde에 다음을 별도로 추가하여야 합니다.

implementation 'org.springdoc:springdoc-openapi-starter-webmvc-ui:3.0.3'

이어서 다음으로 접속 http://localhost:9090/swagger-ui/index.html

## 웹 서빙과, 엔드 포인트 이해
```text
Spring Boot Application
        │
        ▼
 Embedded Tomcat
        │
        ├── API (/api/**)
        ├── Controller (/login, /board ...)
        └── Static Resource (/css, /js, *.html ...)
```

즉, 별도의 Apache나 Nginx가 없어도 Spring Boot 자체가 웹서버 역할을 합니다.
참고로, 백엔드 엔드 포인트는 Controller가 담당합니다.

```text
@RestController
@RequestMapping("/api/posts")
public class PostController {

    @GetMapping
    public List<PostResponse> findAll() {
        ...
    }
}
```

이렇게 구성하면, GET
http://localhost:9090/api/posts 가 자동으로 열립니다.

```text
PostController
↓
/api/posts
```

그러나, 
```text
src/main/resources/static에 있는
static
 ├── login.html
 ├── board.html
 ├── css
 └── js
```
이 파일들은, Spring Boot가 자동으로 정적 리소스(Static Resource) 로 서비스합니다.
즉, src/main/resources/static/board.html 이 파일들은
http://localhost:9090/board.html 로 바로 접근할 수 있습니다.
(별도로 Controller 필요 없음)

```text
서비스 흐름 정리 :

브라우저
    │
    ▼
GET /login.html
    │
    ▼
Spring Boot
    │
    ▼
resources/static/login.html
```