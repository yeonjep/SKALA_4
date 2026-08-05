package loginauth.like.domain;

import jakarta.persistence.*;
import loginauth.post.domain.Post;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "post_likes",
        uniqueConstraints = @UniqueConstraint(
                name = "uk_post_likes_post_username",
                columnNames = {"post_id", "username"}
        )
)
public class PostLike {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "post_id", nullable = false)
    private Post post;

    @Column(nullable = false, length = 50)
    private String username;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    protected PostLike() {
    }

    public PostLike(Post post, String username) {
        this.post = post;
        this.username = username;
        this.createdAt = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public Post getPost() { return post; }
    public String getUsername() { return username; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}
