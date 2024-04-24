docker pull localstack/localstack:s3-latest && \
docker run \
  --rm \
  -p 4566:4566 \
  localstack/localstack:s3-latest