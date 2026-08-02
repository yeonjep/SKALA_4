package login_server;
//package com.example.auth.login_server;

import java.util.HashMap;
import java.util.Map;

// 사용자 인증 처리를 하는 클래스
public class AuthService {
    private final TokenProvider tokenProvider;
    private final Map<String, User> store = new HashMap<>();

    public AuthService(TokenProvider tokenProvider) {
        this.tokenProvider = tokenProvider;
    }

    // 사용자 등록을 하는 메서드
    public void register(String id, String pw) {
        if (store.containsKey(id)) throw new RuntimeException("이미 존재하는 ID");
        store.put(id, User.of(id, pw));
    }

    // 로그인 처리를 하는 메서드
    public String login(String id, String pw) {
        User user = store.get(id);
        if (user == null || !user.matchPw(pw)) {
            throw new RuntimeException("인증 실패");
        }
        return tokenProvider.generate(id);
    }
}