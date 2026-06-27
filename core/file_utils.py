import re
from pathlib import Path

VIDEO_SUFFIXES = {'.mp4', '.mkv', '.flv', '.mov', '.ts'}
IMAGE_SUFFIXES = {'.jpg', '.png', '.jpeg'}

def sanitize_filename(name):
    safe = re.sub(r'[\\/:*?"<>|]', '_', str(name)).strip()
    return safe or "clip"

def clean_output_dir(output_dir, include_images=True):
    if not output_dir.exists():
        return
    for file_path in output_dir.iterdir():
        if not file_path.is_file():
            continue
        suffix = file_path.suffix.lower()
        if suffix in VIDEO_SUFFIXES or (include_images and suffix in IMAGE_SUFFIXES):
            try:
                file_path.unlink()
            except Exception as e:
                print(f"⚠️ 无法删除文件 {file_path.name}: {e}")

def contains_media_files(folder_path, require_ass=False, require_srt=False):
    """Check if a folder contains media files needed for processing."""
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        return False
    has_video = any(f.is_file() and f.suffix.lower() in VIDEO_SUFFIXES for f in folder.iterdir())
    if require_ass:
        has_ass = any(f.is_file() and f.suffix.lower() == '.ass' for f in folder.iterdir())
        return has_video and has_ass if not require_srt else has_video and has_ass and any(f.is_file() and f.suffix.lower() == '.srt' for f in folder.iterdir())
    if require_srt:
        has_srt = any(f.is_file() and f.suffix.lower() == '.srt' for f in folder.iterdir())
        return has_video and has_srt
    return has_video

def resolve_input_dir(input_dir, require_ass=False, require_srt=False):
    """Walk input_dir tree to find the best-matching media subdirectory."""
    candidate = Path(input_dir)
    if not candidate.exists():
        return str(candidate)
    if candidate.is_file():
        return str(candidate.parent)
    if contains_media_files(candidate, require_ass=require_ass, require_srt=require_srt):
        return str(candidate)
    session_dirs = [p for p in candidate.iterdir()
                    if p.is_dir() and contains_media_files(p, require_ass=require_ass, require_srt=require_srt)]
    if not session_dirs:
        return str(candidate)
    session_dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    selected = session_dirs[0]
    print(f"\U0001f4c1 检测到输入根目录，自动选择最近的素材目录: {selected.name}")
    return str(selected)
