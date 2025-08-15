"""This module contains the models for telemetry logging."""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response

LOGGER = logging.getLogger(__name__)


class MessagePayload(BaseModel):
    """Represents a message payload for telemetry logging."""

    request_method: str
    request_body: str | None = None
    request_url_path: str
    request_query_params: dict[str, Any] = {}
    request_path_params: dict[str, Any] = {}
    headers: dict[str, Any] = {}
    response_body: Any | None = None
    response_status_code: int
    process_time_ns: int | None = None

    @classmethod
    async def from_request_response(
        cls, request: Request, response: Response, process_time_ns: int | None = None
    ) -> MessagePayload:
        # Extract request body as string
        request_body_str = None
        try:
            raw_body = await request.body()
            if raw_body:
                request_body_str = raw_body.decode("utf-8")
                request_body_str = " ".join(request_body_str.split())
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Could not extract request body.", exc_info=exc)

        # Extract request details
        endpoint_path = request.url.path
        query_params = dict(request.query_params)
        path_params = dict(request.path_params)
        method = request.method
        headers = dict(request.headers)

        # Extract and process response body
        response_body = response.body
        if response_body:
            try:
                response_body = json.loads(response_body)
            except json.JSONDecodeError:
                response_body = response_body.decode("utf-8")

        status_code = getattr(response, "status_code", 500)

        return cls(
            request_method=method,
            request_body=request_body_str,
            request_url_path=endpoint_path,
            request_query_params=query_params,
            request_path_params=path_params,
            headers=headers,
            response_body=response_body,
            response_status_code=status_code,
            process_time_ns=process_time_ns,
        )
