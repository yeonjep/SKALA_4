package loginauth.global.security;

import org.springframework.http.ResponseCookie;
import org.springframework.stereotype.Component;

import java.time.Duration;

@Component
public class CookieService {

    public static final String ACCESS_TOKEN = "ACCESS_TOKEN";

    private final CookieProperties properties;

    public CookieService(CookieProperties properties) {
        this.properties = properties;
    }

    public ResponseCookie accessToken(String token, Duration ttl) {
        return ResponseCookie.from(ACCESS_TOKEN, token)
                .httpOnly(true)
                .secure(properties.secure())
                .sameSite("Lax")
                .path("/")
                .maxAge(ttl)
                .build();
    }

    public ResponseCookie deleteAccessToken() {
        return ResponseCookie.from(ACCESS_TOKEN, "")
                .httpOnly(true)
                .secure(properties.secure())
                .sameSite("Lax")
                .path("/")
                .maxAge(Duration.ZERO)
                .build();
    }
}
