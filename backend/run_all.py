import os
import sys
import logging
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_script(script_path):
    logger.info(f"Starting execution of: {script_path}")
    try:
        # We use sys.executable to ensure the same Python interpreter is used
        result = subprocess.run([sys.executable, script_path], check=True, text=True)
        logger.info(f"Successfully completed: {script_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running {script_path}. Exit code: {e.returncode}")
        sys.exit(1)

def main():
    logger.info("=== Starting Automated Data Pipeline ===")
    
    # 1. Scrape New Data
    run_script(os.path.join(os.path.dirname(__file__), 'scrapers', 'apify_reddit.py'))
    run_script(os.path.join(os.path.dirname(__file__), 'scrapers', 'playstore.py'))
    run_script(os.path.join(os.path.dirname(__file__), 'scrapers', 'youtube.py'))
    
    # 2. Clean and Filter Data
    run_script(os.path.join(os.path.dirname(__file__), 'processing', 'cleaner.py'))
    
    # 3. Analyze Data with Groq LLM
    run_script(os.path.join(os.path.dirname(__file__), 'processing', 'analyzer.py'))
    
    logger.info("=== Automated Data Pipeline Completed Successfully ===")

if __name__ == "__main__":
    main()
