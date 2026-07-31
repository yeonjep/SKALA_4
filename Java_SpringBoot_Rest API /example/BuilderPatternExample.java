/*
Java는 언어 특성상
	• 객체 수명 관리
	• 생성 시점 제어
	• 생성 책임 분리
	• 불변성 유지
등이 코드 품질의 핵심이므로,디자인 패턴 중에서도 생성 (Creational) 패턴이 가장 체감 효과가 크며
싱글턴, 팩토리, 빌더 패턴 3가만 알아도 체급이 달라짐 (=코드를 ‘쓸 수 있다’ 수준을 넘어, ‘의도를 설계하며 쓴다’는 단계로 올라감)
*/

public class BuilderPatternExample {

    public static void main(String[] args) {

        System.out.println("\n========= Builder Pattern Example ==========");

        // 빌더 패턴 사용
        User user = new User.Builder()
                .id("admin")
                .password("1234")
                .role("ADMIN")
                .build();

        // 출력 포맷 (의미가 드러나도록)
        System.out.println("[User Object Created]");
        System.out.println(" - ID        : " + user.getId());
        System.out.println(" - PASSWORD  : " + user.getPassword());
        System.out.println(" - ROLE      : " + user.getRole());
        System.out.println(" - ACTIVE    : " + user.isActive());

        System.out.println(
            "\n============================================\n" +
            "[User Object Created]\n" +
            " - 빌더 패턴을 통해 객체 생성이 완료됨\n\n" +
            "[Field Mapping]\n" +
            " - ID / PASSWORD / ROLE / ACTIVE\n" +
            " - 빌더에서 설정한 값들이 User 객체에 정확히 반영됨\n\n" +
            "[Default Value]\n" +
            " - ACTIVE : true\n" +
            " - 명시적으로 설정하지 않았지만 기본값이 적용됨\n"
    );
    }
}

// ===== 빌더 패턴 대상 클래스 =====
class User {

    private final String id;
    private final String password;
    private final String role;
    private final boolean active;

    /* private 생성자
    • 외부에서 new User()를 직접 못 하게 차단
	• 빌더 패턴 사용을 강제
    */
    private User(Builder builder) {
        this.id = builder.id;
        this.password = builder.password;
        this.role = builder.role;
        this.active = builder.active;
    }

    // Getter 메서드
    public String getId() {
        return id;
    }

    public String getPassword() {
        return password;
    }

    public String getRole() {
        return role;
    }

    public boolean isActive() {
        return active;
    }

    // ===== Builder =====
    public static class Builder {
        private String id;
        private String password;
        private String role = "USER";   // 기본값
        private boolean active = true;  // 기본값
        /* 기본값 설정 의미 :
        • 설정하지 않으면 기본값 자동 적용
        • 생성자 오버로딩 없이도 다양한 조합 가능
         */
        public Builder id(String id) {
            this.id = id;
            return this;
        }

        public Builder password(String password) {
            this.password = password;
            return this;
        }

        public Builder role(String role) {
            this.role = role;
            return this;
        }

        public Builder active(boolean active) {
            this.active = active;
            return this;
        }

        public User build() {
            return new User(this);
        }
    }
}