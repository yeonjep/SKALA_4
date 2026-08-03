package loginauth.security;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseCookie;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.util.Arrays;
import java.util.Optional;

@Component
public class CookieService {
    public static final String ACCESS_TOKEN = "ACCESS_TOKEN";
    public static final String APP_AUTH = "APP_AUTH";

    private final boolean secure;

    public CookieService(@Value("${app.cookie.secure:false}") boolean secure) {
        this.secure = secure;
    }

    public Optional<String> readAccessToken(HttpServletRequest request) {
        if (request.getCookies() == null) return Optional.empty();
        return Arrays.stream(request.getCookies())
                .filter(cookie -> ACCESS_TOKEN.equals(cookie.getName()))
                .map(Cookie::getValue)
                .findFirst();
    }

    public ResponseCookie accessToken(String token, Duration maxAge) {
        return ResponseCookie.from(ACCESS_TOKEN, token)
                .httpOnly(true).secure(secure).sameSite("Lax")
                .path("/").maxAge(maxAge).build();
    }

    public ResponseCookie appAuth(Duration maxAge) {
        return ResponseCookie.from(APP_AUTH, "1")
                .httpOnly(false).secure(secure).sameSite("Lax")
                .path("/").maxAge(maxAge).build();
    }

    public ResponseCookie delete(String name) {
        return ResponseCookie.from(name, "").httpOnly(ACCESS_TOKEN.equals(name))
                .secure(secure).sameSite("Lax").path("/").maxAge(Duration.ZERO).build();
    }
}
