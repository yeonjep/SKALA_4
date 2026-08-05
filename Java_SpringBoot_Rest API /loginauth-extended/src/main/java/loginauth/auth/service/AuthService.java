package loginauth.auth.service;

import loginauth.auth.domain.User;
import loginauth.auth.exception.DuplicateUsernameException;
import loginauth.auth.exception.InvalidCredentialsException;
import loginauth.auth.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public AuthService(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder
    ) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Transactional
    public void signup(String username, String password) {
        if (userRepository.existsByUsername(username)) {
            throw new DuplicateUsernameException();
        }

        userRepository.save(
                new User(username, passwordEncoder.encode(password))
        );
    }

    public User authenticate(String username, String password) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(InvalidCredentialsException::new);

        if (!passwordEncoder.matches(password, user.getPassword())) {
            throw new InvalidCredentialsException();
        }

        return user;
    }
}
