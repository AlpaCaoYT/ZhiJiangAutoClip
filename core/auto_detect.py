import os

def auto_detect_files(input_dir):
    """自动扫描文件夹下的视频和字幕文件"""
    print(f"正在扫描文件夹: {input_dir}")
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"文件夹不存在: {input_dir}")

    files = os.listdir(input_dir)
    video_exts = ('.mp4', '.flv', '.mkv', '.mov', '.ts')

    videos = [f for f in files if f.lower().endswith(video_exts)]
    srts = [f for f in files if f.lower().endswith('.srt')]

    video_path = None
    srt_path = None

    if len(videos) == 0:
        raise FileNotFoundError("未找到视频文件 (.mp4/.flv/.mkv 等)")
    elif len(videos) > 1:
        raise FileNotFoundError(f"找到多个视频文件，无法确定使用哪个: {videos}")
    else:
        video_path = os.path.join(input_dir, videos[0])
        print(f"已锁定视频: {videos[0]}")

    if len(srts) == 0:
        print("未找到SRT字幕文件，将不写入字幕")
    elif len(srts) > 1:
        raise FileNotFoundError(f"找到多个SRT文件，无法确定使用哪个: {srts}")
    else:
        srt_path = os.path.join(input_dir, srts[0])
        print(f"已锁定字幕: {srts[0]}")

    return video_path, srt_path
