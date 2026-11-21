import json
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from collections.abc import Callable
import psutil

_PROCESS = psutil.Process()

def otel(f: Callable):

	def wrapper(state):
		span = trace.get_current_span()

		span.set_attribute("process.memory.usage_mb", round(_PROCESS.memory_info().rss / 1024**2, 1))
		span.set_attribute("system.memory.utilization", psutil.virtual_memory().percent)

		try:
			result = f(state)
		except Exception as e:
			span.record_exception(e)
			span.set_status(Status(StatusCode.ERROR, str(e)))
			raise

		return result

	return wrapper