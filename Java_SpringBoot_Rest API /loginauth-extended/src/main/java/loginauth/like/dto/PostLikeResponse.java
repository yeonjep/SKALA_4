package loginauth.like.dto;

public record PostLikeResponse(
        Long postId,
        boolean liked,
        long likeCount
) {
}
