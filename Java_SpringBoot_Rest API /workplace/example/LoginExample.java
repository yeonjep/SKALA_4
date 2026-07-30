import java.util.Scanner;

// 실행 클래스
public class LoginExample {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        AuthService authService = new AuthService();

        try {
            System.out.print("아이디를 입력하세요: ");
            String id = scanner.nextLine();

            authService.login(id);

        } catch (LoginException e) {
            System.out.println(e.getMessage());

        } finally {
            scanner.close();
            System.out.println("프로그램을 종료합니다.");
        }
    }
}

// 사용자 정의 예외
class LoginException extends Exception {
    public LoginException(String message) {
        super(message);
    }
}

// 인증 서비스
class AuthService {
    void login(String id) throws LoginException {
        if (!id.equals("admin")) {
            throw new LoginException("로그인 실패");
        }
        System.out.println("로그인 성공");
    }
}
