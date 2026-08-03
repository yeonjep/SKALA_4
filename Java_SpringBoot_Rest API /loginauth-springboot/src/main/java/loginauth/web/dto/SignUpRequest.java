package loginauth.web.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record SignupRequest(

        @NotBlank(message = "아이디를 입력해주세요.")
        @Size(
                min = 4,
                max = 50,
                message = "아이디는 4자 이상 50자 이하로 입력해주세요."
        )
        String username,

        @NotBlank(message = "비밀번호를 입력해주세요.")
        @Size(
                min = 8,
                max = 100,
                message = "비밀번호는 8자 이상 100자 이하로 입력해주세요."
        )
        String password

) {
}