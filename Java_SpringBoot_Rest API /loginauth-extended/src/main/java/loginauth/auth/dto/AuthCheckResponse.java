package loginauth.auth.dto;

public record AuthCheckResponse(
        boolean authenticated,
        String username
) {
}
