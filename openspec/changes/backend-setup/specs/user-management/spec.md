## ADDED Requirements

### Requirement: User registration
The system SHALL allow users to register with email and password.

#### Scenario: Successful registration
- **WHEN** user submits valid email and password
- **THEN** system creates user account and sends confirmation email

#### Scenario: Duplicate email
- **WHEN** user attempts to register with existing email
- **THEN** system returns error "Email already registered"

### Requirement: User login
The system SHALL authenticate users via email and password.

#### Scenario: Email/password login
- **WHEN** user provides valid credentials
- **THEN** system returns JWT token and user profile

#### Scenario: Invalid credentials
- **WHEN** user provides wrong email or password
- **THEN** system returns error "Invalid credentials"

### Requirement: User profile management
The system SHALL allow users to view and update their profile.

#### Scenario: View profile
- **WHEN** authenticated user requests profile
- **THEN** system returns user data (name, email, avatar, created_at)

#### Scenario: Update profile
- **WHEN** user updates profile fields
- **THEN** system saves changes and returns updated profile

### Requirement: Session management
The system SHALL manage user sessions with secure tokens.

#### Scenario: Token refresh
- **WHEN** access token expires
- **THEN** system refreshes token using refresh token

#### Scenario: Logout
- **WHEN** user logs out
- **THEN** system invalidates session tokens
