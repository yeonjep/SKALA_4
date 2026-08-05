CREATE TABLE IF NOT EXISTS users
(
    id          BIGINT NOT NULL AUTO_INCREMENT,
    username    VARCHAR(50) NOT NULL,
    password    VARCHAR(100) NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uk_users_username (username)
);

CREATE TABLE IF NOT EXISTS posts
(
    id          BIGINT NOT NULL AUTO_INCREMENT,
    title       VARCHAR(200) NOT NULL,
    content     TEXT NOT NULL,
    writer      VARCHAR(50) NOT NULL,
    view_count  BIGINT NOT NULL DEFAULT 0,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_posts_writer (writer),
    INDEX idx_posts_created_at (created_at),
    INDEX idx_posts_view_count (view_count)
);

CREATE TABLE IF NOT EXISTS comments
(
    id          BIGINT NOT NULL AUTO_INCREMENT,
    post_id     BIGINT NOT NULL,
    writer      VARCHAR(50) NOT NULL,
    content     TEXT NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_comments_post_id (post_id),
    INDEX idx_comments_writer (writer),

    CONSTRAINT fk_comments_post
        FOREIGN KEY (post_id)
        REFERENCES posts (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS post_likes
(
    id          BIGINT NOT NULL AUTO_INCREMENT,
    post_id     BIGINT NOT NULL,
    username    VARCHAR(50) NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uk_post_likes_post_username (post_id, username),
    INDEX idx_post_likes_post_id (post_id),
    INDEX idx_post_likes_username (username),

    CONSTRAINT fk_post_likes_post
        FOREIGN KEY (post_id)
        REFERENCES posts (id)
        ON DELETE CASCADE
);
