package loginauth.comment.web;

import jakarta.validation.Valid;
import loginauth.comment.dto.CommentCreateRequest;
import loginauth.comment.dto.CommentResponse;
import loginauth.comment.dto.CommentUpdateRequest;
import loginauth.comment.service.CommentService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.net.URI;
import java.util.List;

@RestController
@RequestMapping("/api/posts/{postId}/comments")
public class CommentController {

    private final CommentService commentService;

    public CommentController(CommentService commentService) {
        this.commentService = commentService;
    }

    @GetMapping
    public List<CommentResponse> findAll(@PathVariable Long postId) {
        return commentService.findAll(postId);
    }

    @PostMapping
    public ResponseEntity<CommentResponse> create(
            @PathVariable Long postId,
            @Valid @RequestBody CommentCreateRequest request,
            Authentication authentication
    ) {
        CommentResponse response = commentService.create(
                postId,
                request,
                authentication.getName()
        );

        return ResponseEntity
                .created(
                        URI.create(
                                "/api/posts/" + postId
                                        + "/comments/" + response.id()
                        )
                )
                .body(response);
    }

    @PutMapping("/{commentId}")
    public CommentResponse update(
            @PathVariable Long postId,
            @PathVariable Long commentId,
            @Valid @RequestBody CommentUpdateRequest request,
            Authentication authentication
    ) {
        return commentService.update(
                postId,
                commentId,
                request,
                authentication.getName()
        );
    }

    @DeleteMapping("/{commentId}")
    public ResponseEntity<Void> delete(
            @PathVariable Long postId,
            @PathVariable Long commentId,
            Authentication authentication
    ) {
        commentService.delete(
                postId,
                commentId,
                authentication.getName()
        );

        return ResponseEntity.noContent().build();
    }
}
