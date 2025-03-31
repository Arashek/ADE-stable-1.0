import asyncio
import os
import logging
import argparse
from datetime import datetime
from tests.performance.load_test import LoadTest
from tests.performance.endurance_test import EnduranceTest
from tests.performance.stress_test import StressTest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_tests(
    base_url: str,
    output_dir: str,
    baseline_file: str,
    run_load: bool = True,
    run_endurance: bool = True,
    run_stress: bool = True,
    **kwargs
) -> None:
    """Run performance tests based on specified options."""
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(output_dir, f"performance_test_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Run load test
        if run_load:
            logger.info("Starting load test...")
            await LoadTest.run_test(
                base_url=base_url,
                output_dir=os.path.join(output_dir, "load_test"),
                baseline_file=baseline_file,
                max_concurrent_users=kwargs.get('max_concurrent_users', 100),
                ramp_up_time=kwargs.get('ramp_up_time', 300),
                steady_state_time=kwargs.get('steady_state_time', 600),
                ramp_down_time=kwargs.get('ramp_down_time', 300)
            )
            logger.info("Load test completed")
            
        # Run endurance test
        if run_endurance:
            logger.info("Starting endurance test...")
            await EnduranceTest.run_test(
                base_url=base_url,
                output_dir=os.path.join(output_dir, "endurance_test"),
                baseline_file=baseline_file,
                duration=kwargs.get('duration', 3600),
                check_interval=kwargs.get('check_interval', 300),
                memory_threshold=kwargs.get('memory_threshold', 1000)
            )
            logger.info("Endurance test completed")
            
        # Run stress test
        if run_stress:
            logger.info("Starting stress test...")
            await StressTest.run_test(
                base_url=base_url,
                output_dir=os.path.join(output_dir, "stress_test"),
                baseline_file=baseline_file,
                max_concurrent_requests=kwargs.get('max_concurrent_requests', 1000),
                request_timeout=kwargs.get('request_timeout', 30.0),
                error_threshold=kwargs.get('error_threshold', 0.1),
                recovery_timeout=kwargs.get('recovery_timeout', 300)
            )
            logger.info("Stress test completed")
            
        logger.info(f"All tests completed. Results saved in: {output_dir}")
        
    except Exception as e:
        logger.error(f"Performance testing failed: {str(e)}")
        raise

def main():
    """Main entry point for running performance tests."""
    parser = argparse.ArgumentParser(description='Run ADE platform performance tests')
    parser.add_argument('--base-url', default='http://localhost:8000',
                      help='Base URL of the ADE platform')
    parser.add_argument('--output-dir', default='performance_results',
                      help='Directory to store test results')
    parser.add_argument('--baseline-file', default='baseline_metrics.json',
                      help='Path to baseline metrics file')
    parser.add_argument('--load-test', action='store_true',
                      help='Run load test')
    parser.add_argument('--endurance-test', action='store_true',
                      help='Run endurance test')
    parser.add_argument('--stress-test', action='store_true',
                      help='Run stress test')
    parser.add_argument('--max-concurrent-users', type=int, default=100,
                      help='Maximum number of concurrent users for load test')
    parser.add_argument('--duration', type=int, default=3600,
                      help='Duration of endurance test in seconds')
    parser.add_argument('--max-concurrent-requests', type=int, default=1000,
                      help='Maximum number of concurrent requests for stress test')
    
    args = parser.parse_args()
    
    # If no specific test is selected, run all tests
    if not (args.load_test or args.endurance_test or args.stress_test):
        args.load_test = args.endurance_test = args.stress_test = True
    
    # Run tests
    asyncio.run(run_tests(
        base_url=args.base_url,
        output_dir=args.output_dir,
        baseline_file=args.baseline_file,
        run_load=args.load_test,
        run_endurance=args.endurance_test,
        run_stress=args.stress_test,
        max_concurrent_users=args.max_concurrent_users,
        duration=args.duration,
        max_concurrent_requests=args.max_concurrent_requests
    ))

if __name__ == "__main__":
    main() 