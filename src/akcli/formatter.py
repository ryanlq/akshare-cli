"""Output formatting for DataFrames."""

from __future__ import annotations

import sys
from typing import Optional

import pandas as pd
from rich.console import Console
from rich.table import Table


def format_table(df: pd.DataFrame, limit: Optional[int] = None, columns: Optional[list[str]] = None) -> None:
    """Print DataFrame as a Rich table to stdout."""
    if df.empty:
        Console().print("[dim]No data returned.[/dim]")
        return

    if columns:
        available = [c for c in columns if c in df.columns]
        df = df[available]
    if limit is not None:
        df = df.head(limit)

    console = Console(width=200)
    table = Table(show_header=True, header_style="bold cyan", show_lines=False, pad_edge=False)

    for col in df.columns:
        table.add_column(str(col), overflow="ellipsis")

    for _, row in df.iterrows():
        table.add_row(*[str(v) for v in row.values])

    console.print(table)
    console.print(f"[dim]{len(df)} rows x {len(df.columns)} columns[/dim]")


def format_json(df: pd.DataFrame, limit: Optional[int] = None, columns: Optional[list[str]] = None) -> str:
    """Return DataFrame as JSON string."""
    if columns:
        available = [c for c in columns if c in df.columns]
        df = df[available]
    if limit is not None:
        df = df.head(limit)
    return df.to_json(orient="records", force_ascii=False, date_format="iso", indent=2)


def format_csv(df: pd.DataFrame, limit: Optional[int] = None, columns: Optional[list[str]] = None) -> str:
    """Return DataFrame as CSV string."""
    if columns:
        available = [c for c in columns if c in df.columns]
        df = df[available]
    if limit is not None:
        df = df.head(limit)
    return df.to_csv(index=False)


def format_excel(df: pd.DataFrame, output_path: str, limit: Optional[int] = None, columns: Optional[list[str]] = None) -> None:
    """Write DataFrame to Excel file."""
    if columns:
        available = [c for c in columns if c in df.columns]
        df = df[available]
    if limit is not None:
        df = df.head(limit)
    df.to_excel(output_path, index=False, engine="openpyxl")


def format_output(
    df: pd.DataFrame,
    fmt: str = "table",
    output: Optional[str] = None,
    limit: Optional[int] = None,
    columns: Optional[list[str]] = None,
) -> None:
    """Format and output DataFrame according to user preferences."""
    if df.empty:
        if fmt == "json":
            print("[]")
        else:
            Console().print("[dim]No data returned.[/dim]")
        return

    if fmt == "table":
        if output:
            # Write as CSV if output specified for table format
            with open(output, "w") as f:
                f.write(format_csv(df, limit=limit, columns=columns))
        else:
            format_table(df, limit=limit, columns=columns)

    elif fmt == "json":
        result = format_json(df, limit=limit, columns=columns)
        if output:
            with open(output, "w") as f:
                f.write(result)
        else:
            print(result)

    elif fmt == "csv":
        result = format_csv(df, limit=limit, columns=columns)
        if output:
            with open(output, "w") as f:
                f.write(result)
        else:
            print(result)

    elif fmt == "excel":
        if not output:
            output = "output.xlsx"
        format_excel(df, output, limit=limit, columns=columns)
        Console().print(f"[green]Saved to {output}[/green]")

    elif fmt == "tsv":
        if columns:
            available = [c for c in columns if c in df.columns]
            df = df[available]
        if limit is not None:
            df = df.head(limit)
        result = df.to_csv(index=False, sep="\t")
        if output:
            with open(output, "w") as f:
                f.write(result)
        else:
            print(result)

    else:
        Console().print(f"[red]Unknown format: {fmt}. Use: table, json, csv, excel, tsv[/red]")
