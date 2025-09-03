# deploy.ps1 - PowerShell deployment script for Windows

Write-Host "🚀 Deploying ADK RAG API to Cloud Run..." -ForegroundColor Green

# Deploy to Cloud Run with environment variables
gcloud run deploy adk-rag-api `
  --source . `
  --region us-central1 `
  --allow-unauthenticated `
  --memory 2Gi `
  --timeout 600 `
  --cpu 2 `
  --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=ai-adk-rag-faq,GOOGLE_CLOUD_LOCATION=eu" `
  --project=ai-adk-rag-faq

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Test endpoints:" -ForegroundColor Yellow
Write-Host "  Health: https://adk-rag-api-851160410617.us-central1.run.app/"
Write-Host "  Test: https://adk-rag-api-851160410617.us-central1.run.app/test-agent"
Write-Host "  Query: POST https://adk-rag-api-851160410617.us-central1.run.app/query"
Write-Host ""
Write-Host "📝 Test command:" -ForegroundColor Yellow
Write-Host "curl -X POST https://adk-rag-api-851160410617.us-central1.run.app/query -H 'Content-Type: application/json' -d '{`"question`": `"Tell me about clothing trends`"}'"