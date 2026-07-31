package login_server;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import java.util.Date;
import java.security.Key;

// 데이터 암호화 기능을 처리하는 클래스
public class TokenProvider {
    // 데이터 암호화를 위한 암호화 키 값
    private final String SECRET = "day2-secret-key-must-be-at-least-32-chars!!";
    private final Key key = Keys.hmacShaKeyFor(SECRET.getBytes());

    public String generate(String userId) {
        return Jwts.builder()
                .setSubject(userId)
                .setExpiration(new Date(System.currentTimeMillis() + 1800000)) // 30분
                .signWith(key)
                .compact();
    }
}