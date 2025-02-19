```mermaid
erDiagram
    posts ||--o{ comments : "has"
    posts ||--o{ post_likes : "has"
    posts ||--o{ post_likes : "has"

    posts }|--|| users : "has"
    comments }|--|| users : "has"
    comments ||--o{ comments : "relates"
    post_likes }|--|| users : "has"

    posts {
        uuid id PK
        uuid user_id FK
        string title
        string content
        datetime created_at
        datetime updated_at
    }
    comments {
        uuid id PK
        uuid post_id FK
        uuid parent_comment_id FK
        uuid user_id FK
        string content
        datetime created_at
        datetime updated_at
    }
    post_likes {
        uuid id PK
        uuid post_id FK
        uuid user_id FK
        datetime liked_at
    }
    users {
        uuid id PK
        string username
    }