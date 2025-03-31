import os
import sys
import subprocess
import argparse
from pathlib import Path
import json
from typing import Dict, Any, List
from ...config.logging_config import logger

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Launch distributed training')
    parser.add_argument('--nodes', type=int, default=1,
                      help='Number of nodes to use')
    parser.add_argument('--gpus-per-node', type=int, default=1,
                      help='Number of GPUs per node')
    parser.add_argument('--node-rank', type=int, default=0,
                      help='Rank of the current node')
    parser.add_argument('--master-addr', type=str, default='localhost',
                      help='Address of the master node')
    parser.add_argument('--master-port', type=int, default=29500,
                      help='Port of the master node')
    parser.add_argument('--config', type=str, required=True,
                      help='Path to training configuration file')
    parser.add_argument('--output-dir', type=str, required=True,
                      help='Output directory for training results')
    parser.add_argument('--resume-from', type=str,
                      help='Path to checkpoint to resume from')
    return parser.parse_args()

def get_gpu_info() -> List[Dict[str, Any]]:
    """Get information about available GPUs"""
    try:
        import torch
        gpu_info = []
        
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                gpu_info.append({
                    'id': i,
                    'name': torch.cuda.get_device_name(i),
                    'memory_total': torch.cuda.get_device_properties(i).total_memory,
                    'memory_free': torch.cuda.memory_allocated(i)
                })
                
        return gpu_info
        
    except Exception as e:
        logger.error(f"Error getting GPU info: {str(e)}")
        return []

def launch_training(args: argparse.Namespace):
    """Launch distributed training"""
    try:
        # Load configuration
        with open(args.config, 'r') as f:
            config = json.load(f)
            
        # Get GPU information
        gpu_info = get_gpu_info()
        if not gpu_info:
            logger.warning("No GPUs found. Training will use CPU only.")
            
        # Calculate world size
        world_size = args.nodes * args.gpus_per_node
        
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save launch configuration
        launch_config = {
            'nodes': args.nodes,
            'gpus_per_node': args.gpus_per_node,
            'world_size': world_size,
            'master_addr': args.master_addr,
            'master_port': args.master_port,
            'gpu_info': gpu_info,
            'config': config
        }
        
        with open(output_dir / "launch_config.json", 'w') as f:
            json.dump(launch_config, f, indent=2)
            
        # Launch training processes
        processes = []
        
        for local_rank in range(args.gpus_per_node):
            # Calculate global rank
            global_rank = args.node_rank * args.gpus_per_node + local_rank
            
            # Set environment variables
            env = os.environ.copy()
            env.update({
                'WORLD_SIZE': str(world_size),
                'RANK': str(global_rank),
                'LOCAL_RANK': str(local_rank),
                'MASTER_ADDR': args.master_addr,
                'MASTER_PORT': str(args.master_port)
            })
            
            # Set CUDA device
            if gpu_info:
                env['CUDA_VISIBLE_DEVICES'] = str(local_rank)
                
            # Launch training process
            cmd = [
                sys.executable,
                '-m',
                'backend.learning.train',
                '--config', args.config,
                '--output-dir', args.output_dir
            ]
            
            if args.resume_from:
                cmd.extend(['--resume-from', args.resume_from])
                
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            processes.append(process)
            
        # Monitor processes
        while processes:
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    # Process finished
                    stdout, stderr = process.communicate()
                    
                    if process.returncode != 0:
                        logger.error(f"Process {i} failed with return code {process.returncode}")
                        logger.error(f"stdout: {stdout.decode()}")
                        logger.error(f"stderr: {stderr.decode()}")
                        
                    processes.pop(i)
                    break
                    
            import time
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Error launching training: {str(e)}")
        raise

def main():
    """Main entry point"""
    try:
        args = parse_args()
        launch_training(args)
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 