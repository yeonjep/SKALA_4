package loginauth.config;

import loginauth.security.JwtAuthenticationFilter;
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
                // JWT 쿠키 인증 예제이므로 기본 폼 로그인은 사용하지 않음
                .formLogin(form -> form.disable())
                .httpBasic(basic -> basic.disable())

                // REST API 회원가입·로그인 요청을 위해 비활성화
                .csrf(csrf -> csrf.disable())

                // JWT 기반 Stateless 인증
                .sessionManagement(session ->
                        session.sessionCreationPolicy(
                                SessionCreationPolicy.STATELESS
                        )
                )

                .authorizeHttpRequests(auth -> auth
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

                        .requestMatchers(
                                "/home",
                                "/home.html",
                                "/api/auth/check",
                                "/api/auth/logout"
                        ).authenticated()

                        .anyRequest().authenticated()
                )

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