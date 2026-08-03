package loginauth.web;

import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import loginauth.domain.User;
import loginauth.security.CookieService;
import loginauth.security.JwtProperties;
import loginauth.security.JwtProvider;
import loginauth.service.AuthService;
import loginauth.web.dto.AuthCheckResponse;
import loginauth.web.dto.LoginRequest;
import org.springframework.http.HttpHeaders;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;
    private final JwtProvider jwtProvider;
    private final JwtProperties jwtProperties;
    private final CookieService cookieService;

    public AuthController(
            AuthService authService,
            JwtProvider jwtProvider,
            JwtProperties jwtProperties,
            CookieService cookieService
    ) {
        this.authService = authService;
        this.jwtProvider = jwtProvider;
        this.jwtProperties = jwtProperties;
        this.cookieService = cookieService;
    }

    /*
     * 회원가입
     *
     * signup.html이 일반 form 방식으로
     * application/x-www-form-urlencoded 요청을 보내므로
     * @RequestBody는 사용하지 않습니다.
     */
    @PostMapping("/signup")
    public void signup(
            @Valid LoginRequest request,
            HttpServletResponse response
    ) throws IOException {

        authService.signUp(
                request.username(),
                request.password()
        );

        response.sendRedirect("/login");
    }

    /*
     * 로그인
     */
    @PostMapping("/login")
    public void login(
            @Valid LoginRequest request,
            HttpServletResponse response
    ) throws IOException {

        User user = authService.authenticate(
                request.username(),
                request.password()
        );

        String token = jwtProvider.createAccessToken(user);

        response.addHeader(
                HttpHeaders.SET_COOKIE,
                cookieService
                        .accessToken(
                                token,
                                jwtProperties.accessTokenTtl()
                        )
                        .toString()
        );

        response.addHeader(
                HttpHeaders.SET_COOKIE,
                cookieService
                        .appAuth(
                                jwtProperties.accessTokenTtl()
                        )
                        .toString()
        );

        response.sendRedirect("/home.html");
    }

    /*
     * 현재 로그인 사용자 인증 확인
     */
    @GetMapping("/check")
    public AuthCheckResponse check(
            Authentication authentication
    ) {
        return new AuthCheckResponse(
                true,
                "jwt-cookie",
                authentication.getName()
        );
    }
}