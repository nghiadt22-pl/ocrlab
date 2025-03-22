#!/bin/bash
echo "Running OCR test for specific user with real documents..."

# Set environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file"
    export $(grep -v '^#' .env | xargs)
fi

# Verify environment variables are set
if [ -z "$AzureWebJobsStorage" ] || [ -z "$DOCUMENT_INTELLIGENCE_ENDPOINT" ] || [ -z "$DOCUMENT_INTELLIGENCE_API_KEY" ] || [ -z "$POSTGRES_CONNECTION_STRING" ]; then
    echo "Error: Required environment variables are not set"
    echo "Please set AzureWebJobsStorage, DOCUMENT_INTELLIGENCE_ENDPOINT, DOCUMENT_INTELLIGENCE_API_KEY, and POSTGRES_CONNECTION_STRING"
    exit 1
fi

# Run the test
python test_user_ocr.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "Test completed successfully!"
else
    echo "Test failed!"
fi 