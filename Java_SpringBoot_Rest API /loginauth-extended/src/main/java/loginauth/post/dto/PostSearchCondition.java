package loginauth.post.dto;

public record PostSearchCondition(
        String keyword,
        String searchType,
        String writer,
        String sort
) {
}
