package loginauth.post.service;

import loginauth.comment.repository.CommentRepository;
import loginauth.like.repository.PostLikeRepository;
import loginauth.post.domain.Post;
import loginauth.post.dto.*;
import loginauth.post.exception.PostAccessDeniedException;
import loginauth.post.exception.PostNotFoundException;
import loginauth.post.repository.PostRepository;
import loginauth.post.repository.PostSpecifications;
import org.springframework.data.domain.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class PostService {

    private final PostRepository postRepository;
    private final CommentRepository commentRepository;
    private final PostLikeRepository postLikeRepository;

    public PostService(
            PostRepository postRepository,
            CommentRepository commentRepository,
            PostLikeRepository postLikeRepository
    ) {
        this.postRepository = postRepository;
        this.commentRepository = commentRepository;
        this.postLikeRepository = postLikeRepository;
    }

    public PageResponse<PostResponse> findAll(
            PostSearchCondition condition,
            int page,
            int size
    ) {
        Pageable pageable = PageRequest.of(
                Math.max(page, 0),
                Math.min(Math.max(size, 1), 100),
                resolveSort(condition.sort())
        );

        Page<PostResponse> responsePage = postRepository.findAll(
                        PostSpecifications.withCondition(condition),
                        pageable
                )
                .map(this::toResponse);

        return PageResponse.from(responsePage);
    }

    @Transactional
    public PostResponse findOne(Long postId) {
        Post post = findPost(postId);
        post.increaseViewCount();
        return toResponse(post);
    }

    @Transactional
    public PostResponse create(
            PostCreateRequest request,
            String username
    ) {
        Post post = postRepository.save(
                new Post(
                        request.title(),
                        request.content(),
                        username
                )
        );

        return toResponse(post);
    }

    @Transactional
    public PostResponse update(
            Long postId,
            PostUpdateRequest request,
            String username
    ) {
        Post post = findPost(postId);
        verifyWriter(post, username);
        post.update(request.title(), request.content());
        return toResponse(post);
    }

    @Transactional
    public void delete(Long postId, String username) {
        Post post = findPost(postId);
        verifyWriter(post, username);
        postRepository.delete(post);
    }

    public Post findPost(Long postId) {
        return postRepository.findById(postId)
                .orElseThrow(PostNotFoundException::new);
    }

    private PostResponse toResponse(Post post) {
        return PostResponse.from(
                post,
                postLikeRepository.countByPostId(post.getId()),
                commentRepository.countByPostId(post.getId())
        );
    }

    private void verifyWriter(Post post, String username) {
        if (!post.getWriter().equals(username)) {
            throw new PostAccessDeniedException();
        }
    }

    private Sort resolveSort(String sort) {
        if ("views".equalsIgnoreCase(sort)) {
            return Sort.by(
                    Sort.Order.desc("viewCount"),
                    Sort.Order.desc("createdAt")
            );
        }

        // 좋아요순은 집계 조인이 필요하므로 이 예제에서는 Service에서 지원하지 않고
        // 최신순을 기본값으로 사용합니다. 좋아요 수는 응답에 포함됩니다.
        return Sort.by(Sort.Order.desc("createdAt"));
    }
}
