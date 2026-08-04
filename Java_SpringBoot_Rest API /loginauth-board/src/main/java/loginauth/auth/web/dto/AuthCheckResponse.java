package loginauth.auth.web.dto;

public record AuthCheckResponse(boolean ok, String via, String username) {
}
