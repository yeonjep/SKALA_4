package loginauth.global.web;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class PageController {

    @GetMapping("/")
    public String root() {
        return "redirect:/login.html";
    }

    @GetMapping("/login")
    public String login() {
        return "redirect:/login.html";
    }

    @GetMapping("/signup")
    public String signup() {
        return "redirect:/signup.html";
    }

    @GetMapping("/board")
    public String board() {
        return "redirect:/board.html";
    }

    @GetMapping("/posts/write")
    public String postForm() {
        return "redirect:/post-form.html";
    }

    // 인증 구조 소개 페이지를 계속 유지할 경우에만 남김
    @GetMapping("/home")
    public String home() {
        return "redirect:/home.html";
    }
}