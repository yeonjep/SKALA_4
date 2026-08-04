package loginauth.post.exception;

public class PostNotFoundException extends RuntimeException {

    public PostNotFoundException(Long postId) {
        super("게시글을 찾을 수 없습니다. id=" + postId);
    }
}
