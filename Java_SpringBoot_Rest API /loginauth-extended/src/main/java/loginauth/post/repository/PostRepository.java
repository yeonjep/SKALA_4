package loginauth.post.repository;

import loginauth.post.domain.Post;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface PostRepository extends
        JpaRepository<Post, Long>,
        JpaSpecificationExecutor<Post> {
}
