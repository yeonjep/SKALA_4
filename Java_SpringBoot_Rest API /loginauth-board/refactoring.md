게시판 도메인을 추가합니다. 기존 인증을 하나의 기능 영역으로 내리고, post와 같은 수준으로 조정합니다.
또한 JWT 필터, 쿠키 서비스, JWT Provider가 게시판뿐 아니라 여러 도메인의 공통 인증 필터로 사용되므로
global 폴더를 만들고 이 곳으로 이동합니다.
----------------------------------
loginauth
├── LoginAuthApplication.java
│
├── auth
│   ├── domain
│   │   └── User.java
│   ├── dto
│   │   ├── LoginRequest.java
│   │   ├── SignUpRequest.java
│   │   └── AuthCheckResponse.java
│   ├── exception
│   │   ├── DuplicateUsernameException.java
│   │   └── InvalidCredentialsException.java
│   ├── repository
│   │   └── UserRepository.java
│   ├── service
│   │   └── AuthService.java
│   └── web
│       ├── AuthController.java
│       └── AuthExceptionHandler.java
│
├── post
│   ├── domain
│   ├── dto
│   ├── exception
│   ├── repository
│   ├── service
│   └── web
│
└── global
    ├── config
    │   └── SecurityConfig.java
    ├── exception
    │   └── GlobalExceptionHandler.java
    └── security
        ├── CookieService.java
        ├── JwtAuthenticationFilter.java
        ├── JwtProperties.java
        └── JwtProvider.java

User, 로그인, 회원가입, 인증 서비스 → auth
JWT 필터, 쿠키 처리, Spring Security 설정 → global.security, global.config
게시글 → post
------------

빌드 후, 실행합니다.
./gradlew clean bootJar
java -jar build/libs/loginauth-board-0.0.1-SNAPSHOT.jar
------------------------------------------------------------

접속 주소는 다음과 같습니다.
http://localhost:9090/login