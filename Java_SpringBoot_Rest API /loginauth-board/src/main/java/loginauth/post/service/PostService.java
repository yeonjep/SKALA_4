package loginauth.post.service;

import loginauth.post.domain.Post;
import loginauth.post.dto.PostCreateRequest;
import loginauth.post.dto.PostResponse;
import loginauth.post.dto.PostUpdateRequest;
import loginauth.post.exception.PostAccessDeniedException;
import loginauth.post.exception.PostNotFoundException;
import loginauth.post.repository.PostRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional(readOnly = true)
public class PostService {

    private final PostRepository postRepository;

    public PostService(PostRepository postRepository) {
        this.postRepository = postRepository;
    }

    public List<PostResponse> findAll() {
        return postRepository.findAllByOrderByIdDesc()
                .stream()
                .map(PostResponse::from)
                .toList();
    }

    public PostResponse findById(Long postId) {
        return PostResponse.from(findPost(postId));
    }

    @Transactional
    public PostResponse create(PostCreateRequest request, String username) {
        Post post = new Post(request.title(), request.content(), username);
        return PostResponse.from(postRepository.save(post));
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
        return PostResponse.from(post);
    }

    @Transactional
    public void delete(Long postId, String username) {
        Post post = findPost(postId);
        verifyWriter(post, username);
        postRepository.delete(post);
    }

    private Post findPost(Long postId) {
        return postRepository.findById(postId)
                .orElseThrow(() -> new PostNotFoundException(postId));
    }

    private void verifyWriter(Post post, String username) {
        if (!post.getWriter().equals(username)) {
            throw new PostAccessDeniedException();
        }
    }
}
