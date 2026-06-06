# src/transcript/cli.py
import sys
import click
from transcript.engine import TranscriptEngine
from transcript.extractors.youtube import YouTubeExtractor
from transcript.extractors.bilibili import BilibiliExtractor
from transcript.extractors.local import LocalExtractor


def _build_engine():
    return TranscriptEngine(
        extractors=[
            YouTubeExtractor(),
            BilibiliExtractor(),
            LocalExtractor(),
        ]
    )


@click.group()
def main():
    """video-transcript - 视频逐字稿提取工具"""


@main.command()
@click.argument("input_path")
@click.option("--lang", default="auto", help="语言: zh, en, auto (默认)")
@click.option("--format", "fmt", default="txt", help="输出格式: txt, srt, json (默认txt)")
@click.option("--output", "-o", default=None, help="输出文件路径，默认打印到终端")
def get(input_path, lang, fmt, output):
    """从视频获取逐字稿"""
    engine = _build_engine()
    try:
        click.echo("正在处理...", err=True)
        result = engine.get_transcript(input_path, lang=lang, fmt=fmt)
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(result)
            click.echo(f"已保存到: {output}", err=True)
        else:
            click.echo(result)
    except ValueError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    except FileNotFoundError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"未知错误: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("url")
def list(url):
    """列出视频的可用字幕"""
    engine = _build_engine()
    try:
        subtitles = engine.list_subtitles(url)
        if not subtitles:
            click.echo("未找到可用字幕")
            return
        click.echo(f"找到 {len(subtitles)} 个字幕:\n")
        for sub in subtitles:
            label = "人工字幕" if sub.get("type") == "manual" else "自动字幕"
            click.echo(f"  {sub['language']} ({label}) [{sub['ext']}]")
    except ValueError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
