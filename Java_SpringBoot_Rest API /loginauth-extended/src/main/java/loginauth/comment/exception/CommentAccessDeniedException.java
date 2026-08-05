package loginauth.comment.exception;

public class CommentAccessDeniedException extends RuntimeException {

    public CommentAccessDeniedException() {
        super("댓글 작성자만 수정하거나 삭제할 수 있습니다.");
    }
}
