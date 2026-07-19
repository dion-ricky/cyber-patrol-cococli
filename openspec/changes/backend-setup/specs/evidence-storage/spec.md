## ADDED Requirements

### Requirement: Store scan evidence
The system SHALL store evidence captured during site scans.

#### Scenario: Store screenshot
- **WHEN** scan captures screenshot
- **THEN** system uploads to storage bucket and records URL

#### Scenario: Store video recording
- **WHEN** scan captures video
- **THEN** system uploads to storage bucket and records URL

### Requirement: Retrieve evidence
The system SHALL allow users to access scan evidence.

#### Scenario: View evidence list
- **WHEN** user views scan result
- **THEN** system returns list of evidence files with URLs

#### Scenario: Download evidence
- **WHEN** user downloads evidence file
- **THEN** system serves file from storage bucket

### Requirement: Evidence metadata
The system SHALL track evidence file metadata.

#### Scenario: Record evidence metadata
- **WHEN** evidence file is stored
- **THEN** system records file size, type, capture timestamp

### Requirement: Storage bucket management
The system SHALL organize evidence in storage buckets.

#### Scenario: Bucket structure
- **WHEN** evidence is stored
- **THEN** system organizes by scan ID and evidence type
