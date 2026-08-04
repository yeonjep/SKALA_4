package loginauth.auth.service;

import loginauth.auth.domain.User;
import loginauth.auth.exception.DuplicateUsernameException;
import loginauth.auth.exception.InvalidCredentialsException;
import loginauth.auth.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public AuthService(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Transactional
    public User signUp(String username, String rawPassword) {
        userRepository.findByUsername(username).ifPresent(user -> {
            throw new DuplicateUsernameException(username);
        });
        return userRepository.save(username, passwordEncoder.encode(rawPassword));
    }

    @Transactional(readOnly = true)
    public User authenticate(String username, String rawPassword) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(InvalidCredentialsException::new);
        if (!passwordEncoder.matches(rawPassword, user.password())) {
            throw new InvalidCredentialsException();
        }
        return user;
    }
}
