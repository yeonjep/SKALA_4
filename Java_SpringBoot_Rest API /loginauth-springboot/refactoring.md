기존 파일에서는 HTTP 서버, 라우팅, DB 접근, 비밀번호 암호화, JWT, 쿠키, CORS, 화면 반환이 하나의 클래스에 포함되어 있었기에 유지보수 확정성에서 제약이 있었습니다.
SpringBoot기반으로 SRP 패턴을 적용하여, 다음과 같이 분리합니다.
---------------------------------------------------
src/main/java/loginauth
├── LoginAuthApplication.java
├── config
│   ├── AppConfig.java
│   └── SecurityConfig.java
├── domain
│   └── User.java
├── repository
│   ├── UserRepository.java
│   └── JdbcUserRepository.java
├── service
│   └── AuthService.java
├── security
│   ├── CookieService.java
│   ├── JwtAuthenticationFilter.java
│   ├── JwtProperties.java
│   └── JwtProvider.java
├── exception
│   ├── DuplicateUsernameException.java
│   └── InvalidCredentialsException.java
└── web
    ├── AuthController.java
    ├── PageController.java
    ├── ApiExceptionHandler.java
    └── dto
        ├── AuthCheckResponse.java
        ├── LoginRequest.java
        └── SignUpRequest.java

AuthController : 회원가입·로그인·인증 확인·로그아웃 HTTP 처리
AuthService : 회원가입과 로그인 업무 로직
UserRepository : 사용자 저장소 추상화
JdbcUserRepository : JdbcTemplate을 이용한 MariaDB 접근
JwtProvider : JWT 생성과 검증
CookieService : JWT 쿠키 생성·조회·삭제
JwtAuthenticationFilter : 요청 쿠키를 검사해 Spring Security 인증 객체 생성
SecurityConfig : URL 접근 권한, CORS, Stateless 정책
ApiExceptionHandler : 예외를 일관된 JSON 응답으로 변환

즉, 기존의 한 파일에 섞여 있던 책임이 SRP 기준으로 나뉘고, AuthService가 구체적인 JDBC 구현체가 아닌 UserRepository 인터페이스에 의존하도록 만들어 DIP도 적용합니다.
----------------------------------------------------

개선된 인증 흐름은 다음과 같습니다.
로그인 요청
   ↓
AuthController
   ↓
AuthService
   ↓
UserRepository
   ↓
BCrypt 비밀번호 검증
   ↓
JwtProvider가 JWT 생성
   ↓
HttpOnly ACCESS_TOKEN 쿠키 발급
-----------------------------

이후 보호된 API 요청에서 다음과 같이 작동하게 됩니다.
브라우저 요청
   ↓
ACCESS_TOKEN 쿠키
   ↓
JwtAuthenticationFilter
   ↓
JWT 서명·issuer·만료시간 검증
   ↓
SecurityContext에 Authentication 등록
   ↓
Controller 접근 허용
------------------

빌드 후, 실행합니다.
./gradlew clean bootJar
java -jar build/libs/loginauth-springboot-0.0.1-SNAPSHOT.jar
------------------------------------------------------------

./gradlew clean bootJar
: 기존 빌드 결과물을 지우고(clean), 실행 가능한 JAR 파일을 새로 생성합니다(bootJar는 Spring Boot 플러그인이 제공하는 태스크로, 의존성까지 포함한 "fat jar"를 만듭니다).
파일명은, settings.gradle의 프로젝트 이름 + build.gradle의 버전이 합쳐져서 결정됩니다.

java -jar build/libs/loginauth-springboot-0.0.1-SNAPSHOT.jar
: 생성된 JAR을 직접 실행합니다. 내장 톰캣(embedded Tomcat)이 포함되어 있어 별도 웹서버 설치 없이 바로 구동됩니다.

http://localhost:8888/login: application.yml 에 server.port=8888로 설정되어 있습니다.(기본값은 8080입니다).

참고, 개발 중 바로 실행 : ./gradlew bootRun (JAR 빌드 없이 바로 애플리케이션 구동, 개발 시 가장 많이 씀)
배포용 JAR 생성 후 실행: ./gradlew clean bootJar → java -jar build/libs/....jar

접속 주소는 다음과 같습니다.
---------------------
http://localhost:8888/login
