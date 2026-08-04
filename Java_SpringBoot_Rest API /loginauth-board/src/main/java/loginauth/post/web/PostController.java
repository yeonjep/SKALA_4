package loginauth.post.web;

import jakarta.validation.Valid;
import loginauth.post.dto.PostCreateRequest;
import loginauth.post.dto.PostResponse;
import loginauth.post.dto.PostUpdateRequest;
import loginauth.post.service.PostService;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/posts")
public class PostController {

    private final PostService postService;

    public PostController(PostService postService) {
        this.postService = postService;
    }

    @GetMapping
    public List<PostResponse> findAll() {
        return postService.findAll();
    }

    @GetMapping("/{postId}")
    public PostResponse findById(@PathVariable Long postId) {
        return postService.findById(postId);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public PostResponse create(
            @Valid @RequestBody PostCreateRequest request,
            Authentication authentication
    ) {
        return postService.create(request, authentication.getName());
    }

    @PutMapping("/{postId}")
    public PostResponse update(
            @PathVariable Long postId,
            @Valid @RequestBody PostUpdateRequest request,
            Authentication authentication
    ) {
        return postService.update(postId, request, authentication.getName());
    }

    @DeleteMapping("/{postId}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(
            @PathVariable Long postId,
            Authentication authentication
    ) {
        postService.delete(postId, authentication.getName());
    }
}
