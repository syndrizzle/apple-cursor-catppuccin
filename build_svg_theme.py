#!/usr/bin/env python3

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, Union
from xml.etree import ElementTree

import toml


SVG_NAMESPACE = "http://www.w3.org/2000/svg"
XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"
BASE_COLOR = re.compile(r"#00ff00", re.IGNORECASE)
OUTLINE_COLOR = re.compile(r"#0000ff", re.IGNORECASE)
Number = Union[int, float]

ElementTree.register_namespace("", SVG_NAMESPACE)
ElementTree.register_namespace("xlink", XLINK_NAMESPACE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a KDE Plasma scalable SVG cursor theme."
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--svg-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--base-color", required=True)
    parser.add_argument("--outline-color", required=True)
    parser.add_argument("--canvas-size", type=int, default=32)
    parser.add_argument("--nominal-size", type=int, default=24)
    return parser.parse_args()


def get_setting(
    cursor: Dict[str, Any], fallback: Dict[str, Any], name: str
) -> Any:
    if name in cursor:
        return cursor[name]
    if name in fallback:
        return fallback[name]
    raise KeyError(f"Missing cursor setting: {name}")


def replace_colors(value: str, base_color: str, outline_color: str) -> str:
    value = BASE_COLOR.sub(base_color, value)
    return OUTLINE_COLOR.sub(outline_color, value)


def parse_dimension(value: str, path: Path, dimension: str) -> float:
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(?:px)?\s*", value)
    if not match:
        raise ValueError(f"Unsupported SVG {dimension} in {path}: {value}")
    return float(match.group(1))


def compact_number(value: float) -> Number:
    rounded = round(value, 8)
    if rounded.is_integer():
        return int(rounded)
    return rounded


def write_svg(
    source: Path,
    destination: Path,
    base_color: str,
    outline_color: str,
    canvas_size: int,
) -> Tuple[float, float]:
    parser = ElementTree.XMLParser(
        target=ElementTree.TreeBuilder(insert_comments=True)
    )
    tree = ElementTree.parse(source, parser=parser)
    root = tree.getroot()

    source_width = parse_dimension(root.attrib["width"], source, "width")
    source_height = parse_dimension(root.attrib["height"], source, "height")

    root.set("width", str(canvas_size))
    root.set("height", str(canvas_size))

    for element in root.iter():
        for name, value in element.attrib.items():
            element.set(
                name, replace_colors(value, base_color, outline_color)
            )
        if element.text:
            element.text = replace_colors(
                element.text, base_color, outline_color
            )
        if element.tail:
            element.tail = replace_colors(
                element.tail, base_color, outline_color
            )

    tree.write(destination, encoding="utf-8", xml_declaration=True)
    return source_width, source_height


def svg_sources(svg_dir: Path, png_pattern: str) -> List[Path]:
    svg_pattern = str(Path(png_pattern).with_suffix(".svg"))
    sources = sorted(svg_dir.rglob(svg_pattern))
    if not sources:
        raise FileNotFoundError(
            f"No SVG sources match {svg_pattern!r} in {svg_dir}"
        )
    return sources


def build_cursor(
    svg_dir: Path,
    output_dir: Path,
    cursor: Dict[str, Any],
    fallback: Dict[str, Any],
    base_color: str,
    outline_color: str,
    canvas_size: int,
    nominal_size: int,
) -> None:
    cursor_name = cursor["x11_name"]
    sources = svg_sources(svg_dir, cursor["png"])
    cursor_dir = output_dir / cursor_name
    cursor_dir.mkdir()

    hotspot_x = float(get_setting(cursor, fallback, "x_hotspot"))
    hotspot_y = float(get_setting(cursor, fallback, "y_hotspot"))
    delay = int(get_setting(cursor, fallback, "x11_delay"))
    animated = len(sources) > 1
    metadata = []

    for source in sources:
        destination = cursor_dir / source.name
        source_width, source_height = write_svg(
            source,
            destination,
            base_color,
            outline_color,
            canvas_size,
        )
        frame = {
            "filename": source.name,
            "hotspot_x": compact_number(
                hotspot_x * canvas_size / source_width
            ),
            "hotspot_y": compact_number(
                hotspot_y * canvas_size / source_height
            ),
            "nominal_size": nominal_size,
        }
        if animated:
            if delay <= 0:
                raise ValueError(
                    f"Animated cursor {cursor_name!r} needs a positive delay"
                )
            frame["delay"] = delay
        metadata.append(frame)

    with (cursor_dir / "metadata.json").open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)
        file.write("\n")


def build_aliases(
    output_dir: Path, cursors: Iterable[Dict[str, Any]]
) -> None:
    for cursor in cursors:
        target = cursor["x11_name"]
        if not (output_dir / target).is_dir():
            raise FileNotFoundError(f"Alias target does not exist: {target}")
        for alias in cursor.get("x11_symlinks", []):
            alias_path = output_dir / alias
            if alias_path.exists() or alias_path.is_symlink():
                raise FileExistsError(f"Duplicate cursor name: {alias}")
            alias_path.symlink_to(target, target_is_directory=True)


def build_theme(args: argparse.Namespace) -> None:
    if args.canvas_size <= 0:
        raise ValueError("Canvas size must be positive")
    if args.nominal_size <= 0:
        raise ValueError("Nominal size must be positive")

    config = toml.load(args.config)
    cursor_config = config["cursors"]
    fallback = cursor_config["fallback_settings"]
    cursors = [
        cursor
        for name, cursor in cursor_config.items()
        if name != "fallback_settings" and "x11_name" in cursor
    ]

    shutil.rmtree(args.output_dir, ignore_errors=True)
    args.output_dir.mkdir(parents=True)

    for cursor in cursors:
        build_cursor(
            args.svg_dir,
            args.output_dir,
            cursor,
            fallback,
            args.base_color,
            args.outline_color,
            args.canvas_size,
            args.nominal_size,
        )

    build_aliases(args.output_dir, cursors)


if __name__ == "__main__":
    build_theme(parse_args())
