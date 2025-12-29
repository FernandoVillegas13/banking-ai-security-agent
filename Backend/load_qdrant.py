import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COLLECTION_NAME = "fraud_policies"

policies = [
    {
        "policy_id": "FP-01",
        "rule": "Monto > 3x promedio habitual y horario fuera de rango → CHALLENGE",
        "version": "2025.1"
    },
    {
        "policy_id": "FP-02",
        "rule": "Transacción internacional y dispositivo nuevo → ESCALATE_TO_HUMAN",
        "version": "2025.1"
    }
]

def get_embedding(text: str) -> list[float]:
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding

def main():
    qdrant = QdrantClient(url=QDRANT_URL)
    
    collections = qdrant.get_collections().collections
    if COLLECTION_NAME in [c.name for c in collections]:
        print(f"Deleting existing collection: {COLLECTION_NAME}")
        qdrant.delete_collection(COLLECTION_NAME)
    
    print(f"Creating collection: {COLLECTION_NAME}")
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
    )
    
    points = []
    for idx, policy in enumerate(policies, start=1):
        text = f"Policy {policy['policy_id']}: {policy['rule']}"
        print(f"Generating embedding for chunk {idx}: {policy['policy_id']}")
        
        embedding = get_embedding(text)
        
        point = PointStruct(
            id=idx,
            vector=embedding,
            payload={
                "chunk_id": str(idx),
                "policy_id": policy["policy_id"],
                "rule": policy["rule"],
                "version": policy["version"],
                "text": text
            }
        )
        points.append(point)
    
    print(f"Uploading {len(points)} points to Qdrant...")
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    
    print("\nVerifying upload...")
    collection_info = qdrant.get_collection(COLLECTION_NAME)
    print(f"Collection points count: {collection_info.points_count}")
    
    scroll_result = qdrant.scroll(
        collection_name=COLLECTION_NAME,
        limit=10
    )
    
    print("\nStored policies:")
    for point in scroll_result[0]:
        print(f"  - ID: {point.id}, Policy: {point.payload['policy_id']}, Rule: {point.payload['rule'][:50]}...")
    
    print("\nUpload completed successfully!")

if __name__ == "__main__":
    main()
