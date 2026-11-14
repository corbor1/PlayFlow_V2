import logging
import structlog
from fastapi import Request

def configure_structlog():
    # Базовая настройка стандартного logging (для Docker/контейнеров)
    logging.basicConfig(
        format="%(message)s",  # Важно: передаем только сообщение, остальное делает structlog
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),  # ISO формат времени
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,  # Связка с logging
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

configure_structlog()
