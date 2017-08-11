import logging

class HealthcheckFilter(logging.Filter):
    def filter(self, log_record):
        if 'healthcheck' in log_record.msg:
            return False
        return True