#!/usr/bin/env python3

"""
Thailand Synthesis Pipeline Runner
Run the complete Thailand synthetic population generation pipeline
"""

import os
import sys
import argparse

# Add the workspace to Python path
sys.path.insert(0, '/Users/prince/Workspaces/Transport/ile-de-france')

def run_thailand_synthesis():
    """Run the Thailand synthesis pipeline"""
    try:
        import synpp

        # Run the Thailand synthesis pipeline
        synpp.run("config_thailand.yml")
        print("Thailand synthesis pipeline completed successfully!")

    except ImportError:
        print("Error: synpp package not found. Please install it first:")
        print("pip install synpp")
        sys.exit(1)
    except Exception as e:
        print(f"Error running Thailand synthesis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Thailand Synthesis Pipeline')
    parser.add_argument('--config', default='config_thailand.yml',
                       help='Configuration file to use (default: config_thailand.yml)')

    args = parser.parse_args()

    print("Starting Thailand Synthesis Pipeline...")
    print(f"Using configuration: {args.config}")

    # Check if config file exists
    if not os.path.exists(args.config):
        print(f"Error: Configuration file {args.config} not found!")
        sys.exit(1)

    run_thailand_synthesis()
