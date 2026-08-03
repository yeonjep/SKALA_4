package loginauth.repository;

import loginauth.domain.User;
import java.util.Optional;

public interface UserRepository {
    User save(String username, String encodedPassword);
    Optional<User> findByUsername(String username);
}
