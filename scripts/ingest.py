"""Create a simple JSON embedding index from text/Markdown documents in S3."""
import json
import os
import re
import boto3

REGION = os.environ.get("AWS_REGION", "ap-south-1")
BUCKET = os.environ["RAG_BUCKET"]
EMBEDDING_MODEL_ID = os.environ.get("EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0")
s3 = boto3.client("s3", region_name=REGION)
bedrock = boto3.client("bedrock-runtime", region_name=REGION)


def chunk_text(text, chunk_size=900, overlap=120):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def embed(text):
    response = bedrock.invoke_model(
        modelId=EMBEDDING_MODEL_ID,
        body=json.dumps({"inputText": text, "dimensions": 1024, "normalize": True}),
        accept="application/json",
        contentType="application/json",
    )
    return json.loads(response["body"].read())["embedding"]


def main():
    paginator = s3.get_paginator("list_objects_v2")
    rows = []
    for page in paginator.paginate(Bucket=BUCKET, Prefix="documents/"):
        for item in page.get("Contents", []):
            key = item["Key"]
            if not key.lower().endswith((".txt", ".md")):
                continue
            body = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read().decode("utf-8", errors="replace")
            for number, chunk in enumerate(chunk_text(body)):
                rows.append({
                    "source": key.removeprefix("documents/"),
                    "chunk": number,
                    "text": chunk,
                    "embedding": embed(chunk),
                })
                print(f"Embedded {key} chunk {number}")
    if not rows:
        raise SystemExit("No .txt or .md documents found under documents/. Upload a document first.")
    s3.put_object(
        Bucket=BUCKET,
        Key="index/vector-index.json",
        Body=json.dumps(rows).encode("utf-8"),
        ContentType="application/json",
    )
    print(f"Wrote {len(rows)} chunks to s3://{BUCKET}/index/vector-index.json")


if __name__ == "__main__":
    main()
