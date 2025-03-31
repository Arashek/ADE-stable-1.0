import asyncio
import logging
from ..services.test_orchestrator import test_orchestrator
from ..services.model_trainer import model_trainer
from ..services.user_simulation_agent import user_simulator
from ..database.redis_client import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def initialize_testing_system():
    """Initialize the automated testing system."""
    try:
        logger.info("Initializing automated testing system...")

        # Initialize Redis connection
        await redis_client.ping()
        logger.info("Redis connection established")

        # Load existing policies if available
        try:
            await model_trainer.load_policies("models/policies")
            logger.info("Loaded existing policies")
        except Exception as e:
            logger.warning(f"No existing policies found: {str(e)}")

        # Initialize test orchestrator
        await test_orchestrator.initialize()
        logger.info("Test orchestrator initialized")

        # Start continuous testing
        await test_orchestrator.start_automated_testing()
        logger.info("Automated testing started")

    except Exception as e:
        logger.error(f"Error initializing testing system: {str(e)}")
        raise

def main():
    """Main entry point for the startup script."""
    try:
        asyncio.run(initialize_testing_system())
    except KeyboardInterrupt:
        logger.info("Shutting down testing system...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 