import time
from typing import Any, Callable

from app.fortyguard_client import FortyGuardError


def submit_and_wait(
    client_method: Callable[..., Any],
    client: Any,
    label: str,
    *,
    poll_interval: float = 5.0,
    initial_delay: float = 3.0,
    transient_403_retries: int = 4,
    failure_retries: int = 2,
    timeout: float = 600.0,
    skip_on_failure: bool = False,
    **kwargs: Any,
) -> dict[str, Any] | None:

    def give_up(exc: Exception):
        if skip_on_failure:
            return None

        raise exc

    for submit_attempt in range(failure_retries + 1):

        try:
            activity_id = client_method(
                wait=False,
                **kwargs,
            )
        except Exception as exc:
            if submit_attempt < failure_retries:
                time.sleep(5 * (submit_attempt + 1))
                continue

            return give_up(exc)

        if initial_delay:
            time.sleep(initial_delay)

        for poll_attempt in range(transient_403_retries + 1):

            try:
                result = client.wait_for(
                    activity_id,
                    poll_interval=poll_interval,
                    timeout=timeout,
                )
                return {
                    "activity_id": activity_id,
                    "result": result,
                }

            except FortyGuardError as exc:

                message = str(exc)

                is_403 = (
                    "-> 403" in message
                    or "Unauthorized access" in message
                )
                is_task_failure = (
                    " failed:" in message
                    and "-> " not in message
                )

                if (
                    is_403
                    and poll_attempt < transient_403_retries
                ):
                    time.sleep(5 * (poll_attempt + 1))
                    continue

                if (
                    is_task_failure
                    and submit_attempt < failure_retries
                ):
                    time.sleep(5 * (submit_attempt + 1))
                    break

                
                return give_up(exc)

            except Exception as exc:
                return give_up(exc)

    return give_up(
        RuntimeError(
            f"{label}: exhausted all submission attempts."
        )
    )
