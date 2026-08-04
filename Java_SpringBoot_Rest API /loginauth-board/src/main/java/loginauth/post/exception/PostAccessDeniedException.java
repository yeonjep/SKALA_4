package loginauth.post.exception;

public class PostAccessDeniedException extends RuntimeException {

    public PostAccessDeniedException() {
        super("작성자만 게시글을 수정하거나 삭제할 수 있습니다.");
    }
}
