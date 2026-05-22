import logging


class TraceIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "trace_id"):
            record.trace_id = "-"
        return True


def configure_logging() -> None:
    _filter = TraceIdFilter()
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s trace_id=%(trace_id)s %(message)s")
        )
        handler.addFilter(_filter)
        root.addHandler(handler)
    else:
        for handler in root.handlers:
            handler.addFilter(_filter)
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s trace_id=%(trace_id)s %(message)s")
            )
    root.addFilter(_filter)
