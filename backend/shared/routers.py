from typing import Any, Callable, get_type_hints, NoReturn, Never

from fastapi import APIRouter as _APIRouter


class APIRouter(_APIRouter):
    """
    Overrides the route decorator logic to use the annotated return type as the `response_model` if unspecified.
    """

    def add_api_route(
        self, path: str, endpoint: Callable[..., Any], **kwargs: dict[str, Any]
    ) -> None:  # pragma: no cover
        if kwargs.get("response_model") is None:
            return_annotation = get_type_hints(endpoint).get("return")
            invalid_annotations = (type(None), NoReturn, Never)

            if return_annotation not in invalid_annotations:
                kwargs["response_model"] = return_annotation

        return super().add_api_route(path, endpoint, **kwargs)
