from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from .diagnostician import diagnose
from .interpreter import StandardInterpreter
from .loaders import StandardPackError, load_standard_pack, validate_standard_pack
from .output_formatter import format_result
from .versioning import compare_packs, format_changelog


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "diagnose":
            text = Path(args.input).read_text(encoding="utf-8")
            result = diagnose(
                text=text,
                standard_id=args.standard,
                pack_path=args.pack,
                positive_mode=args.positive_mode,
                positive_choices=args.positive_choices,
            )
            output = format_result(result, args.format)
            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
            else:
                print(output, end="")
            return 0

        if args.command == "explain":
            pack = load_standard_pack(args.pack)
            standard = pack.get_standard(args.standard)
            print(StandardInterpreter().explain(standard))
            return 0

        if args.command == "validate-pack":
            pack = validate_standard_pack(args.pack_path)
            print(f"标准包校验通过：{pack.metadata.name} {pack.metadata.version}")
            return 0

        if args.command == "diff-pack":
            print(format_changelog(compare_packs(args.old_pack_path, args.new_pack_path)), end="")
            return 0

        if args.command == "scaffold-pack":
            scaffold_pack(args.name, args.output)
            print(f"已创建标准包模板：{args.output}")
            return 0

    except (StandardPackError, KeyError, ValueError, FileNotFoundError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sat", description="标准行动转译工具")
    subparsers = parser.add_subparsers(dest="command")

    diagnose_parser = subparsers.add_parser("diagnose", help="诊断材料并生成行动建议")
    diagnose_parser.add_argument("--pack", required=True, help="标准包目录")
    diagnose_parser.add_argument("--standard", required=True, help="标准编号，如 B7")
    diagnose_parser.add_argument("--input", required=True, help="待诊断材料路径")
    diagnose_parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    diagnose_parser.add_argument("--output", help="输出文件路径")
    diagnose_parser.add_argument(
        "--positive-mode",
        choices=["ask", "no", "yes"],
        default="ask",
        help="当材料较符合标准时，控制是否进入优势提炼流程",
    )
    diagnose_parser.add_argument(
        "--positive-choices",
        help="当 --positive-mode yes 时，传入组长选择，如 1A,2A,3B",
    )

    explain_parser = subparsers.add_parser("explain", help="解释某条标准")
    explain_parser.add_argument("--pack", required=True, help="标准包目录")
    explain_parser.add_argument("--standard", required=True, help="标准编号，如 B7")

    validate_parser = subparsers.add_parser("validate-pack", help="校验标准包")
    validate_parser.add_argument("pack_path")

    diff_parser = subparsers.add_parser("diff-pack", help="比较两个标准包")
    diff_parser.add_argument("old_pack_path")
    diff_parser.add_argument("new_pack_path")

    scaffold_parser = subparsers.add_parser("scaffold-pack", help="创建迁移标准包模板")
    scaffold_parser.add_argument("--name", required=True, help="新标准包名称")
    scaffold_parser.add_argument("--output", required=True, help="输出目录")

    return parser


def scaffold_pack(name: str, output: str) -> None:
    project_root = Path(__file__).resolve().parents[2]
    template = project_root / "data" / "standard_packs" / "template_school_pack"
    destination = Path(output)
    if destination.exists():
        raise ValueError(f"output already exists: {destination}")
    shutil.copytree(template, destination)

    metadata_path = destination / "metadata.json"
    metadata = metadata_path.read_text(encoding="utf-8")
    metadata = metadata.replace("template_school_pack", name)
    metadata = metadata.replace("学校/区域标准包模板", name)
    metadata_path.write_text(metadata, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
