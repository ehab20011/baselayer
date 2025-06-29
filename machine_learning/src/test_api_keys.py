from openai import OpenAI
import os
from dotenv import load_dotenv
from pinecone import Pinecone
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def test_openai_connection():
    try:
        # initialize the openai client and get the api key from the env
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # try a completion response from the openai client
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'OpenAI connection successful!'"}
            ]
        )
        
        # log the response
        logger.info("✅ OpenAI API Connection Test")
        logger.info(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        logger.error("❌ Error connecting to OpenAI")
        logger.error(f"Error details: {str(e)}")
        return False

def test_pinecone_connection():
    try:
        # initialize the pinecone client and get the api key from the env
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        
        # get list of indexes from the pinecone client
        indexes = pc.list_indexes()
        
        # check if our index exists
        index_name = os.getenv('PINECONE_INDEX_NAME', 'ppp-vector-search')
        if index_name in indexes.names():
            # try to connect to the index
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            
            logger.info("✅ Pinecone Connection Test")
            logger.info(f"Successfully connected to index: {index_name}")
            logger.info(f"Index stats:")
            logger.info(f"  - Dimension: {stats.dimension}")
            logger.info(f"  - Index Fullness: {stats.index_fullness}")
            logger.info(f"  - Total Vector Count: {stats.total_vector_count}")
            logger.info(f"  - Metric: {stats.metric}")
            return True
        else:
            logger.warning(f"⚠️ Index '{index_name}' not found")
            logger.warning(f"Available indexes: {indexes.names()}")
            return False
        
    except Exception as e:
        logger.error("❌ Error connecting to Pinecone")
        logger.error(f"Error details: {str(e)}")
        return False

if __name__ == "__main__":
    # load environment variables
    load_dotenv('../.env')
    
    # check for required environment variables
    required_vars = ['OPENAI_API_KEY', 'PINECONE_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    # if any of the required environment variables are missing, log an error and exit
    if missing_vars:
        logger.error("Missing required environment variables:")
        for var in missing_vars:
            logger.error(f"  - {var}")
        exit(1)
    
    logger.info("=== Testing API Connections ===")
    # Test OpenAI and Pinecone
    openai_success = test_openai_connection()
    pinecone_success = test_pinecone_connection()
    
    # print the test summary
    logger.info("=== Test Summary ===")
    logger.info(f"OpenAI Connection: {'✅ Success' if openai_success else '❌ Failed'}")
    logger.info(f"Pinecone Connection: {'✅ Success' if pinecone_success else '❌ Failed'}") 