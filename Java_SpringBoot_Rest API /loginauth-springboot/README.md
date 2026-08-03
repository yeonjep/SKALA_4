# The following practice code is intended for educational purposes only. For contact :  audit@korea.ac.kr, Sungryel Lim Ph.D

# This practice code is not a completed commercial version but has been developed for educational purposes; supplementation is required depending on the deployment objective for use as a commercial service.


# Spring Boot 프로젝트 구조를 "실행 흐름"을 따라가는 순서로 이해합니다.

1. 진입점(Application.java) : LoginAuthApplication.java부터 시작합니다. Spring Boot는 이 파일의 main() 메서드에서 내장 서버(Tomcat)를 띄우며 실행되므로, 프로젝트의 시작점이 됩니다.

2. 설정(config, application.yml) : 애플리케이션이 어떤 설정으로 동작하는지(DB 연결, 포트 등) 설명합니다. application.yml과 config 패키지를 함께 다룹니다.

3. 요청 진입 → 도메인 → 저장소 순서 (web → service → domain/repository)
- web: 사용자의 HTTP 요청을 받는 컨트롤러 계층 (예: 로그인 요청을 받는 곳)
- service: 실제 비즈니스 로직(인증 처리 등)
- domain: 데이터의 형태(User 엔티티 등)
- repository: DB와 실제로 상호작용하는 계층
즉, "요청이 들어와서 → 처리되고 → 저장되는" 흐름 순서로 이해할 수 있습니다.

4. 보안(security) : 인증/인가를 어떻게 처리하는지(Spring Security 설정) 제시합니다. 로그인 인증 프로그램이니 이 부분이 핵심 포인트가 될 것입니다.

5. 예외 처리(exception)  : 에러 상황을 어떻게 핸들링하는지 제시합니다.

6. 화면(resources/static) : login.html, signup.html, home.html 등 실제 사용자가 보는 화면과, 이 화면들이 앞서 설명한 컨트롤러와 어떻게 연결되는지 이해합니다.


# Spring Boot는 Annotation이 핵심입니다. Annotation은 기계가 읽는 주석이라는 뜻이며, 실제로 일을 하는 건 그 태그를 읽고 반응하는 스프링의 엔진(컴포넌트 스캐너, 리플렉션, 빈 팩토리)입니다.

현재 실습 프로젝트의 패키지 구조(config, domain, exception, repository, security, service, web)에 맞춰 이해

1. 부트스트랩/설정 (config, 메인 클래스)
@SpringBootApplication - 메인 클래스에 붙이는 시작점 표시. @Configuration+@EnableAutoConfiguration+@ComponentScan을 합친 것입니다.
@Configuration — 이 클래스가 빈을 정의하는 설정 클래스임을 표시합니다.
@Bean — @Configuration 클래스 안의 메서드가 반환하는 객체를 스프링 빈으로 등록합니다.
@Value — application.yml의 값을 필드에 하나씩 꺼내 주입합니다.

2. 빈 등록 (전체 공통) : 어노테이션이 붙은 클래스는 개발자가 new로 만들지 않고, 스프링 컨테이너(ApplicationContext)가 대신 객체를 만들어서 보관해 둡니다. 이렇게 스프링이 대신 만들어서 관리하는 객체를 "빈"이라고 부릅니다.
@Component — 가장 기본적인 "이 클래스는 스프링이 관리하는 객체다"라는 표시입니다.
@Service — 비즈니스 로직 담당 빈임을 표시합니다 (@Component의 특수한 형태).
@Repository — DB 접근 담당 빈임을 표시하고, DB 예외를 스프링이 이해하는 예외로 바꿔줍니다.
@Controller / @RestController — 웹 요청을 처리하는 빈. @RestController는 응답을 JSON 등 데이터로 바로 내려줍니다.

3. 의존성 주입
@Autowired — 필요한 빈을 스프링이 찾아서 자동으로 연결(주입)해 줍니다.
@RequiredArgsConstructor(Lombok) — final 필드 기준으로 생성자를 자동 생성해서, 생성자 주입을 간편하게 해줍니다.

4. 웹 (web)
@RequestMapping / @GetMapping / @PostMapping 등 — 어떤 URL과 HTTP 메서드에 이 메서드가 반응할지 지정합니다.
@RequestParam — 쿼리 파라미터(?id=1) 값을 메서드 인자로 받습니다.
@PathVariable — URL 경로 자체에 포함된 값(/users/{id})을 받습니다.
@RequestBody — 요청 본문(JSON)을 객체로 자동 변환해서 받습니다.

5. 도메인 (domain)
@Entity — 이 클래스가 DB 테이블과 매핑되는 객체임을 표시합니다.
@Id — 엔티티의 기본키 필드를 지정합니다.
@GeneratedValue — 기본키 값을 자동으로 채번하는 방식을 지정합니다.

6. 예외 처리 (exception)
@RestControllerAdvice — 여러 컨트롤러에 공통으로 적용될 예외 처리기 클래스임을 표시합니다.
@ExceptionHandler — 특정 종류의 예외가 발생했을 때 실행할 메서드를 지정합니다.

7. 보안 (security)
@EnableWebSecurity — 스프링 시큐리티 설정을 활성화합니다.
@PreAuthorize — 메서드 실행 전에 권한(role)을 검사합니다.

정리하면, "폴더 이름은 껍데기고, 실제로 스프링이 반응하는 건 이 어노테이션들입니다.


# 핵심 : Spring Boot는 명시적 연결이 필요 없습니다.

1. 순수 Java에서는 main()에서 직접 new LoginService(), new UserRepository() 등을 만들어 연결했어야 합니다. 하지만 Spring Boot는 @SpringBootApplication 어노테이션 하나가 그 역할을 대신합니다.

2. 동작 원리
@SpringBootApplication: 이 어노테이션은 사실 3개 어노테이션이 합쳐진 것입니다.
- @Configuration: 이 클래스가 설정 클래스임을 표시
- @EnableAutoConfiguration: Spring Boot가 필요한 설정을 자동으로 구성
- @ComponentScan: 이 클래스가 위치한 패키지(loginauth)부터 하위 패키지를 전부 스캔해서, @Controller, @Service, @Repository, @Component 등이 붙은 클래스를 자동으로 찾아 객체(Bean)로 등록

3. SpringApplication.run()이 하는 일: 이 메서드가 실행되는 순간, 내부적으로
- 내장 Tomcat 서버를 띄우고
- @ComponentScan으로 config, domain, repository, security, service, web 패키지 안의 모든 클래스를 스캔해서
- 어노테이션이 붙은 클래스들을 자동으로 객체화하고, 필요한 의존성끼리 자동으로 연결(의존성 주입, DI)합니다.

4. 그래서 main()이 텅 비어 보이는 이유

명시적으로 "A를 만들고, B에 넣고, C를 실행해라"라고 쓰는 대신, 각 클래스에 붙은 어노테이션(@RestController, @Service 등)이 "나는 이런 역할을 하는 클래스다"라고 선언만 하면, Spring이 컨테이너 실행 시점에 알아서 찾아서 연결합니다.

5. 확인하기
web 패키지 안의 컨트롤러 클래스를 열어보면 클래스 상단에 @RestController나 @Controller가 붙어 있습니다. 그 클래스가 바로 사용자의 HTTP 요청을 처음 받는 지점이며, main()에서 명시적으로 호출하지 않아도 Spring이 이미 등록해놓은 상태이므로 요청이 오면 자동으로 실행됩니다.


# Spring Boot JWT Cookie Login

기존 `SimpleAuthServer.java`를 SRP와 DIP 관점에서 Spring Boot 구조로 분리한 교육용 프로젝트입니다.

# 책임 분리
- `AuthController`: HTTP 요청/응답과 쿠키 발급
- `AuthService`: 회원가입 및 인증 유스케이스
- `UserRepository` / `JdbcUserRepository`: 사용자 영속성
- `JwtProvider`: JWT 생성·검증
- `CookieService`: 인증 쿠키 생성·삭제·조회
- `JwtAuthenticationFilter`: 요청 쿠키를 읽어 Spring Security 인증 객체 생성
- `SecurityConfig`: 접근 정책, CORS, Stateless 정책
- `ApiExceptionHandler`: 오류 응답 통일

# 실행
1. MariaDB 실행 후 `sql_db` 데이터베이스를 생성합니다.
2. JDK 21과 Gradle 8.14+ 또는 9.x를 준비합니다.
3. 필요하면 환경변수를 설정합니다. 예제는 application.yml 파일에 설정되어 있습니다.

```bash
export DB_URL='jdbc:mariadb://localhost:53301/sql_db'
export DB_USER='root'
export DB_PASSWORD='SqlDba-1'
export JWT_SECRET='충분히-긴-운영용-비밀키-32자-이상'
./gradlew bootRun
```

브라우저: `http://localhost:8888/login`

# API
- `POST /api/auth/signup` JSON: `{"username":"user1","password":"password123"}`
- `POST /api/auth/login` JSON: 동일. 성공 시 HttpOnly `ACCESS_TOKEN` 쿠키 발급
- `GET /api/auth/check`: JWT 쿠키 인증 상태 확인
- `POST /api/auth/logout`: 인증 쿠키 삭제

# 운영 전 점검
- HTTPS 환경에서 `COOKIE_SECURE=true`
- JWT secret은 Secret Manager 또는 환경변수 사용
- CSRF 방어 활성화 또는 SPA용 CSRF 토큰 패턴 적용
- Refresh Token, 키 회전, 로그아웃 토큰 폐기 정책 추가
- 프론트엔드와 API가 교차 출처라면 정확한 Origin만 허용
