package loginauth.web;

import loginauth.exception.DuplicateUsernameException;
import loginauth.exception.InvalidCredentialsException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.Map;

@RestControllerAdvice
public class ApiExceptionHandler {
    @ExceptionHandler(DuplicateUsernameException.class)
    ResponseEntity<Map<String, String>> duplicate(DuplicateUsernameException e) {
        return ResponseEntity.badRequest().body(Map.of("code", "DUPLICATE_USERNAME", "message", e.getMessage()));
    }

    @ExceptionHandler(InvalidCredentialsException.class)
    ResponseEntity<Map<String, String>> invalid(InvalidCredentialsException e) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(Map.of("code", "INVALID_CREDENTIALS", "message", e.getMessage()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<Map<String, String>> validation(MethodArgumentNotValidException e) {
        return ResponseEntity.badRequest().body(Map.of("code", "VALIDATION_ERROR", "message", "입력값을 확인하세요."));
    }
}
