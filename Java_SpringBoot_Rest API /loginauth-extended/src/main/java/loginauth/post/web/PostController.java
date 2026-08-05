package loginauth.post.web;

import jakarta.validation.Valid;
import loginauth.post.dto.*;
import loginauth.post.service.PostService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.net.URI;

@RestController
@RequestMapping("/api/posts")
public class PostController {

    private final PostService postService;

    public PostController(PostService postService) {
        this.postService = postService;
    }

    @GetMapping
    public PageResponse<PostResponse> findAll(
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "titleContent") String searchType,
            @RequestParam(required = false) String writer,
            @RequestParam(defaultValue = "latest") String sort,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size
    ) {
        return postService.findAll(
                new PostSearchCondition(
                        keyword,
                        searchType,
                        writer,
                        sort
                ),
                page,
                size
        );
    }

    @GetMapping("/{postId}")
    public PostResponse findOne(@PathVariable Long postId) {
        return postService.findOne(postId);
    }

    @PostMapping
    public ResponseEntity<PostResponse> create(
            @Valid @RequestBody PostCreateRequest request,
            Authentication authentication
    ) {
        PostResponse response = postService.create(
                request,
                authentication.getName()
        );

        return ResponseEntity
                .created(URI.create("/api/posts/" + response.id()))
                .body(response);
    }

    @PutMapping("/{postId}")
    public PostResponse update(
            @PathVariable Long postId,
            @Valid @RequestBody PostUpdateRequest request,
            Authentication authentication
    ) {
        return postService.update(
                postId,
                request,
                authentication.getName()
        );
    }

    @DeleteMapping("/{postId}")
    public ResponseEntity<Void> delete(
            @PathVariable Long postId,
            Authentication authentication
    ) {
        postService.delete(postId, authentication.getName());
        return ResponseEntity.noContent().build();
    }
}
