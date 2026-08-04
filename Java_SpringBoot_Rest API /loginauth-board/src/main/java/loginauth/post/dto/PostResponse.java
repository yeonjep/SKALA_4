package loginauth.post.dto;

import loginauth.post.domain.Post;

import java.time.LocalDateTime;

public record PostResponse(
        Long id,
        String title,
        String content,
        String writer,
        LocalDateTime createdAt,
        LocalDateTime updatedAt
) {
    public static PostResponse from(Post post) {
        return new PostResponse(
                post.getId(),
                post.getTitle(),
                post.getContent(),
                post.getWriter(),
                post.getCreatedAt(),
                post.getUpdatedAt()
        );
    }
}
