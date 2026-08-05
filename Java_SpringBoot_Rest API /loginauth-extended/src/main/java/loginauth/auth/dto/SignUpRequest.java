package loginauth.auth.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record SignUpRequest(
        @NotBlank(message = "아이디를 입력해주세요.")
        @Size(min = 4, max = 50, message = "아이디는 4~50자로 입력해주세요.")
        String username,

        @NotBlank(message = "비밀번호를 입력해주세요.")
        @Size(min = 8, max = 100, message = "비밀번호는 8자 이상 입력해주세요.")
        String password
) {
}
