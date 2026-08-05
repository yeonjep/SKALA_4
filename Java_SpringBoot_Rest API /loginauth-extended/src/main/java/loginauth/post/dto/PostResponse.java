package loginauth.post.dto;

import loginauth.post.domain.Post;

import java.time.LocalDateTime;

public record PostResponse(
        Long id,
        String title,
        String content,
        String writer,
        long viewCount,
        long likeCount,
        long commentCount,
        LocalDateTime createdAt,
        LocalDateTime updatedAt
) {
    public static PostResponse from(
            Post post,
            long likeCount,
            long commentCount
    ) {
        return new PostResponse(
                post.getId(),
                post.getTitle(),
                post.getContent(),
                post.getWriter(),
                post.getViewCount(),
                likeCount,
                commentCount,
                post.getCreatedAt(),
                post.getUpdatedAt()
        );
    }
}
