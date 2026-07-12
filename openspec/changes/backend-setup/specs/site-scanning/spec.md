## ADDED Requirements

### Requirement: Initiate site scan
The system SHALL allow users to request a scan of a suspicious URL.

#### Scenario: Scan request
- **WHEN** user submits URL for scanning
- **THEN** system creates scan job and returns scan ID

#### Scenario: Edge Function invocation
- **WHEN** scan is initiated
- **THEN** system invokes site-scanning Edge Function with scan ID and URL

### Requirement: Scan execution
The system SHALL execute site scanning via Edge Function.

#### Scenario: Edge Function starts
- **WHEN** Edge Function receives scan request
- **THEN** function sets scan status to "processing"

#### Scenario: Gambling site detection
- **WHEN** scan analyzes gambling-related content
- **THEN** function identifies and categorizes as gambling

#### Scenario: Scam site detection
- **WHEN** scan detects scam indicators
- **THEN** function identifies and categorizes as scam

#### Scenario: Illegal lending detection
- **WHEN** scan finds illegal lending/BNPL patterns
- **THEN** function identifies and categorizes as illegal lending

#### Scenario: Edge Function failure
- **WHEN** Edge Function encounters error during scan
- **THEN** function sets scan status to "failed" with error message

### Requirement: Scan result storage
The system SHALL store and return scan results.

#### Scenario: Complete scan
- **WHEN** scan finishes processing in Edge Function
- **THEN** function stores result with risk score, categories, and evidence URLs

#### Scenario: Retrieve scan result
- **WHEN** user requests scan result by ID
- **THEN** system returns full result with categories and evidence

### Requirement: Scan status tracking
The system SHALL provide real-time scan progress.

#### Scenario: Scan in progress
- **WHEN** scan is processing in Edge Function
- **THEN** system shows progress status to user

#### Scenario: Scan completion
- **WHEN** Edge Function completes scan
- **THEN** system notifies user with result summary

### Requirement: Edge Function management
The system SHALL support Edge Function deployment and monitoring.

#### Scenario: Deploy Edge Function
- **WHEN** developer deploys site-scanning function
- **THEN** Supabase deploys function to edge runtime

#### Scenario: Function logs
- **WHEN** Edge Function executes
- **THEN** system logs execution details for debugging
