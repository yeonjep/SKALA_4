package loginauth.comment.dto;

import loginauth.comment.domain.Comment;

import java.time.LocalDateTime;

public record CommentResponse(
        Long id,
        Long postId,
        String writer,
        String content,
        LocalDateTime createdAt,
        LocalDateTime updatedAt
) {
    public static CommentResponse from(Comment comment) {
        return new CommentResponse(
                comment.getId(),
                comment.getPost().getId(),
                comment.getWriter(),
                comment.getContent(),
                comment.getCreatedAt(),
                comment.getUpdatedAt()
        );
    }
}
