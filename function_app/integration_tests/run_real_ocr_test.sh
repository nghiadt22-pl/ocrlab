#!/bin/bash
echo "Running real OCR test with Azure Document Intelligence..."

# Set environment variables for the test
# Replace with your actual connection string for Azure Storage
export AzureWebJobsStorage="your_storage_connection_string_here"

# Run the test
python test_real_ocr.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "Test completed successfully!"
else
    echo "Test failed!"
fi 