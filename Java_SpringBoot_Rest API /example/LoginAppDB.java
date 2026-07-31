import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Scanner;

public class LoginAppDB {

    // ==================================================
    // MariaDB 접속 정보
    // ==================================================
    private static final String DB_URL =
            "jdbc:mariadb://localhost:53301/sql_db";

    private static final String DB_USER = "root";
    private static final String DB_PASSWORD = "SqlDba-1";

    // ==================================================
    // 비밀번호 형식 검증 규칙
    // ==================================================
    private static final int MIN_PASSWORD_LENGTH = 8;

    // 배열: 비밀번호에 반드시 하나 이상 포함되어야 하는 특수문자 목록
    private static final char[] SPECIAL_CHARS = {
            '!', '@', '#', '$', '%', '^', '&', '*'
    };

    public static void main(String[] args) {

        // Scanner도 사용 후 자동으로 닫히도록 try-with-resources 사용
        try (Scanner scanner = new Scanner(System.in)) {

            // ==================================================
            // 1. ID와 비밀번호 입력
            // ==================================================
            System.out.print("아이디: ");
            String username = scanner.nextLine().trim();

            System.out.print("비밀번호: ");
            String password = scanner.nextLine().trim();

            // 빈 값 입력 여부 확인
            if (username.isEmpty() || password.isEmpty()) {
                System.out.println("아이디와 비밀번호를 모두 입력해주세요.");
                return;
            }

            // ==================================================
            // 2. 비밀번호 형식 검증 (배열 활용)
            //    - DB까지 갈 필요 없이 여기서 먼저 걸러낸다.
            // ==================================================
            if (!isLongEnough(password)) {
                System.out.println(
                        "비밀번호는 " + MIN_PASSWORD_LENGTH + "자 이상이어야 합니다."
                );
                return;
            }

            if (!containsSpecialChar(password)) {
                System.out.println(
                        "비밀번호에 특수문자(" + new String(SPECIAL_CHARS)
                                + ") 중 하나를 포함해야 합니다."
                );
                return;
            }

            // ==================================================
            // 3. 로그인 검증 (DB 조회)
            // ==================================================
            LoginResult loginResult =
                    authenticate(username, password);

            // ==================================================
            // 4. 결과 출력
            // ==================================================
            switch (loginResult) {

                case SUCCESS ->
                        System.out.println("로그인에 성공했습니다.");

                case USER_NOT_FOUND ->
                        System.out.println("존재하지 않는 아이디입니다.");

                case INVALID_PASSWORD ->
                        System.out.println("비밀번호가 일치하지 않습니다.");

                case DATABASE_ERROR ->
                        System.out.println(
                                "데이터베이스 처리 중 오류가 발생했습니다."
                        );
            }
        }
    }

    /**
     * 비밀번호 길이가 최소 기준(MIN_PASSWORD_LENGTH) 이상인지 확인합니다.
     *
     * @param password 검사할 비밀번호
     * @return 최소 길이 이상이면 true
     */
    private static boolean isLongEnough(String password) {
        return password.length() >= MIN_PASSWORD_LENGTH;
    }

    /**
     * 비밀번호에 SPECIAL_CHARS 배열에 정의된 특수문자가
     * 하나라도 포함되어 있는지 확인합니다.
     *
     * String -> char 배열로 변환한 뒤, 정의된 특수문자 배열과
     * 하나씩 비교하며 순회합니다. (배열 + 반복문 + 메서드 조합)
     *
     * @param password 검사할 비밀번호
     * @return 특수문자가 하나라도 포함되어 있으면 true
     */
    private static boolean containsSpecialChar(String password) {
        char[] passwordChars = password.toCharArray();

        for (char c : passwordChars) {
            for (char special : SPECIAL_CHARS) {
                if (c == special) {
                    return true;
                }
            }
        }
        return false;
    }

    /**
     * users 테이블에서 username을 조회한 뒤
     * 입력받은 비밀번호와 저장된 비밀번호를 비교합니다.
     *
     * @param username 사용자가 입력한 아이디
     * @param password 사용자가 입력한 비밀번호
     * @return 로그인 처리 결과
     */
    private static LoginResult authenticate(
            String username,
            String password
    ) {

        // username을 기준으로 사용자의 비밀번호 조회
        String sql = """
                SELECT password
                FROM users
                WHERE username = ?
                """;

        /*
         * Connection, PreparedStatement를 사용한 후
         * 자동으로 닫히도록 try-with-resources를 사용합니다.
         */
        try (
                Connection connection =
                        DriverManager.getConnection(
                                DB_URL,
                                DB_USER,
                                DB_PASSWORD
                        );

                PreparedStatement statement =
                        connection.prepareStatement(sql)
        ) {

            /*
             * SQL의 첫 번째 물음표(?)에
             * 사용자가 입력한 username을 전달합니다.
             *
             * PreparedStatement를 사용하면
             * SQL Injection 공격 위험을 줄일 수 있습니다.
             */
            statement.setString(1, username);

            try (ResultSet resultSet =
                         statement.executeQuery()) {

                /*
                 * 조회 결과가 없다면
                 * 해당 username이 존재하지 않는 것입니다.
                 */
                if (!resultSet.next()) {
                    return LoginResult.USER_NOT_FOUND;
                }

                // DB에 저장된 비밀번호 조회
                String savedPassword =
                        resultSet.getString("password");

                /*
                 * 문자열 내용 비교에는 ==가 아니라
                 * equals()를 사용해야 합니다.
                 */
                if (savedPassword.equals(password)) {
                    return LoginResult.SUCCESS;
                }

                return LoginResult.INVALID_PASSWORD;
            }

        } catch (SQLException e) {

            // 실제 DB 오류 내용을 콘솔에 출력
            System.err.println(
                    "DB 연결 또는 조회 오류: "
                            + e.getMessage()
            );

            return LoginResult.DATABASE_ERROR;
        }
    }

    /*
     * 로그인 검증 결과를 구분하기 위한 enum
     */
    private enum LoginResult {
        SUCCESS,
        USER_NOT_FOUND,
        INVALID_PASSWORD,
        DATABASE_ERROR
    }
}


/* 다음 명령어로 컴파일합니다.
 * javac -cp .:mariadb-java-client-3.4.1.jar LoginApp.java 
 */

/* 다음 명령어로 실행합니다.
 * java -cp .:mariadb-java-client-3.4.1.jar LoginApp
 */