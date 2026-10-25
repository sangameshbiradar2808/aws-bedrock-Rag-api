# AWS Bedrock RAG API — Terraform + Python

A small, portfolio-ready Retrieval-Augmented Generation (RAG) project on AWS. Upload documents to Amazon S3, create embeddings with Amazon Bedrock Titan Embeddings, retrieve relevant chunks, and answer questions with a Bedrock foundation model through AWS Lambda + API Gateway. Logs go to Amazon CloudWatch and infrastructure is managed with Terraform.

## Architecture

`Local documents → S3 documents bucket → scripts/ingest.py → Bedrock Titan embeddings → S3 vector index`

`Client → API Gateway (HTTP API) → Python Lambda → query embedding → cosine-similarity retrieval → Bedrock text generation → JSON response`

CloudWatch Logs captures Lambda execution logs. Terraform provisions the S3 bucket, Lambda, API Gateway, IAM role/policies, and log group.

## Tech stack / GitHub keywords

**AWS, Amazon Web Services, Amazon Bedrock, Amazon S3, AWS Lambda, Amazon API Gateway, Amazon CloudWatch, Terraform, Infrastructure as Code (IaC), Python, boto3, RAG, Retrieval-Augmented Generation, Generative AI, LLM, foundation models, embeddings, vector search, semantic search, cosine similarity, prompt engineering, serverless, REST API, IAM, least privilege, cloud automation, DevOps, CI/CD-ready, observability, logging, JSON API, NLP.**

## Prerequisites

- AWS account and configured credentials (`aws configure` or an AWS profile)
- Terraform 1.5+
- Python 3.11+
- Bedrock model access enabled in your AWS region for:
  - `amazon.titan-embed-text-v2:0`
  - `anthropic.claude-3-haiku-20240307-v1:0` (or change `GENERATION_MODEL_ID` to a model enabled for your account)
- Choose a region where both selected Bedrock models are available.

> Costs: this project can incur charges for Lambda, API Gateway, S3, CloudWatch, and Bedrock inference. Delete resources when finished.

## Repository layout

```text
aws-bedrock-rag-terraform/
├── README.md
├── .gitignore
├── requirements.txt
├── docs/
│   └── sample-company-handbook.txt
├── scripts/
│   └── ingest.py
├── lambda/
│   └── app.py
└── terraform/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    └── terraform.tfvars.example
```

## 1. Deploy infrastructure

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit region and optionally project_name.
terraform init
terraform validate
terraform plan
terraform apply
```

Save the outputs `documents_bucket`, `api_url`, and `lambda_name`. Keep `terraform.tfvars` private if you add secrets (this project does not require any).

## 2. Upload source documents to S3

From the repository root, set the bucket name returned by Terraform:

```bash
export RAG_BUCKET="paste-documents_bucket-output-here"
aws s3 cp docs/sample-company-handbook.txt "s3://${RAG_BUCKET}/documents/sample-company-handbook.txt"
```

Upload additional `.txt` or `.md` files under the `documents/` prefix.

## 3. Build the embedding index

Install dependencies and run the ingestion script from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
export AWS_REGION="ap-south-1"  # use the same region as Terraform
export RAG_BUCKET="your-bucket-name"
python scripts/ingest.py
```

The script reads `.txt` and `.md` documents from `s3://BUCKET/documents/`, splits them into chunks, creates Titan embeddings, and writes `index/vector-index.json` to the same bucket. Re-run ingestion after adding or changing documents.

## 4. Ask a question through API Gateway

Use the `api_url` output:

```bash
curl -X POST "PASTE_API_URL_HERE/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I request access to a company laptop?"}'
```

Example response:

```json
{
  "answer": "According to the handbook, submit an access request to the IT service desk...",
  "sources": ["sample-company-handbook.txt"]
}
```

The API route is `POST /ask`. Lambda returns a JSON response and writes request/error details to CloudWatch. Avoid sending confidential documents or sensitive personal data to a demo system.

## 5. View logs

```bash
aws logs tail "/aws/lambda/$(cd terraform && terraform output -raw lambda_name)" --follow
```

Or open **AWS Console → CloudWatch → Log groups** and select the Lambda log group.

## 6. Test / troubleshoot

- `AccessDeniedException` from Bedrock: confirm model access is enabled and the Lambda execution role has `bedrock:InvokeModel`.
- `No indexed documents`: check that documents are in the `documents/` prefix and re-run `scripts/ingest.py`.
- `Model not found`: set `generation_model_id` in `terraform/terraform.tfvars` to a text-generation model ID enabled in your region.
- API `500`: inspect the Lambda CloudWatch log stream.
- `terraform destroy` removes infrastructure and the bucket's objects must be deleted first if the bucket is not empty. This template sets `force_destroy = true`, so use it only for a demo bucket.

## Security notes

- The API is intentionally unauthenticated for a simple demo. Add IAM/JWT/Cognito authorization, throttling, and request validation before production use.
- The Lambda role is scoped to the project's bucket and selected model invocation.
- S3 public access is blocked and bucket encryption is enabled.
- Do not commit AWS credentials, state files, `terraform.tfvars`, or real private documents.

## Suggested GitHub repository

**Repository name:** `aws-bedrock-rag-terraform`

**Description:** `Serverless Retrieval-Augmented Generation (RAG) API on AWS using Amazon Bedrock embeddings, S3 document storage, Python Lambda, API Gateway, CloudWatch, and Terraform IaC.`

**Topics:** `aws`, `amazon-bedrock`, `rag`, `generative-ai`, `python`, `lambda`, `api-gateway`, `s3`, `cloudwatch`, `terraform`, `iac`, `serverless`, `embeddings`, `vector-search`, `devops`
