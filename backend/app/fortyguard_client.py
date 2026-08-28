import os
import time
from functools import lru_cache
from typing import Any

import requests

from app.config import get_settings


class FortyGuardError(Exception):
    pass


class FortyGuardClient:
    def __init__(self, api_key: str, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "api-key": api_key,
            "Content-Type": "application/json",
        })

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        response = self.session.request(
            method,
            f"{self.base_url}{path}",
            timeout=60,
            **kwargs,
        )
        if not response.ok:
            raise FortyGuardError(
                f"{method} {path} -> {response.status_code}: {response.text[:500]}"
            )

        body = response.json()
        if body.get("error"):
            raise FortyGuardError(body.get("message", "FortyGuard request failed."))
        return body

    def _submit(self, path: str, payload: dict[str, Any]) -> str:
        body = self._request("POST", path, json=payload)
        try:
            return body["data"]["activity_id"]
        except KeyError as exc:
            raise FortyGuardError(f"Unexpected response shape: {body}") from exc

    def wait_for(
        self,
        activity_id: str,
        poll_interval: float = 5.0,
        timeout: float = 600.0,
    ) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            response = self.session.get(
                f"{self.base_url}/v1/status/{activity_id}",
                timeout=60,
            )
            if response.status_code == 404:
                time.sleep(poll_interval)
                continue
            if not response.ok:
                raise FortyGuardError(
                    f"GET /v1/status/{activity_id} -> {response.status_code}: "
                    f"{response.text[:500]}"
                )

            data = response.json().get("data", {})
            status = str(data.get("status", "")).lower()
            if status in {"completed", "succeeded"}:
                return data.get("result", data)
            if status in {"failed", "error"}:
                raise FortyGuardError(
                    f"Activity {activity_id} failed: {data.get('message') or data}"
                )
            time.sleep(poll_interval)

        raise FortyGuardError(
            f"Activity {activity_id} timed out after {timeout:.0f} seconds."
        )

    def heatmap(self, *, wait: bool = True, **kwargs: Any) -> str | dict[str, Any]:
        activity_id = self._submit("/v1/heatmap", kwargs)
        return self.wait_for(activity_id) if wait else activity_id

    def env_params(self, *, wait: bool = True, **kwargs: Any) -> str | dict[str, Any]:
        activity_id = self._submit("/v1/env_params", kwargs)
        return self.wait_for(activity_id) if wait else activity_id

    def satellite(self, *, wait: bool = True, **kwargs: Any) -> str | dict[str, Any]:
        activity_id = self._submit("/v1/satellite", kwargs)
        return self.wait_for(activity_id) if wait else activity_id

    def streetview(self, *, wait: bool = True, **kwargs: Any) -> str | dict[str, Any]:
        activity_id = self._submit("/v1/streetview", kwargs)
        return self.wait_for(activity_id) if wait else activity_id

    def heat_intelligence(
        self,
        *,
        wait: bool = True,
        **kwargs: Any,
    ) -> str | dict[str, Any]:
        activity_id = self._submit("/v1/heat_intelligence", kwargs)
        return self.wait_for(activity_id) if wait else activity_id


@lru_cache
def get_fortyguard_client() -> FortyGuardClient:
    settings = get_settings()

    if not settings.fortyguard_api_key:
        raise RuntimeError(
            "FORTYGUARD_API_KEY is not configured."
        )

    return FortyGuardClient(
        api_key=settings.fortyguard_api_key,
        base_url=os.getenv(
            "FORTYGUARD_BASE_URL",
            "https://api.fortyguard.com",
        ),
    )

__all__ = [
    "FortyGuardClient",
    "FortyGuardError",
    "get_fortyguard_client",
]
