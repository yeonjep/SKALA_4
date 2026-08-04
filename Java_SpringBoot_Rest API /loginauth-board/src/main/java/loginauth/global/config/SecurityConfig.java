package loginauth.global.config;

import loginauth.global.security.JwtAuthenticationFilter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    public SecurityConfig(
            JwtAuthenticationFilter jwtAuthenticationFilter
    ) {
        this.jwtAuthenticationFilter = jwtAuthenticationFilter;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(
            HttpSecurity http
    ) throws Exception {

        http
                /*
                 * 별도의 AuthController가 로그인 API를 처리하므로
                 * Spring Security 기본 로그인 화면은 사용하지 않습니다.
                 */
                .formLogin(form -> form.disable())
                .httpBasic(basic -> basic.disable())

                /*
                 * 현재 교육용 JWT Cookie 예제에서는 CSRF를 비활성화합니다.
                 * 운영 환경의 Cookie 인증에서는 CSRF 방어를 별도로 적용해야 합니다.
                 */
                .csrf(csrf -> csrf.disable())

                /*
                 * 서버 세션을 생성하지 않고,
                 * 요청마다 JWT Cookie를 검증합니다.
                 */
                .sessionManagement(session ->
                        session.sessionCreationPolicy(
                                SessionCreationPolicy.STATELESS
                        )
                )

                .authorizeHttpRequests(auth -> auth

                        /*
                         * 로그인하지 않아도 접근 가능한 경로
                         */
                        .requestMatchers(
                                "/",
                                "/login",
                                "/login.html",
                                "/signup",
                                "/signup.html",
                                "/css/**",
                                "/js/**",
                                "/favicon.ico",
                                "/api/auth/login",
                                "/api/auth/signup",
                                "/error"
                        ).permitAll()

                        /*
                         * 로그인해야 접근할 수 있는 인증 및 게시판 경로
                         */
                        .requestMatchers(
                                "/home",
                                "/home.html",
                                "/board",
                                "/board.html",
                                "/post-form.html",
                                "/api/auth/check",
                                "/api/auth/logout",
                                "/api/posts/**"
                        ).authenticated()

                        /*
                         * 별도로 명시하지 않은 나머지 요청도
                         * 기본적으로 인증을 요구합니다.
                         */
                        .anyRequest().authenticated()
                )

                /*
                 * JWT Cookie를 검사하는 필터를
                 * 기본 UsernamePasswordAuthenticationFilter보다 먼저 실행합니다.
                 */
                .addFilterBefore(
                        jwtAuthenticationFilter,
                        UsernamePasswordAuthenticationFilter.class
                );

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }
}