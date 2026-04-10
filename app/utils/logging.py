import logging


def configure_logging(log_level: str) -> None:
    """Configure service-wide logging in a predictable format."""
    logging.basicConfig(
        level=log_level.upper(),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
