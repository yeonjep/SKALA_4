package loginauth.security;

import com.auth0.jwt.exceptions.JWTVerificationException;
import com.auth0.jwt.interfaces.DecodedJWT;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final CookieService cookieService;
    private final JwtProvider jwtProvider;

    public JwtAuthenticationFilter(
            CookieService cookieService,
            JwtProvider jwtProvider
    ) {
        this.cookieService = cookieService;
        this.jwtProvider = jwtProvider;
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {

        cookieService.readAccessToken(request).ifPresent(token -> {
            try {
                DecodedJWT jwt = jwtProvider.verify(token);

                String username =
                        jwt.getClaim("username").asString();

                UsernamePasswordAuthenticationToken authentication =
                        new UsernamePasswordAuthenticationToken(
                                username,
                                null,
                                List.of(
                                        new SimpleGrantedAuthority("ROLE_USER")
                                )
                        );

                SecurityContextHolder
                        .getContext()
                        .setAuthentication(authentication);

            } catch (JWTVerificationException exception) {
                SecurityContextHolder.clearContext();
            }
        });

        filterChain.doFilter(request, response);
    }
}