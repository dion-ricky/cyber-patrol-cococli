-- Semantic View for Cyber Patrol scan data
-- Enables Cortex Analyst to answer natural-language questions about site scans

CREATE OR REPLACE SEMANTIC VIEW CYBERPATROL.RAW.CYBER_PATROL_ANALYSIS
  TABLES (
    CYBERPATROL.RAW.SCAN_REQUESTS AS requests
      PRIMARY KEY (REQUEST_ID)
      WITH COLUMNS (
        REQUEST_ID
          AS 'Unique scan request identifier',
        STATUS
          AS 'Status of the scan request (e.g. done, pending, failed)',
        ERROR
          AS 'Error message if the scan failed',
        CREATED_AT
          AS 'When the scan was requested',
        UPDATED_AT
          AS 'When the scan request was last updated'
      ),

    CYBERPATROL.RAW.SCAN_RESULTS AS results
      PRIMARY KEY (ID_SCRAP)
      WITH COLUMNS (
        ID_SCRAP
          AS 'Unique scan result identifier',
        REQUEST_ID
          AS 'Foreign key to scan_requests',
        CRAWLED_TIME
          AS 'When the website was crawled/visited',
        WEBSITE
          AS 'Domain name or shortlink service of the scanned site',
        CLASSIFY_WEBSITE
          AS 'Classification of the website: GAMBLING_WEBSITE, SCAM_WEBSITE, or UNCLASSIFIED',
        CREATED_AT
          AS 'When the scan result was recorded'
      ),

    CYBERPATROL.RAW.URLSCAN_RESULTS AS urlscan
      PRIMARY KEY (ID)
      WITH COLUMNS (
        ID
          AS 'Unique urlscan result identifier',
        REQUEST_ID
          AS 'Foreign key to scan_requests',
        UUID
          AS 'UUID from the urlscan.io service',
        VERDICTS
          AS 'JSON verdict data including maliciousness scores from community, engines, and urlscan',
        PAGE
          AS 'JSON page metadata including domain, IP, ASN, country, TLS info, and page title',
        LISTS
          AS 'JSON lists data from urlscan',
        STATS
          AS 'JSON statistics about the page load',
        CREATED_AT
          AS 'When the urlscan result was recorded'
      )
  )

  RELATIONSHIPS (
    results (REQUEST_ID) REFERENCES requests (REQUEST_ID)
      AS 'Each scan result belongs to one scan request',
    urlscan (REQUEST_ID) REFERENCES requests (REQUEST_ID)
      AS 'Each urlscan result belongs to one scan request'
  )

  METRICS (
    total_scans AS COUNT(results.ID_SCRAP)
      AS 'Total number of site scans performed',
    gambling_sites AS COUNT_IF(results.CLASSIFY_WEBSITE = 'GAMBLING_WEBSITE')
      AS 'Number of sites classified as gambling',
    scam_sites AS COUNT_IF(results.CLASSIFY_WEBSITE = 'SCAM_WEBSITE')
      AS 'Number of sites classified as scam',
    unclassified_sites AS COUNT_IF(results.CLASSIFY_WEBSITE = 'UNCLASSIFIED')
      AS 'Number of sites with no malicious indicators',
    avg_scan_duration_seconds AS AVG(DATEDIFF('second', requests.CREATED_AT, requests.UPDATED_AT))
      AS 'Average time in seconds from scan request to completion',
    avg_malicious_score AS AVG(urlscan.VERDICTS:engines:score::FLOAT)
      AS 'Average maliciousness score from urlscan engines (0-100, higher = more suspicious)'
  )

  FILTERS (
    gambling_only AS results.CLASSIFY_WEBSITE = 'GAMBLING_WEBSITE'
      AS 'Filter to only gambling websites',
    scam_only AS results.CLASSIFY_WEBSITE = 'SCAM_WEBSITE'
      AS 'Filter to only scam/phishing websites',
    malicious_only AS results.CLASSIFY_WEBSITE != 'UNCLASSIFIED'
      AS 'Filter to all malicious websites (gambling + scam)',
    high_threat_score AS urlscan.VERDICTS:engines:score::FLOAT > 50
      AS 'Filter to sites with engine threat score above 50'
  )

  COMMENT = 'Cyber Patrol scan analysis: website classifications, threat scores, and scan performance metrics'

  AI_VERIFIED_QUERIES (
    classification_breakdown AS (
      QUESTION 'How many sites are in each classification category?'
      VERIFIED_AT 1753948800
      ONBOARDING_QUESTION TRUE
      VERIFIED_BY '(STEWARD = cyber_patrol_team)'
      SQL 'SELECT results.CLASSIFY_WEBSITE AS classification, COUNT(*) AS site_count FROM CYBERPATROL.RAW.SCAN_RESULTS AS results GROUP BY results.CLASSIFY_WEBSITE ORDER BY site_count DESC'
    ),
    recent_gambling_sites AS (
      QUESTION 'What are the most recent gambling sites detected?'
      VERIFIED_AT 1753948800
      ONBOARDING_QUESTION TRUE
      VERIFIED_BY '(STEWARD = cyber_patrol_team)'
      SQL 'SELECT results.WEBSITE, results.CRAWLED_TIME, urlscan.PAGE:title::VARCHAR AS page_title, urlscan.PAGE:domain::VARCHAR AS actual_domain FROM CYBERPATROL.RAW.SCAN_RESULTS AS results LEFT JOIN CYBERPATROL.RAW.URLSCAN_RESULTS AS urlscan ON results.REQUEST_ID = urlscan.REQUEST_ID WHERE results.CLASSIFY_WEBSITE = ''GAMBLING_WEBSITE'' ORDER BY results.CRAWLED_TIME DESC'
    ),
    threat_scores_summary AS (
      QUESTION 'What is the average threat score by classification?'
      VERIFIED_AT 1753948800
      ONBOARDING_QUESTION FALSE
      VERIFIED_BY '(STEWARD = cyber_patrol_team)'
      SQL 'SELECT results.CLASSIFY_WEBSITE AS classification, AVG(urlscan.VERDICTS:engines:score::FLOAT) AS avg_threat_score, COUNT(*) AS site_count FROM CYBERPATROL.RAW.SCAN_RESULTS AS results LEFT JOIN CYBERPATROL.RAW.URLSCAN_RESULTS AS urlscan ON results.REQUEST_ID = urlscan.REQUEST_ID GROUP BY results.CLASSIFY_WEBSITE ORDER BY avg_threat_score DESC NULLS LAST'
    )
  );
