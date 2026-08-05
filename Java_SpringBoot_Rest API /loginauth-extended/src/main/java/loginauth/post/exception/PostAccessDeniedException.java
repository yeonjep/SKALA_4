package loginauth.post.exception;

public class PostAccessDeniedException extends RuntimeException {

    public PostAccessDeniedException() {
        super("게시글 작성자만 수정하거나 삭제할 수 있습니다.");
    }
}
