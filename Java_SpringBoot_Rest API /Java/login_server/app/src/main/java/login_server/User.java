package login_server;
//package com.example.auth.login_server;
// 암호화 라이브러리를 사용할 거야~
import org.mindrot.jbcrypt.BCrypt;

// 회원 정보를 관리할 객체를 만들기 위한 클래스
public class User {
    // 사용자 아이디
    private final String id;
    // 암호화된 비밀번호
    private final String hashedPw;

    // 생성자 객체를 생성할때 자동으로 호출된다.
    private User(String id, String hashedPw) {
        this.id = id;
        this.hashedPw = hashedPw;
    }

    // 객체를 생성하기 위해 호출할 메서드
    public static User of(String id, String rawPw) {
        // 사용자 비밀번호는 암호화하여 객체에 담아준다.
        String hash = BCrypt.hashpw(rawPw, BCrypt.gensalt(12));
        return new User(id, hash);
    }

    // 암호화된 데이터와 입력한 비밀번호가 같은지 체크해주는 메서드
    public boolean matchPw(String rawPw) {
        return BCrypt.checkpw(rawPw, this.hashedPw);
    }

    public String getId() { return id; }
}