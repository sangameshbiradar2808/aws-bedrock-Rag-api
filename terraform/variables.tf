variable "aws_region" {
  description = "AWS region where Bedrock models are enabled."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Prefix for resources; use lowercase letters, numbers, and hyphens."
  type        = string
  default     = "bedrock-rag-demo"
}

variable "embedding_model_id" {
  type    = string
  default = "amazon.titan-embed-text-v2:0"
}

variable "generation_model_id" {
  description = "Bedrock text-generation model ID enabled for your account and region."
  type        = string
  default     = "anthropic.claude-3-haiku-20240307-v1:0"
}
