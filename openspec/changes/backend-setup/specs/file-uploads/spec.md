## ADDED Requirements

### Requirement: Upload file in chat
The system SHALL allow users to attach files to chat messages.

#### Scenario: Image upload
- **WHEN** user attaches image to message
- **THEN** system uploads file and stores reference in message

#### Scenario: Document upload
- **WHEN** user attaches document to message
- **THEN** system uploads file and stores reference in message

### Requirement: File validation
The system SHALL validate uploaded files.

#### Scenario: File type validation
- **WHEN** user uploads unsupported file type
- **THEN** system rejects upload with error message

#### Scenario: File size validation
- **WHEN** user uploads file exceeding size limit
- **THEN** system rejects upload with error message

### Requirement: File access control
The system SHALL restrict file access to authorized users.

#### Scenario: Owner access
- **WHEN** file owner requests their file
- **THEN** system serves the file

#### Scenario: Unauthorized access
- **WHEN** non-owner requests file
- **THEN** system returns 403 Forbidden
