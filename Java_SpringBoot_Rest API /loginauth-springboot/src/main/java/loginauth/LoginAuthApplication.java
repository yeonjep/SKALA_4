package loginauth;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class LoginAuthApplication {
    public static void main(String[] args) {
        SpringApplication.run(LoginAuthApplication.class, args);
    }
}

// 스프링 부트 프로젝트에서 흔히 쓰는 "계층별(레이어별) 패키지 구조" 관행입니다. 보통 이렇게 나눕니다.

// controller(또는 web) — HTTP 요청을 받는 계층
// service — 비즈니스 로직 계층
// repository(또는 dao) — DB 접근 계층
// domain(또는 entity, model) — @Entity 같은 도메인 객체
// dto — 계층 간 데이터 전달용 객체
// config — 설정 클래스
// exception — 예외 및 예외 처리기
// security — 인증/인가 관련 설정


// 실행 시점 기준으로 정리하면 다음과 같습니다.

// 1. LoginAuthApplication.java의 main() 실행 : JVM이 가장 먼저 찾는 지점입니다. 여기서 SpringApplication.run(LoginAuthApplication.class, args)가 호출되면서 스프링 부트 부팅이 시작됩니다.

// 2. src/main/resources/application.yml 로드 : 빈(Bean)을 만들기 전에 먼저 환경(Environment)을 구성합니다. DB 접속 정보, 포트 같은 설정값이 여기서 읽혀 이후 단계에서 쓰입니다. 평소 자바 코드에서는 UserRepository repo = new UserRepository();처럼 개발자가 직접 new로 객체를 만듭니다. 그런데 스프링에서는 @Repository, @Service 같은 어노테이션이 붙은 클래스는 개발자가 new로 만들지 않고, 스프링 컨테이너(ApplicationContext)가 대신 객체를 만들어서 보관해 둡니다. 이렇게 스프링이 대신 만들어서 관리하는 객체를 "빈"이라고 부릅니다.

// 3. 컴포넌트 스캔 범위 결정 : LoginAuthApplication.java가 loginauth 패키지에 있으므로, @SpringBootApplication에 포함된 @ComponentScan이 loginauth와 그 하위 패키지 전부(config, domain, exception, repository, security, service, web)를 스캔 대상으로 잡습니다. 여기서 이 여섯 개 폴더가 스캔 범위 안에 들어오는 이유가 "메인 클래스가 그 상위 패키지에 있기 때문"입니다.

// 4. config/ 처리 : @Configuration 클래스들이 먼저 등록됩니다. 다른 빈들이 이 설정에 의존하는 경우가 많아 우선순위가 높습니다.

// 5. security/ 처리 : Spring Security 필터 체인 설정이 등록됩니다. 이후 들어오는 모든 요청이 이 필터를 거치게 됩니다.

// 6. domain/ 스캔 : @Entity 클래스들이 JPA에 의해 인식되고, DB 접속 정보(2번에서 읽은 설정)를 바탕으로 테이블과 매핑됩니다.

// 7. repository/ 처리 : Spring Data JPA가 domain의 엔티티 정보를 바탕으로 리포지토리 인터페이스의 구현체를 자동으로 만들어줍니다.

// 8. service/ 처리 : @Service 빈들이 등록되면서 repository를 주입받습니다.

// 9. web/ 처리 : 컨트롤러 빈들이 등록되고 service를 주입받으며, URL과 메서드가 매핑됩니다.

// 10. exception/ 처리 : @ControllerAdvice 등 예외 처리 핸들러가 등록되어, 이후 컨트롤러에서 발생하는 예외를 가로챌 준비를 마칩니다.

// 11. 내장 톰캣 기동 : 모든 빈이 완성되면 application.yml에 설정된 포트로 내장 웹서버가 열리고, 요청을 받을 준비가 끝납니다.

// 4~9번이 실제로는 "폴더 순서대로 하나씩 처리"되는 게 아니라 스프링이 의존관계 그래프를 보고 필요한 순서대로 빈을 만드는 것입니다. 다만 설정→보안→도메인/리포지토리→서비스→컨트롤러→예외처리라는 흐름 자체는 실제 의존 방향과 일치해서, "왜 이런 폴더 구조로 나누는가"를 이해할 수 있습니다.
