package loginauth.like.repository;

import loginauth.like.domain.PostLike;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface PostLikeRepository extends JpaRepository<PostLike, Long> {

    Optional<PostLike> findByPostIdAndUsername(
            Long postId,
            String username
    );

    boolean existsByPostIdAndUsername(
            Long postId,
            String username
    );

    long countByPostId(Long postId);
}
