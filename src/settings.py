import os
import sys
import logging
from dotenv import load_dotenv

# initialize logger
logger = logging.getLogger("pipetest")
logging.basicConfig(format='[%(asctime)s] %(levelname)s - %(message)s', level=logging.INFO)
queried_user = ""

try:
    load_dotenv()
    queried_users_str = os.getenv("PIPETEST_QUERIED_USERS")
    queried_users = queried_users_str.split(",")
    querying_interval = int(os.getenv("PIPETEST_QUERYING_INTERVAL"))
    pipedrive_api_token = os.getenv("PIPETEST_PIEPEDRIVE_API_KEY")
    pipedrive_company_name = os.getenv("PIPETEST_PIEPEDRIVE_COMPANY_NAME")
except Exception as e:
    logger.exception(e)
    sys.exit()

if len(queried_users) / querying_interval > 1:
    logger.warning("With current configuration GitHub API rate limit will be exceeded. Check PIPETEST_QERIED_USERS and PIPETEST_QUERYING_PERIOD values")
