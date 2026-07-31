/*
try {
    // 예외 발생 가능 코드
} catch (예외타입 e) {
    // 예외 처리
} finally {
    // 항상 실행 (선택)
}

// 예외 던지기
throw new Exception("메시지");

// 메서드에서 예외 선언
throws Exception
*/

import java.util.Scanner;

public class ExceptionExample2 {

    // 숫자 검사 메서드
    static void checkNumber(int num) throws Exception {
        if (num < 0) {
            throw new Exception("음수는 허용되지 않습니다.");
        }
        System.out.println(num + "는 양수입니다.");
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        while (true) {
            try {
                System.out.print("숫자를 입력하세요: ");
                int number = scanner.nextInt();

                // 예외 발생 가능 코드
                checkNumber(number);

            } catch (Exception e) {
                // 음수 입력 시
                System.out.println(e.getMessage());
                System.out.println("프로그램을 종료합니다.");
                break; // 반복 종료 → 프로그램 종료
            }
        }

        scanner.close();
    }
}