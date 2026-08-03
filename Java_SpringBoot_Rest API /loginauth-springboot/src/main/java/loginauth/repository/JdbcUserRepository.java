package loginauth.repository;

import loginauth.domain.User;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Repository;

import java.sql.PreparedStatement;
import java.sql.Statement;
import java.util.Optional;

@Repository
public class JdbcUserRepository implements UserRepository {
    private final JdbcTemplate jdbcTemplate;

    public JdbcUserRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Override
    public User save(String username, String encodedPassword) {
        String sql = "INSERT INTO users(username, password) VALUES (?, ?)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(connection -> {
            PreparedStatement ps = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setString(1, username);
            ps.setString(2, encodedPassword);
            return ps;
        }, keyHolder);
        Number key = keyHolder.getKey();
        return new User(key == null ? null : key.longValue(), username, encodedPassword);
    }

    @Override
    public Optional<User> findByUsername(String username) {
        return jdbcTemplate.query(
                "SELECT id, username, password FROM users WHERE username = ?",
                (rs, rowNum) -> new User(rs.getLong("id"), rs.getString("username"), rs.getString("password")),
                username
        ).stream().findFirst();
    }
}
