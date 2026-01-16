import argparse
import sys
import logging
from kriptomatte.infrastructure.logging.logger import setup_logger
from kriptomatte.infrastructure.persistence.exr_repository import OpenExrRepository
from kriptomatte.application.services import CryptomatteExtractionService

def get_args():
    parser = argparse.ArgumentParser(description='Decode Cryptomattes in EXR file to PNG files (DDD Refactored).')
    parser.add_argument('--input', '-i', dest='input_path', type=str, required=True,
                        help='Provide path of exr file')
    return parser.parse_args()

def main():
    args = get_args()
    
    # Setup Infrastructure
    logger = setup_logger()
    
    repo = OpenExrRepository()
    service = CryptomatteExtractionService(repo)
    
    try:
        service.extract_all(args.input_path)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
