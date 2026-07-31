// ===== 실행 클래스 =====
public class PatternExample {
    public static void main(String[] args) {
        System.out.println();
        System.out.println("========= Singleton Pattern =========");

        Singleton s1 = Singleton.getInstance();
        Singleton s2 = Singleton.getInstance();

        s1.doSomething();
        System.out.println("s1 == s2 : " + (s1 == s2));

        System.out.println();
        System.out.println("========== Factory Pattern ==========");

        User admin = UserFactory.createUser("admin");
        User normal = UserFactory.createUser("normal");

        admin.printRole();
        normal.printRole();
        System.out.println();
    }
}

/* ===== 싱글턴 패턴 =====
핵심 포인트 :
	• private static final Singleton instance
	• 클래스가 로딩될 때 객체 1개만 미리 생성
	• private Singleton()
	• 외부에서 new Singleton() 불가능
	• getInstance()
	• 유일한 객체 접근 통로
Main에서 사용 :
	• getInstance()를 두 번 호출
	• 하지만 새 객체를 만드는 것이 아니라, 이미 만들어진 같은 객체를 반환 (비교 결과 같음)
*/
class Singleton {
    private static final Singleton instance = new Singleton();

    private Singleton() {}

    public static Singleton getInstance() {
        return instance;
    }

    public void doSomething() {
        System.out.println("싱글턴 객체 동작");
    }
}

/* ===== 팩토리 패턴 =====
핵심 포인트:
    • User 인터페이스를 각각 다르게 구현
    • 실제 동작은 클래스마다 다름
	• 객체 생성 책임을 한 곳에 모음
	• new를 사용하는 위치를 숨김
	• 조건에 따라 다른 객체를 생성
Main에서 사용 :
	• 문자열 값에 따라
        • "admin" → AdminUser 객체 생성
        • 그 외 → NormalUser 객체 생성
	• 반환 타입은 모두 User (다형성)
    • 실제 객체 타입에 따라 다른 메서드 실행
*/
interface User {
    void printRole();
}

class AdminUser implements User {
    public void printRole() {
        System.out.println("관리자입니다.");
    }
}

class NormalUser implements User {
    public void printRole() {
        System.out.println("일반 사용자입니다.");
    }
}

class UserFactory {
    public static User createUser(String type) {
        if ("admin".equals(type)) {
            return new AdminUser();
        }
        return new NormalUser();
    }
}
