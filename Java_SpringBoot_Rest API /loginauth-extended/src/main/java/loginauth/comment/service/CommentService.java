package loginauth.comment.service;

import loginauth.comment.domain.Comment;
import loginauth.comment.dto.CommentCreateRequest;
import loginauth.comment.dto.CommentResponse;
import loginauth.comment.dto.CommentUpdateRequest;
import loginauth.comment.exception.CommentAccessDeniedException;
import loginauth.comment.exception.CommentNotFoundException;
import loginauth.comment.repository.CommentRepository;
import loginauth.post.domain.Post;
import loginauth.post.service.PostService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional(readOnly = true)
public class CommentService {

    private final CommentRepository commentRepository;
    private final PostService postService;

    public CommentService(
            CommentRepository commentRepository,
            PostService postService
    ) {
        this.commentRepository = commentRepository;
        this.postService = postService;
    }

    public List<CommentResponse> findAll(Long postId) {
        postService.findPost(postId);

        return commentRepository.findByPostIdOrderByCreatedAtAsc(postId)
                .stream()
                .map(CommentResponse::from)
                .toList();
    }

    @Transactional
    public CommentResponse create(
            Long postId,
            CommentCreateRequest request,
            String username
    ) {
        Post post = postService.findPost(postId);

        Comment comment = commentRepository.save(
                new Comment(post, username, request.content())
        );

        return CommentResponse.from(comment);
    }

    @Transactional
    public CommentResponse update(
            Long postId,
            Long commentId,
            CommentUpdateRequest request,
            String username
    ) {
        Comment comment = findComment(postId, commentId);
        verifyWriter(comment, username);
        comment.update(request.content());
        return CommentResponse.from(comment);
    }

    @Transactional
    public void delete(
            Long postId,
            Long commentId,
            String username
    ) {
        Comment comment = findComment(postId, commentId);
        verifyWriter(comment, username);
        commentRepository.delete(comment);
    }

    private Comment findComment(Long postId, Long commentId) {
        Comment comment = commentRepository.findById(commentId)
                .orElseThrow(CommentNotFoundException::new);

        if (!comment.getPost().getId().equals(postId)) {
            throw new CommentNotFoundException();
        }

        return comment;
    }

    private void verifyWriter(Comment comment, String username) {
        if (!comment.getWriter().equals(username)) {
            throw new CommentAccessDeniedException();
        }
    }
}
