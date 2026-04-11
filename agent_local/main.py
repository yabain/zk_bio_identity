import argparse

from config import load_config
from logging_config import configure_logging
from service import AgentService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to YAML configuration file")
    args = parser.parse_args()

    configure_logging()
    config = load_config(args.config)
    AgentService(config).run_forever()


if __name__ == "__main__":
    main()
