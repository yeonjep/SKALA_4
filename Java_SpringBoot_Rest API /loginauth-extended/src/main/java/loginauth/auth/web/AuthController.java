package loginauth.auth.web;

import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import loginauth.auth.domain.User;
import loginauth.auth.dto.AuthCheckResponse;
import loginauth.auth.dto.LoginRequest;
import loginauth.auth.dto.SignUpRequest;
import loginauth.auth.service.AuthService;
import loginauth.global.security.CookieService;
import loginauth.global.security.JwtProperties;
import loginauth.global.security.JwtProvider;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

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

    @PostMapping("/signup")
    public ResponseEntity<Void> signup(
            @Valid @RequestBody SignUpRequest request
    ) {
        authService.signup(request.username(), request.password());
        return ResponseEntity.noContent().build();
    }

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
                cookieService.accessToken(
                        token,
                        jwtProperties.accessTokenTtl()
                ).toString()
        );

        response.sendRedirect("/board.html");
    }

    @GetMapping("/check")
    public AuthCheckResponse check(Authentication authentication) {
        return new AuthCheckResponse(true, authentication.getName());
    }

    @PostMapping("/logout")
    public ResponseEntity<Void> logout() {
        return ResponseEntity.noContent()
                .header(
                        HttpHeaders.SET_COOKIE,
                        cookieService.deleteAccessToken().toString()
                )
                .build();
    }
}
