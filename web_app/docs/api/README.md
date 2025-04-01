# API Documentation

## Endpoints

### 1. Session Management
#### POST /api/setup
- Creates new user session
- Initializes directory structure
- Returns session identifier

Request: None
Response:
```json
{
    "session_id": "string",
    "status": "success"
}
```

### 2. File Operations
#### POST /api/upload
- Handles file uploads
- Supports multiple formats
- Validates file integrity

Request:
- Multipart form data with file

Response:
```json
{
    "filename": "string",
    "status": "success"
}
```

### 3. Test Operations
#### POST /api/test
- Executes statistical tests
- Processes results
- Returns analysis

Request:
```json
{
    "test_indices": [int],
    "parameters": {
        "block_length": int,
        "sequence_length": int
    }
}
```

### 4. Results Management
#### POST /api/download_results
- Creates compressed results package
- Returns test results file

### 5. Entropy Analysis
#### POST /api/ent
- Calculates entropy metrics
- Returns detailed analysis
