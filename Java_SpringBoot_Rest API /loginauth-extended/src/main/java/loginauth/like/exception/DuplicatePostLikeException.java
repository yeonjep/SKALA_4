package loginauth.like.exception;

public class DuplicatePostLikeException extends RuntimeException {

    public DuplicatePostLikeException() {
        super("이미 좋아요를 누른 게시글입니다.");
    }
}
