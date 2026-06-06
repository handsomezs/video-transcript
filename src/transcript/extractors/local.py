# src/transcript/extractors/local.py
import os
import tempfile
from transcript.extractors.base import BaseExtractor, Transcript, Segment


VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv", ".m4v"}


class LocalExtractor(BaseExtractor):
    def supports(self, input_path: str) -> bool:
        if input_path.startswith(("http://", "https://")):
            return False
        ext = os.path.splitext(input_path)[1].lower()
        if ext in VIDEO_EXTENSIONS:
            return True
        if os.path.isfile(input_path):
            return True
        return False

    def extract(self, input_path: str, lang: str = "auto") -> Transcript:
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"视频文件不存在: {input_path}")

        audio_path = self._extract_audio(input_path)
        try:
            return self._transcribe(audio_path, lang)
        finally:
            if os.path.exists(audio_path):
                os.unlink(audio_path)

    def _extract_audio(self, video_path: str) -> str:
        import ffmpeg

        fd, audio_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)

        try:
            ffmpeg.input(video_path).output(
                audio_path, acodec="pcm_s16le", ac=1, ar="16000"
            ).run(quiet=True, overwrite_output=True)
        except ffmpeg.Error as e:
            raise RuntimeError(f"音频提取失败: {e.stderr.decode() if e.stderr else e}")

        return audio_path

    def _transcribe(self, audio_path: str, lang: str) -> Transcript:
        from faster_whisper import WhisperModel

        model_size = "small"
        model = WhisperModel(model_size, device="cpu", compute_type="int8")

        lang_param = None if lang == "auto" else lang
        segments_out, info = model.transcribe(audio_path, language=lang_param)

        segments = []
        for seg in segments_out:
            segments.append(
                Segment(start=round(seg.start, 3), end=round(seg.end, 3), text=seg.text.strip())
            )

        detected_lang = info.language if info.language else lang

        return Transcript(
            segments=segments,
            language=detected_lang,
            source_type="local",
        )
