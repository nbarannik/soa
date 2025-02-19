```mermaid
erDiagram
    users ||--o{ user_roles : "has"
    users ||--o{ user_roles : "has"
    users ||--o{ user_sessions : "creates"
    users }o--o{ user_subscriptions : "relates"
    users {
        uuid id PK
        string username
        string email
        string password_hash
        datetime created_at
        datetime updated_at
    }
    user_roles {
        uuid id PK
        uuid user_id FK
        string role
    }
    user_subscriptions {
        uuid id PK
        uuid user_id FK
        uuid subscribed_to_id FK
    }
    user_sessions {
        uuid id PK
        uuid user_id FK
        string session_token
        string user_agent
        datetime created_at
        datetime expires_at
        string ip_address
    }