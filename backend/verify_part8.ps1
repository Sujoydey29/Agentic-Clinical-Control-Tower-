# Verify Part 8 (Evaluation & Safety)

# 1. Run Agent Workflow to generate data
Write-Host "Running Agent Workflow..."
$body = @{ trigger_type = "auto"; target_role = "nurse" } | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/agents/run" -Method Post -Body $body -ContentType "application/json"
$workflow_id = $response.workflow_id
Write-Host "Workflow ID: $workflow_id"
Write-Host "Status: $($response.status)"

# 2. Check Metrics (should have auto-logged)
Write-Host "`nChecking Initial Metrics..."
$metrics = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/evaluation/metrics" -Method Get
Write-Host ($metrics | ConvertTo-Json -Depth 3)

# 3. Submit Feedback
Write-Host "`nSubmitting Feedback..."
$feedback = @{
    workflow_id = $workflow_id
    feedback_type = "thumbs_up"
    comments = "Great plan, very safe."
    user_role = "doctor"
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/evaluation/feedback" -Method Post -Body $feedback -ContentType "application/json"

# 4. Check Metrics again (should update)
Write-Host "`nChecking Updated Metrics..."
$metrics = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/evaluation/metrics" -Method Get
Write-Host ($metrics | ConvertTo-Json -Depth 3)

# 5. Check Audit Trail
Write-Host "`nChecking Audit Trail..."
$audit = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/evaluation/audit/$workflow_id" -Method Get
Write-Host ($audit | ConvertTo-Json -Depth 3)
