"""Test script to populate the pipeline with sample data."""

import sys
import os
import json
from pathlib import Path

# Load environment variables from .env
from pathlib import Path
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import Pipeline
from samples.sample_data import get_samples


def test_pipeline():
    """Test the pipeline with sample documents."""
    print("🚀 Testing Akhila AI Pipeline\n")
    print("=" * 60)
    
    # Initialize pipeline
    print("\n1. Initializing pipeline...")
    pipeline = Pipeline(
        db_path="data/pipeline.db",
        ai_provider=os.getenv("AI_PROVIDER", "openai"),
        ai_model=os.getenv("AI_MODEL", None)
    )
    print("✓ Pipeline initialized")
    
    # Get samples
    samples = get_samples()
    print(f"\n2. Processing {len(samples)} sample documents...")
    
    results = []
    for i, sample in enumerate(samples, 1):
        print(f"\n   Document {i}/{len(samples)}: {sample['source']}")
        print(f"   Text preview: {sample['text'][:100].strip()}...")
        
        result = pipeline.ingest(sample['text'], sample['source'])
        
        if result['status'] == 'success':
            print(f"   ✓ Processed successfully (ID: {result['document_id']})")
            print(f"   Sentiment: {result['analysis']['sentiment']} "
                  f"(confidence: {result['analysis']['sentiment_confidence']:.2f})")
            print(f"   Topics: {', '.join(result['analysis']['topics'])}")
            print(f"   Entities: {len(result['analysis']['entities'])} found")
            results.append(result)
        else:
            print(f"   ✗ Error: {result['message']}")
    
    # Display statistics
    print("\n" + "=" * 60)
    print("\n3. System Statistics:")
    stats = pipeline.stats()
    print(f"   Total documents: {stats['stats']['total_documents']}")
    print(f"   Sentiment breakdown:")
    for sentiment, count in stats['stats']['sentiment_breakdown'].items():
        print(f"      {sentiment}: {count}")
    
    # Save results
    print("\n4. Saving results...")
    output_file = "data/outputs/test_results.json"
    os.makedirs("data/outputs", exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump({
            "test_run": "sample_data_ingestion",
            "total_processed": len(results),
            "results": results,
            "statistics": stats['stats']
        }, f, indent=2)
    
    print(f"   ✓ Results saved to {output_file}")
    
    # Test retrieval
    print("\n5. Testing document retrieval...")
    if results:
        doc_id = results[0]['document_id']
        retrieved = pipeline.retrieve(doc_id)
        if retrieved['status'] == 'success':
            print(f"   ✓ Successfully retrieved document {doc_id}")
            print(f"   Summary: {retrieved['data']['analysis']['summary'][:100]}...")
    
    print("\n" + "=" * 60)
    print("\n✅ Pipeline test completed successfully!")
    print(f"\nNext steps:")
    print(f"  • Start API server: python main.py")
    print(f"  • View UI: http://localhost:8000")
    print(f"  • API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    try:
        test_pipeline()
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
