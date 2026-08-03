"""
Extracts metadata from video files using FFmpegManager.
"""
from pathlib import Path
from engines.video_engine.ffmpeg.ffmpeg_manager import FFmpegManager
from core.models.video_models import ExtendedVideoMetadata, AudioStreamMetadata, VideoStreamMetadata

class MetadataService:
    def __init__(self, ffmpeg_manager: FFmpegManager) -> None:
        self.ffmpeg_manager = ffmpeg_manager

    def extract_metadata(self, file_path: Path) -> ExtendedVideoMetadata:
        """Extract fully populated metadata from a video file."""
        data = self.ffmpeg_manager.run_ffprobe(file_path)
        
        format_info = data.get("format", {})
        streams = data.get("streams", [])
        
        v_streams = []
        a_streams = []
        
        duration = float(format_info.get("duration", 0.0))
        size = int(format_info.get("size", 0))
        container = format_info.get("format_name", "")
        creation_time = format_info.get("tags", {}).get("creation_time")
        
        width = 0
        height = 0
        fps = 0.0
        aspect_ratio = ""
        rotation = 0
        
        for stream in streams:
            if stream.get("codec_type") == "video":
                fps_str = stream.get("r_frame_rate", "0/1")
                try:
                    num, den = map(int, fps_str.split('/'))
                    current_fps = num / den if den != 0 else 0.0
                except Exception:
                    current_fps = 0.0
                
                bitrate = stream.get("bit_rate")
                v_stream = VideoStreamMetadata(
                    index=stream.get("index", 0),
                    codec_name=stream.get("codec_name", ""),
                    width=stream.get("width", 0),
                    height=stream.get("height", 0),
                    fps=current_fps,
                    bitrate=int(bitrate) if bitrate else None
                )
                v_streams.append(v_stream)
                
                # Assume first video stream represents main file props
                if width == 0:
                    width = v_stream.width
                    height = v_stream.height
                    fps = current_fps
                    aspect_ratio = stream.get("display_aspect_ratio", "")
                    side_data = stream.get("side_data_list", [])
                    for sd in side_data:
                        if sd.get("side_data_type") == "Display Matrix":
                            rotation = int(sd.get("rotation", 0))

            elif stream.get("codec_type") == "audio":
                bitrate = stream.get("bit_rate")
                a_stream = AudioStreamMetadata(
                    index=stream.get("index", 0),
                    codec_name=stream.get("codec_name", ""),
                    sample_rate=int(stream.get("sample_rate", 0)),
                    channels=stream.get("channels", 0),
                    bitrate=int(bitrate) if bitrate else None
                )
                a_streams.append(a_stream)
        
        return ExtendedVideoMetadata(
            file_path=file_path,
            duration_sec=duration,
            width=width,
            height=height,
            fps=fps,
            has_audio=len(a_streams) > 0,
            container_format=container,
            video_streams=v_streams,
            audio_streams=a_streams,
            aspect_ratio=aspect_ratio,
            rotation=rotation,
            creation_time=creation_time,
            file_size_bytes=size
        )
