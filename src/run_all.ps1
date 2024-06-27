# Start the master app
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "master_app/master_app.py"

# Start the summarization app
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "summarization_app/summarization_app.py"

# Start the table extraction app
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "table_extraction_app/table_extraction_app.py"

# Wait a few seconds to ensure the apps are up and running
Start-Sleep -Seconds 5

# Open the master app in the default web browser
Start-Process "http://localhost:8085"
