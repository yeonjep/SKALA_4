package loginauth.security;

import com.auth0.jwt.JWT;
import com.auth0.jwt.JWTVerifier;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.interfaces.DecodedJWT;
import loginauth.domain.User;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.Date;

@Component
public class JwtProvider {
    private final JwtProperties properties;
    private final Algorithm algorithm;
    private final JWTVerifier verifier;

    public JwtProvider(JwtProperties properties) {
        this.properties = properties;
        this.algorithm = Algorithm.HMAC256(properties.secret());
        this.verifier = JWT.require(algorithm).withIssuer(properties.issuer()).build();
    }

    public String createAccessToken(User user) {
        Instant now = Instant.now();
        return JWT.create()
                .withIssuer(properties.issuer())
                .withIssuedAt(Date.from(now))
                .withExpiresAt(Date.from(now.plus(properties.accessTokenTtl())))
                .withSubject(String.valueOf(user.id()))
                .withClaim("username", user.username())
                .sign(algorithm);
    }

    public DecodedJWT verify(String token) {
        return verifier.verify(token);
    }
}
