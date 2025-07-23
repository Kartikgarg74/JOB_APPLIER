import logging


def setup_logging(log_level_str: str = "INFO"):
    """
    [CONTEXT] Sets up the logging configuration for the application.
    [PURPOSE] Centralizes logging setup to ensure consistent log levels and formatting.
    """
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    # Optionally, add a file handler
    # log_file = os.getenv('LOG_FILE', 'job_applier_agent.log')
    # file_handler = logging.FileHandler(log_file)
    # file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    # logging.getLogger().addHandler(file_handler)

    logging.info(f"Logging set up with level: {log_level_str.upper()}")
