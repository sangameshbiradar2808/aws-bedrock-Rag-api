output "documents_bucket" {
  description = "S3 bucket for documents and embedding index."
  value       = aws_s3_bucket.documents.bucket
}

output "api_url" {
  description = "Base URL for the HTTP API; append /ask."
  value       = aws_apigatewayv2_api.http.api_endpoint
}

output "lambda_name" {
  value = aws_lambda_function.rag.function_name
}
