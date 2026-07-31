import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

/**
 * DB 없이 메모리(HashMap)만으로 동작하는 간이 로그인 검증기.
 * JDBC/MariaDB 연동 없이 로직(String, 조건문, 메서드)만 빠르게 확인할 때 사용.
 *
 * 주의: 비밀번호를 평문으로 저장/비교합니다.
 *      실제 서비스에서는 반드시 해시(SHA-256 등)로 저장/비교해야 합니다.
 */
public class LoginAppSimple {

    // 간이 DB 역할 (실제 DB 대신 메모리에 저장)
    static Map<String, String> db = new HashMap<>();

    static {
        // 초기 사용자 등록 (평문 저장!)
        db.put("java", "java@test");
        db.put("king", "mySecret");
    }

    public static void main(String[] args) {

        try (Scanner sc = new Scanner(System.in)) {

            System.out.print("아이디: ");
            String id = sc.nextLine().trim();

            System.out.print("비밀번호: ");
            String pw = sc.nextLine().trim();

            if (id.isEmpty() || pw.isEmpty()) {
                System.out.println("아이디와 비밀번호를 모두 입력해주세요.");
                return;
            }

            if (!db.containsKey(id)) {
                System.out.println("존재하지 않는 ID");
                return;
            }

            String savedPw = db.get(id);

            // 문자열 내용 비교는 ==가 아니라 equals()
            if (savedPw.equals(pw)) {
                System.out.println("로그인 성공");
            } else {
                System.out.println("비밀번호가 일치하지 않습니다.");
            }
        }
    }
}
