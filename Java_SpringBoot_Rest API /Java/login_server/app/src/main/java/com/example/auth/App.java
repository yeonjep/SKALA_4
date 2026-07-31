//package login_server;
package com.example.auth;
// 현재 Java 프로그램에서 사용하고 하는 외부 라이브러리를 명시한다.
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

public class App {
    // Map을 생성한다.
    // Map : 이름으로 값을 관리하는 데이터 관리 요소
    // 가입 되어 있는 회원들의 아이디와 비밀번호를 저장해둘 저장소로
    // 사용할 것이다.
    private static final Map<String, String> db = new HashMap<>();

    // static 코드블럭
    // 원래 클래스안에 있는 모든 요소들은 객체라는 것을 만들어야
    // 사용할 수 있다.
    // static이 붙어 있는 것들은 바로 사용이 가능하다.
    // static 코드 블럭은 프로그램 실행시 자동으로 동작되는 부분을
    // 만들고 싶을 때 사용한다.
    static {
        // Map에 데이터를 저장한다.
        // 데이터를 관리할 때 사용할 이름을 사용자 ID 로 사용하고
        // 관리할 값을 비밀번호로 사용 하겠습니다.
        db.put("alice", "pass1234");
        db.put("bob", "mySecret");
    }

    // 자바 프로그램의 시작점
    public static void main(String[] args) {
        // 키보드 입력을 위한 객체를 생성한다.
        // 키보드를 통해 라인단위로 입력을 받는다.
        Scanner sc = new Scanner(System.in);
        System.out.println("=== Day 1: 간이 로그인 시스템 ===");
        // 사용자의 로그인 정보를 입력받는다.
        System.out.print("아이디: ");
        // nextLine() : 키보드로 한 줄 입력 받는다.
        // trim() : 좌우 공백 제거
        String id = sc.nextLine().trim();

        System.out.print("비밀번호: ");
        String pw = sc.nextLine().trim();

        // Map에 사용자가 입력한 ID로 저장되어 있는 값이 있는지 확인
        // if 문 : ( ) 의 코드의 결과가 참인 경우에만 수행되는 코드 관리 요소
        // Map에 입력한 ID 저장된 값이 없으면 if 문 내부의 코드가
        // 동작한다.
        if (!db.containsKey(id)) {
            // 출력
            System.out.println("존재하지 않는 ID입니다.");
            // main 종료 -> 프로그램 종료
            return;
        }

        // 평문비교 (보안 취약점)
        // db.get(id) : 맵에서 id 변수에 들어있는 문자열을 이름으로 하는
        // 값을 가지고 온다.
        // .equals(pw) : pw와 같은지 확인한다.
        if (db.get(id).equals(pw)) {
            System.out.println("로그인 성공! 환영합니다");
        } else {
            System.out.println("비밀번호가 틀렸습니다");
        }
    }
}