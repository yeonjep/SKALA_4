package loginauth.global.exception;

import loginauth.auth.exception.DuplicateUsernameException;
import loginauth.auth.exception.InvalidCredentialsException;
import loginauth.comment.exception.CommentAccessDeniedException;
import loginauth.comment.exception.CommentNotFoundException;
import loginauth.like.exception.DuplicatePostLikeException;
import loginauth.post.exception.PostAccessDeniedException;
import loginauth.post.exception.PostNotFoundException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler({
            DuplicateUsernameException.class,
            DuplicatePostLikeException.class
    })
    public ResponseEntity<Map<String, String>> conflict(RuntimeException exception) {
        return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(Map.of("message", exception.getMessage()));
    }

    @ExceptionHandler({
            InvalidCredentialsException.class
    })
    public ResponseEntity<Map<String, String>> unauthorized(RuntimeException exception) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(Map.of("message", exception.getMessage()));
    }

    @ExceptionHandler({
            PostAccessDeniedException.class,
            CommentAccessDeniedException.class
    })
    public ResponseEntity<Map<String, String>> forbidden(RuntimeException exception) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN)
                .body(Map.of("message", exception.getMessage()));
    }

    @ExceptionHandler({
            PostNotFoundException.class,
            CommentNotFoundException.class
    })
    public ResponseEntity<Map<String, String>> notFound(RuntimeException exception) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(Map.of("message", exception.getMessage()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, String>> validation(MethodArgumentNotValidException exception) {
        String message = exception.getBindingResult().getFieldErrors().stream()
                .findFirst()
                .map(error -> error.getDefaultMessage())
                .orElse("입력값을 확인해주세요.");

        return ResponseEntity.badRequest()
                .body(Map.of("message", message));
    }
}
