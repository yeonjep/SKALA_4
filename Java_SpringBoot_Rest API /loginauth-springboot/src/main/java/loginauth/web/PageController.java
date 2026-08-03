package loginauth.web;

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

    @GetMapping("/home")
    public String home() {
        return "redirect:/home.html";
    }
}