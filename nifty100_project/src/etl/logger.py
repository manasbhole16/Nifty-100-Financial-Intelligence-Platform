import logging
import os

# 1. Create a "logs" folder if it doesn't exist yet
os.makedirs("logs", exist_ok=True)

# 2. Configure the "receipt format" for our logs
logging.basicConfig(
    filename="logs/pipeline.log",      # Where to save the file
    level=logging.INFO,                # Record everything from INFO and above
    format="%(asctime)s | %(levelname)s | %(message)s", # How the text should look
    datefmt="%Y-%m-%d %H:%M:%S"        # How the timestamp should look
)

# 3. Create a function to hand out the logger to other scripts
def get_logger(module_name):
    return logging.getLogger(module_name)