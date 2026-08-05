package loginauth.post.repository;

import jakarta.persistence.criteria.Predicate;
import loginauth.post.domain.Post;
import loginauth.post.dto.PostSearchCondition;
import org.springframework.data.jpa.domain.Specification;

import java.util.ArrayList;
import java.util.List;

public final class PostSpecifications {

    private PostSpecifications() {
    }

    public static Specification<Post> withCondition(
            PostSearchCondition condition
    ) {
        return (root, query, builder) -> {
            List<Predicate> predicates = new ArrayList<>();

            /*
             * 작성자 완전 일치 필터
             */
            if (
                    condition.writer() != null
                            && !condition.writer().isBlank()
            ) {
                predicates.add(
                        builder.equal(
                                root.<String>get("writer"),
                                condition.writer().trim()
                        )
                );
            }

            /*
             * 검색어 필터
             *
             * Hibernate 7에서는 TEXT/CLOB로 매핑된 필드에
             * lower()를 적용하면 타입 검증 오류가 발생할 수 있습니다.
             *
             * 따라서 title, content, writer 모두 lower() 없이
             * LIKE 검색을 적용합니다.
             */
            if (
                    condition.keyword() != null
                            && !condition.keyword().isBlank()
            ) {
                String keyword =
                        "%" + condition.keyword().trim() + "%";

                String searchType =
                        condition.searchType() == null
                                || condition.searchType().isBlank()
                                ? "titleContent"
                                : condition.searchType();

                Predicate keywordPredicate = switch (searchType) {

                    case "title" -> builder.like(
                            root.<String>get("title"),
                            keyword
                    );

                    case "content" -> builder.like(
                            root.<String>get("content"),
                            keyword
                    );

                    case "writer" -> builder.like(
                            root.<String>get("writer"),
                            keyword
                    );

                    case "titleContent" -> builder.or(
                            builder.like(
                                    root.<String>get("title"),
                                    keyword
                            ),
                            builder.like(
                                    root.<String>get("content"),
                                    keyword
                            )
                    );

                    default -> builder.or(
                            builder.like(
                                    root.<String>get("title"),
                                    keyword
                            ),
                            builder.like(
                                    root.<String>get("content"),
                                    keyword
                            )
                    );
                };

                predicates.add(keywordPredicate);
            }

            return builder.and(
                    predicates.toArray(Predicate[]::new)
            );
        };
    }
}