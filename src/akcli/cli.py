"""AKShare CLI - Main entry point."""

from __future__ import annotations

import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from akcli import __version__
from akcli.formatter import format_output
from akcli.registry import FunctionRegistry, FunctionInfo
from akcli.runner import execute, ExecutionError, MissingParameterError, InvalidParameterError
from akcli.categories import SCENES, get_category_tier, get_category_label, get_category_desc
from akcli.favorites import load_favorites, add_favorite, remove_favorite

console = Console()
registry = FunctionRegistry()


def _show_help():
    console.print(Panel(
        "[bold]ak[/bold] - AKShare CLI for Chinese financial data\n\n"
        "[dim]Version:[/dim] " + __version__ + "\n\n"
        "[bold]Usage:[/bold]\n"
        "  ak [cyan]<function_name>[/cyan] [dim]--param1 val1 --param2 val2[/dim]\n"
        "  ak [cyan]list[/cyan] [dim][--all] [--category CAT] [--scene SCENE] [--favorite] [--search TERM][/dim]\n"
        "  ak [cyan]info[/cyan] [dim]<function_name>[/dim]\n"
        "  ak [cyan]fav[/cyan] [dim]<function_name> [备注][/dim]\n"
        "  ak [cyan]unfav[/cyan] [dim]<function_name>[/dim]\n\n"
        "[bold]Global Options:[/bold]\n"
        "  --format json|csv|table|excel|tsv   Output format (default: table)\n"
        "  --output FILE                       Output to file\n"
        "  --limit N                           Limit rows\n"
        "  --columns COL1,COL2                 Select columns\n"
        "  --help, -h                          Show help\n"
        "  --version, -V                       Show version\n\n"
        "[bold]Examples:[/bold]\n"
        "  ak stock_zh_a_hist --symbol 000001 --period daily --start-date 20240101\n"
        "  ak stock_zh_a_spot_em --format json --limit 5\n"
        "  ak list                             [dim]# 核心+常用类别[/dim]\n"
        "  ak list --all                       [dim]# 全部类别[/dim]\n"
        "  ak list --favorite                  [dim]# 我的收藏[/dim]\n"
        "  ak list --category stock            [dim]# 指定类别[/dim]\n"
        "  ak list --scene 选股                [dim]# 按场景筛选[/dim]\n"
        "  ak fav stock_zh_a_hist 最常用        [dim]# 收藏[/dim]\n"
        "  ak unfav stock_zh_a_hist            [dim]# 取消收藏[/dim]\n"
        "  ak info stock_zh_a_hist",
        title="[bold]AKShare CLI[/bold]",
        border_style="cyan",
    ))


def _show_version():
    console.print(f"ak {__version__}")


def _cmd_list(category: Optional[str] = None, search: Optional[str] = None,
              fmt: str = "table", show_all: bool = False, scene: Optional[str] = None,
              favorite: bool = False):
    """List available akshare functions with tiered display."""

    # Favorites mode
    if favorite:
        _cmd_list_favorites(fmt)
        return

    # Determine tier cutoff
    max_tier = 5 if show_all else 2

    # Scene-based filtering
    scene_categories = None
    if scene:
        scene_info = SCENES.get(scene)
        if not scene_info:
            console.print(f"[red]Unknown scene: {scene}[/red]")
            console.print(f"[dim]Available scenes: {', '.join(SCENES.keys())}[/dim]")
            return
        scene_categories = scene_info["categories"]
        max_tier = 5  # scenes always show all their categories

    # List categories overview (when no specific category/search/scene)
    if not category and not search and not scene:
        _cmd_list_categories(max_tier, fmt)
        return

    # List functions for a specific category, search, or scene
    funcs = registry.list_functions(
        category=category, search=search,
        max_tier=max_tier, categories=scene_categories,
    )

    if not funcs:
        console.print("[yellow]No functions found.[/yellow]")
        return

    favs = load_favorites()

    if fmt == "json":
        import json
        data = [
            {"name": f.name, "category": f.category, "category_label": f.category_label,
             "description": f.description, "param_count": len(f.params),
             "tier": get_category_tier(f.category),
             "favorite": f.name in favs}
            for f in funcs
        ]
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # Group by category for cleaner display
    current_cat = None
    for f in funcs:
        if f.category != current_cat:
            current_cat = f.category
            tier = get_category_tier(f.category)
            tier_mark = "" if tier <= 2 else f" [dim](T{tier})[/dim]"
            console.print(f"\n[bold cyan]{get_category_label(f.category)}[/bold cyan]{tier_mark}  [dim]{get_category_desc(f.category)}[/dim]")

        star = "[yellow]*[/yellow]" if f.name in favs else " "
        console.print(f" {star} [bold]{f.name}[/bold]  [dim]{f.description[:55]}[/dim]")

    console.print(f"\n[dim]{len(funcs)} functions[/dim]")


def _cmd_list_favorites(fmt: str):
    """Display favorited functions."""
    favs = load_favorites()
    if not favs:
        console.print("[yellow]No favorites yet.[/yellow]")
        console.print("[dim]Add with: ak fav <function_name> [备注][/dim]")
        return

    if fmt == "json":
        import json
        data = []
        for name, note in favs.items():
            info = registry.get(name)
            data.append({
                "name": name,
                "note": note,
                "category": info.category if info else "unknown",
                "description": info.description if info else "",
            })
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    console.print(f"\n[bold]我的收藏[/bold]  [dim]({len(favs)})[/dim]")
    for name, note in favs.items():
        info = registry.get(name)
        if info:
            desc = info.description[:45]
            cat = get_category_label(info.category)
        else:
            desc = "[dim](函数不存在)[/dim]"
            cat = "?"
        note_str = f"  [dim]{note}[/dim]" if note else ""
        console.print(f"  [yellow]*[/yellow] [bold]{name}[/bold]  [{cat}] {desc}{note_str}")

    console.print()


def _cmd_list_categories(max_tier: int, fmt: str):
    """Display category overview with counts."""
    cats = registry.list_categories(max_tier=max_tier)

    if not cats:
        console.print("[yellow]No categories found.[/yellow]")
        return

    if fmt == "json":
        import json
        data = [
            {"category": cat, "label": label, "description": desc, "count": count, "tier": tier}
            for cat, label, desc, count, tier in cats
        ]
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    current_tier = 0
    tier_names = {1: "核心", 2: "常用", 3: "专业", 4: "小众", 5: "其他"}

    for cat, label, desc, count, tier in cats:
        if tier != current_tier:
            current_tier = tier
            console.print(f"\n[bold]{tier_names.get(tier, '其他')}[/bold]")

        console.print(
            f"  [bold cyan]{label:6s}[/bold cyan]  "
            f"[dim]{desc[:30]:30s}[/dim]  "
            f"[green]{count:3d}[/green] 个函数  "
            f"[dim]ak list --category {cat}[/dim]"
        )

    total = sum(c for _, _, _, c, _ in cats)
    console.print(f"\n[dim]共 {total} 个函数  |  用 'ak list --all' 查看全部  |  用 'ak list --category <类别>' 查看某类[/dim]")

    # Show available scenes
    if SCENES:
        console.print(f"\n[bold]场景筛选[/bold]  [dim]ak list --scene <场景>[/dim]")
        for scene_name, scene_info in SCENES.items():
            console.print(f"  [bold]{scene_name}[/bold]  [dim]{scene_info['desc']}[/dim]")


def _cmd_info(func_name: str, fmt: str = "table"):
    """Show detailed info about a function."""
    info = registry.get(func_name)
    if not info:
        console.print(f"[red]Function '{func_name}' not found.[/red]")
        console.print("[dim]Use 'ak list' to see available functions.[/dim]")
        sys.exit(1)

    if fmt == "json":
        import json
        print(json.dumps(info.to_dict(), ensure_ascii=False, indent=2))
        return

    console.print(f"[bold cyan]{info.name}[/bold cyan]")
    console.print(f"  {info.description}")
    console.print(f"  Category: {info.category_label}")
    console.print()

    if info.params:
        table = Table(show_header=True, header_style="bold", pad_edge=False)
        table.add_column("Parameter", style="bold", width=16)
        table.add_column("Type", width=10)
        table.add_column("Default", width=15)
        table.add_column("Description", min_width=30)
        table.add_column("Choices", style="dim")

        for p in info.params:
            default_str = p.default if p.has_default else "[red]required[/red]"
            choices_str = ", ".join(p.choices) if p.choices else ""
            table.add_row(
                f"--{p.name}", p.type_hint, default_str, p.description[:50], choices_str
            )
        console.print(table)
    else:
        console.print("[dim]No parameters required.[/dim]")

    console.print()
    console.print("[bold]Example:[/bold]")
    parts = [f"ak {info.name}"]
    for p in info.params[:3]:
        val = p.default if p.has_default and p.default and p.default != "None" else "VALUE"
        parts.append(f"--{p.name} {val}")
    console.print(f"  {'  '.join(parts)}")


def _parse_dynamic_args(args: list[str]) -> tuple[str, dict[str, str], dict[str, str]]:
    """Parse dynamic function arguments.

    Returns (func_name, func_params, global_options).
    """
    if not args:
        return "", {}, {}

    func_name = args[0]
    func_params = {}
    global_opts = {}
    reserved = {"--format", "--output", "--limit", "--columns", "--help", "-h", "--version", "-V", "list", "info"}

    i = 1
    while i < len(args):
        arg = args[i]

        if arg in ("--help", "-h"):
            return func_name, func_params, {"help": "true"}
        if arg in ("--version", "-V"):
            return func_name, func_params, {"version": "true"}

        if arg.startswith("--"):
            # Convert --param-name to param_name
            key = arg[2:].replace("-", "_")

            if arg == "--format":
                if i + 1 < len(args):
                    global_opts["format"] = args[i + 1]
                    i += 2
                    continue
            elif arg == "--output":
                if i + 1 < len(args):
                    global_opts["output"] = args[i + 1]
                    i += 2
                    continue
            elif arg == "--limit":
                if i + 1 < len(args):
                    global_opts["limit"] = args[i + 1]
                    i += 2
                    continue
            elif arg == "--columns":
                if i + 1 < len(args):
                    global_opts["columns"] = args[i + 1]
                    i += 2
                    continue
            else:
                # Function parameter
                if i + 1 < len(args) and not args[i + 1].startswith("--"):
                    func_params[key] = args[i + 1]
                    i += 2
                    continue
                else:
                    # Flag-style parameter (no value)
                    func_params[key] = "true"
                    i += 1
                    continue
        else:
            i += 1

    return func_name, func_params, global_opts


def main():
    """Main entry point."""
    args = sys.argv[1:]

    if not args or args[0] in ("--help", "-h"):
        registry.load()
        _show_help()
        return

    if args[0] in ("--version", "-V"):
        _show_version()
        return

    # Load registry (uses cache if available)
    if not registry.load():
        console.print("[red]Failed to load akshare functions. Is akshare installed?[/red]")
        sys.exit(1)

    # Handle subcommands
    if args[0] == "list":
        cat = None
        search = None
        fmt = "table"
        show_all = False
        scene = None
        favorite = False
        i = 1
        while i < len(args):
            if args[i] in ("--category", "-c") and i + 1 < len(args):
                cat = args[i + 1]
                i += 2
            elif args[i] in ("--search", "-s") and i + 1 < len(args):
                search = args[i + 1]
                i += 2
            elif args[i] == "--format" and i + 1 < len(args):
                fmt = args[i + 1]
                i += 2
            elif args[i] == "--scene" and i + 1 < len(args):
                scene = args[i + 1]
                i += 2
            elif args[i] == "--all":
                show_all = True
                i += 1
            elif args[i] in ("--favorite", "--fav", "-f"):
                favorite = True
                i += 1
            else:
                i += 1
        _cmd_list(category=cat, search=search, fmt=fmt, show_all=show_all, scene=scene, favorite=favorite)
        return

    if args[0] == "fav":
        if len(args) < 2:
            console.print("[red]Usage: ak fav <function_name> [备注][/red]")
            sys.exit(1)
        func_name = args[1]
        if not registry.get(func_name):
            console.print(f"[red]Function '{func_name}' not found.[/red]")
            sys.exit(1)
        note = " ".join(args[2:]) if len(args) > 2 else ""
        add_favorite(func_name, note)
        console.print(f"[green]已收藏[/green] {func_name}" + (f"  [dim]{note}[/dim]" if note else ""))
        return

    if args[0] == "unfav":
        if len(args) < 2:
            console.print("[red]Usage: ak unfav <function_name>[/red]")
            sys.exit(1)
        func_name = args[1]
        if remove_favorite(func_name):
            console.print(f"[green]已取消收藏[/green] {func_name}")
        else:
            console.print(f"[yellow]'{func_name}' 不在收藏列表中[/yellow]")
        return

    if args[0] == "info":
        if len(args) < 2:
            console.print("[red]Usage: ak info <function_name>[/red]")
            sys.exit(1)
        fmt = "table"
        if "--format" in args:
            idx = args.index("--format")
            if idx + 1 < len(args):
                fmt = args[idx + 1]
        _cmd_info(args[1], fmt=fmt)
        return

    # Dynamic function execution
    func_name, func_params, global_opts = _parse_dynamic_args(args)

    if not func_name:
        _show_help()
        return

    if global_opts.get("help"):
        _cmd_info(func_name)
        return

    func_info = registry.get(func_name)
    if not func_info:
        console.print(f"[red]Function '{func_name}' not found.[/red]")
        # Try fuzzy match: search by prefix
        prefix = "_".join(func_name.split("_")[:3])
        similar = [f.name for f in registry.list_functions(search=prefix)[:5]]
        if similar:
            console.print(f"[dim]Similar functions: {', '.join(similar)}[/dim]")
        else:
            console.print("[dim]Use 'ak list' to see available functions.[/dim]")
        sys.exit(1)

    # Execute
    try:
        df = execute(func_info, func_params)
    except MissingParameterError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)
    except InvalidParameterError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)
    except ExecutionError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    # Output
    fmt = global_opts.get("format", "table")
    output = global_opts.get("output")
    limit = int(global_opts["limit"]) if "limit" in global_opts else None
    columns = global_opts.get("columns", "").split(",") if "columns" in global_opts and global_opts["columns"] else None

    # Filter out empty strings from columns
    if columns:
        columns = [c.strip() for c in columns if c.strip()]

    format_output(df, fmt=fmt, output=output, limit=limit, columns=columns)


if __name__ == "__main__":
    main()
