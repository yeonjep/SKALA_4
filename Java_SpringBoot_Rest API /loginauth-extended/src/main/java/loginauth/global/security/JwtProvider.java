package loginauth.global.security;

import com.auth0.jwt.JWT;
import com.auth0.jwt.JWTVerifier;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.interfaces.DecodedJWT;
import loginauth.auth.domain.User;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.Date;

@Component
public class JwtProvider {

    private final JwtProperties properties;
    private final Algorithm algorithm;
    private final JWTVerifier verifier;

    public JwtProvider(JwtProperties properties) {
        if (properties.secret() == null || properties.secret().isBlank()) {
            throw new IllegalArgumentException("JWT secret must not be blank");
        }

        this.properties = properties;
        this.algorithm = Algorithm.HMAC256(properties.secret());
        this.verifier = JWT.require(algorithm)
                .withIssuer(properties.issuer())
                .build();
    }

    public String createAccessToken(User user) {
        Instant now = Instant.now();

        return JWT.create()
                .withIssuer(properties.issuer())
                .withSubject(user.getUsername())
                .withIssuedAt(Date.from(now))
                .withExpiresAt(Date.from(now.plus(properties.accessTokenTtl())))
                .sign(algorithm);
    }

    public String getUsername(String token) {
        DecodedJWT jwt = verifier.verify(token);
        return jwt.getSubject();
    }

    public boolean isValid(String token) {
        try {
            verifier.verify(token);
            return true;
        } catch (RuntimeException exception) {
            return false;
        }
    }
}
