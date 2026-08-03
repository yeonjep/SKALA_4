package loginauth.exception;

public class DuplicateUsernameException extends RuntimeException {
    public DuplicateUsernameException(String username) { super("이미 존재하는 사용자명입니다: " + username); }
}
