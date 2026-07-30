package loginapp;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

/**
 * LoginAppDB의 비밀번호 형식 검증 로직(배열 + String)을 테스트합니다.
 * DB 접속이 필요한 authenticate()는 이 테스트 범위에서 제외했습니다.
 */
class AppTest {

    @Test
    void passwordShorterThanMinimumLengthIsRejected() {
        assertFalse(LoginAppDB.isLongEnough("abc12!"));
    }

    @Test
    void passwordAtMinimumLengthIsAccepted() {
        assertTrue(LoginAppDB.isLongEnough("abcd123!"));
    }

    @Test
    void passwordWithSpecialCharIsDetected() {
        assertTrue(LoginAppDB.containsSpecialChar("abcd123!"));
    }

    @Test
    void passwordWithoutSpecialCharIsRejected() {
        assertFalse(LoginAppDB.containsSpecialChar("abcd1234"));
    }
}
