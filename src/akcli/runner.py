"""Safe function execution engine."""

from __future__ import annotations

from typing import Any

import pandas as pd

from akcli.registry import FunctionInfo, ParamInfo


class ExecutionError(Exception):
    pass


class MissingParameterError(ExecutionError):
    pass


class InvalidParameterError(ExecutionError):
    pass


class EmptyResultError(ExecutionError):
    pass


def _coerce_value(value: str, param: ParamInfo) -> Any:
    """Convert string CLI input to the expected type."""
    type_hint = param.type_hint

    if value == "None" or value == "none":
        return None

    # Bool
    if type_hint == "bool":
        return value.lower() in ("true", "1", "yes")

    # Int
    if type_hint == "int":
        try:
            return int(value)
        except ValueError:
            pass

    # Float
    if type_hint in ("float", "float64"):
        try:
            return float(value)
        except ValueError:
            pass

    # List-like: "item1,item2" -> ["item1", "item2"]
    if "list" in type_hint.lower() or "List" in type_hint:
        if "," in value:
            return [v.strip() for v in value.split(",")]
        return [value]

    return value


def execute(func_info: FunctionInfo, params: dict[str, str]) -> pd.DataFrame:
    """Execute an akshare function safely.

    Args:
        func_info: Function metadata from registry.
        params: Raw string parameters from CLI.

    Returns:
        DataFrame result.

    Raises:
        MissingParameterError: Required parameter not provided.
        InvalidParameterError: Value not in allowed choices.
        ExecutionError: Function execution failed.
    """
    # Import akshare lazily
    import akshare as ak

    func = getattr(ak, func_info.name, None)
    if func is None:
        raise ExecutionError(f"Function {func_info.name} not found in akshare")

    # Build validated params
    validated: dict[str, Any] = {}
    for param_info in func_info.params:
        raw_value = params.get(param_info.name)

        if raw_value is not None:
            value = _coerce_value(raw_value, param_info)
            if param_info.choices and value not in param_info.choices:
                raise InvalidParameterError(
                    f"Parameter --{param_info.name}: invalid value '{raw_value}'. "
                    f"Choices: {', '.join(param_info.choices)}"
                )
            validated[param_info.name] = value
        elif param_info.has_default:
            pass  # Use default
        else:
            raise MissingParameterError(
                f"Required parameter --{param_info.name} is missing. "
                f"Run 'ak info {func_info.name}' for details."
            )

    try:
        df = func(**validated)
    except Exception as e:
        raise ExecutionError(f"Failed to execute {func_info.name}: {e}") from e

    if not isinstance(df, pd.DataFrame):
        raise ExecutionError(f"Expected DataFrame, got {type(df).__name__}")

    return df
