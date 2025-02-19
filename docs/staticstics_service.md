```mermaid
erDiagram
    post_statistics ||--o{ comment_statistics : "related"
    post_statistics ||--o{ like_statistics : "related"
    comment_statistics ||--o{ comment_statistics : "relates"

    post_statistics {
        uuid id PK
        uuid post_id FK
        int views_count
        int likes_count
        int comments_count
        string username
        datetime created_at
        datetime updated_at
    }
    comment_statistics {
        uuid id PK
        uuid post_id FK
        uuid parent_comment_id FK
        uuid user_id FK
        string username
        int reply_count
        datetime created_at
        datetime updated_at
    }
    like_statistics {
        uuid id PK
        uuid post_id FK
        uuid user_id FK
        string username
        datetime liked_at
    }