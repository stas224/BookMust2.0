docker pull localstack/localstack:s3-latest && \
docker run \
  --rm -d \
  -p 4566:4566 \
  localstack/localstack:s3-latest \ &&
python s3-init.py
