package login_server;
//package com.example.auth.login_server;

public class App {
    public static void main(String[] args) {
        TokenProvider tp = new TokenProvider();
        AuthService service = new AuthService(tp);

        // 회원 가입 프로세스를 가정한다.
        System.out.println("회원가입 진행...");
        service.register("alice", "pass1234");

        // 로그인 프로세스를 가정한다.
        System.out.println("로그인 진행...");
        String token = service.login("alice", "pass1234");
        System.out.println("발급된 JWT: " + token);
    }
}