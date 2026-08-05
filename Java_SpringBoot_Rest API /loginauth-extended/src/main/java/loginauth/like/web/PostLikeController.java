package loginauth.like.web;

import loginauth.like.dto.PostLikeResponse;
import loginauth.like.service.PostLikeService;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/posts/{postId}/likes")
public class PostLikeController {

    private final PostLikeService postLikeService;

    public PostLikeController(PostLikeService postLikeService) {
        this.postLikeService = postLikeService;
    }

    @GetMapping
    public PostLikeResponse status(
            @PathVariable Long postId,
            Authentication authentication
    ) {
        return postLikeService.status(
                postId,
                authentication.getName()
        );
    }

    @PostMapping
    public PostLikeResponse like(
            @PathVariable Long postId,
            Authentication authentication
    ) {
        return postLikeService.like(
                postId,
                authentication.getName()
        );
    }

    @DeleteMapping
    public PostLikeResponse unlike(
            @PathVariable Long postId,
            Authentication authentication
    ) {
        return postLikeService.unlike(
                postId,
                authentication.getName()
        );
    }
}
