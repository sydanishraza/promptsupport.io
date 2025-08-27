import time
import logging
from functools import wraps

logger = logging.getLogger("ke")

def stage_log(stage_name: str):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.time()
            job_id = kwargs.get("job_id") or getattr(args[0], "job_id", None) or "-"
            logger.info({"event":"stage_start","stage":stage_name,"job_id":job_id})
            out = fn(*args, **kwargs)
            dur = int((time.time()-start)*1000)
            logger.info({"event":"stage_end","stage":stage_name,"job_id":job_id,"duration_ms":dur})
            return out
        return wrapper
    return deco