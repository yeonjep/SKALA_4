package loginauth.like.service;

import loginauth.like.domain.PostLike;
import loginauth.like.dto.PostLikeResponse;
import loginauth.like.exception.DuplicatePostLikeException;
import loginauth.like.repository.PostLikeRepository;
import loginauth.post.domain.Post;
import loginauth.post.service.PostService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class PostLikeService {

    private final PostLikeRepository postLikeRepository;
    private final PostService postService;

    public PostLikeService(
            PostLikeRepository postLikeRepository,
            PostService postService
    ) {
        this.postLikeRepository = postLikeRepository;
        this.postService = postService;
    }

    public PostLikeResponse status(Long postId, String username) {
        postService.findPost(postId);

        return new PostLikeResponse(
                postId,
                postLikeRepository.existsByPostIdAndUsername(
                        postId,
                        username
                ),
                postLikeRepository.countByPostId(postId)
        );
    }

    @Transactional
    public PostLikeResponse like(Long postId, String username) {
        if (postLikeRepository.existsByPostIdAndUsername(
                postId,
                username
        )) {
            throw new DuplicatePostLikeException();
        }

        Post post = postService.findPost(postId);
        postLikeRepository.save(new PostLike(post, username));

        return new PostLikeResponse(
                postId,
                true,
                postLikeRepository.countByPostId(postId)
        );
    }

    @Transactional
    public PostLikeResponse unlike(Long postId, String username) {
        PostLike postLike = postLikeRepository
                .findByPostIdAndUsername(postId, username)
                .orElse(null);

        if (postLike != null) {
            postLikeRepository.delete(postLike);
        }

        return new PostLikeResponse(
                postId,
                false,
                postLikeRepository.countByPostId(postId)
        );
    }
}
