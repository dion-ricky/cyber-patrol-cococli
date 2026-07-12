## ADDED Requirements

### Requirement: Initiate site scan
The system SHALL allow users to request a scan of a suspicious URL.

#### Scenario: Scan request
- **WHEN** user submits URL for scanning
- **THEN** system creates scan job and returns scan ID

### Requirement: Scan execution
The system SHALL scan sites for malicious content categories.

#### Scenario: Gambling site detection
- **WHEN** scan analyzes gambling-related content
- **THEN** system identifies and categorizes as gambling

#### Scenario: Scam site detection
- **WHEN** scan detects scam indicators
- **THEN** system identifies and categorizes as scam

#### Scenario: Illegal lending detection
- **WHEN** scan finds illegal lending/BNPL patterns
- **THEN** system identifies and categorizes as illegal lending

### Requirement: Scan result storage
The system SHALL store and return scan results.

#### Scenario: Complete scan
- **WHEN** scan finishes processing
- **THEN** system stores result with risk score, categories, and evidence URLs

#### Scenario: Retrieve scan result
- **WHEN** user requests scan result by ID
- **THEN** system returns full result with categories and evidence

### Requirement: Scan status tracking
The system SHALL provide real-time scan progress.

#### Scenario: Scan in progress
- **WHEN** scan is processing
- **THEN** system shows progress status to user

#### Scenario: Scan completion
- **WHEN** scan completes
- **THEN** system notifies user with result summary
