# src/transcript/web.py
import tempfile
import os
import gradio as gr
from transcript.engine import TranscriptEngine
from transcript.extractors.youtube import YouTubeExtractor
from transcript.extractors.bilibili import BilibiliExtractor
from transcript.extractors.local import LocalExtractor


def build_engine():
    return TranscriptEngine(
        extractors=[
            YouTubeExtractor(),
            BilibiliExtractor(),
            LocalExtractor(),
        ]
    )


engine = build_engine()


def process_transcript(input_url, input_file, lang, fmt):
    input_path = input_url.strip() if input_url else None

    if input_file is not None:
        input_path = input_file

    if not input_path:
        return "请输入URL或上传视频文件", None

    try:
        text = engine.get_transcript(input_path, lang=lang, fmt=fmt)

        suffix = ".srt" if fmt == "srt" else (".json" if fmt == "json" else ".txt")
        fd, filepath = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)

        return text, filepath
    except Exception as e:
        return f"处理失败: {e}", None


def create_ui():
    with gr.Blocks(title="Video Transcript 视频逐字稿") as demo:
        gr.Markdown("# Video Transcript 视频逐字稿提取工具")

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 输入")
                input_url = gr.Textbox(
                    label="视频链接 (YouTube / B站)",
                    placeholder="https://www.youtube.com/watch?v=...",
                )
                input_file = gr.File(
                    label="或上传本地视频",
                    file_types=["video"],
                )
                with gr.Row():
                    lang = gr.Dropdown(
                        choices=["auto", "zh", "en"],
                        value="auto",
                        label="语言",
                    )
                    fmt = gr.Dropdown(
                        choices=["txt", "srt", "json"],
                        value="txt",
                        label="输出格式",
                    )
                submit_btn = gr.Button("获取逐字稿", variant="primary")

            with gr.Column(scale=1):
                gr.Markdown("### 逐字稿")
                output_text = gr.Textbox(
                    label="结果",
                    lines=20,
                    max_lines=30,
                    interactive=True,
                    placeholder="逐字稿将在这里显示...",
                )
                download_file = gr.File(label="下载文件", visible=True)

        submit_btn.click(
            fn=process_transcript,
            inputs=[input_url, input_file, lang, fmt],
            outputs=[output_text, download_file],
        )

    return demo


def main():
    demo = create_ui()
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)


if __name__ == "__main__":
    main()
