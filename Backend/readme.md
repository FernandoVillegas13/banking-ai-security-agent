docker build -t deepfeeltest_api .

docker-compose up -d --build# banking-ai-security-agent

docker build -t banking-agent:dev .
docker run -it --rm -v "$PWD":/app -p 8000:8000 banking-agent:dev
docker-compose exec api python3 load_qdrant.py