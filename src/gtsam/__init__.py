import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Use DEBUG for more verbose logs
    format='[%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger("spg-gtsam")

