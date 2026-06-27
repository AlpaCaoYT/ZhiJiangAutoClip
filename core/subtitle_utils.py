import os
import re

class SubtitleUtils:
    # 各成员专属字幕样式（Kdenlive 多轨字幕用）
    # 颜色严格对照成员知识库代表色：嘉然粉、贝拉紫、乃琳蓝、心宜金、思诺银
    MEMBER_STYLES = [
        ("嘉然",   "&H00FFFFFF", "&H00B469FF"),  # 粉色 #FF69B4
        ("贝拉",   "&H00FFFFFF", "&H00B6599B"),  # 紫色 #9B59B6
        ("乃琳",   "&H00FFFFFF", "&H00DB9834"),  # 蓝色 #3498DB
        ("心宜",   "&H00FFFFFF", "&H0000D7FF"),  # 金色 #FFD700
        ("思诺",   "&H00FFFFFF", "&H00C0C0C0"),  # 银色 #C0C0C0
        ("ASOUL",  "&H00FFFFFF", "&H00FF6A00"),  # 深蓝 #006AFF
    ]

    def __init__(self, config):
        self.config = config

    @staticmethod
    def parse_srt_time(time_str):
        time_str = time_str.replace(',', '.').strip()
        parts = time_str.split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        if len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        print(f"⚠️ 时间格式无法识别: {time_str}")
        return 0

    @staticmethod
    def sec_to_ass_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds % 1) * 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    @staticmethod
    def sec_to_srt_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    @staticmethod
    def parse_srt(srt_path):
        if not srt_path or not os.path.exists(srt_path):
            return []
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        subs = []
        for block in re.split(r'\n\n+', content.strip()):
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                time_match = re.search(
                    r'(\d+:\d+:\d+[,\.]\d+)\s*-->\s*(\d+:\d+:\d+[,\.]\d+)',
                    lines[1]
                )
                if time_match:
                    start = SubtitleUtils.parse_srt_time(time_match.group(1))
                    end = SubtitleUtils.parse_srt_time(time_match.group(2))
                    text = '\n'.join(lines[2:])
                    subs.append({'start': start, 'end': end, 'text': text})
        return subs

    @staticmethod
    def get_expanded_time_range(subtitles, target_start, target_end, pre_count, post_count):
        if not subtitles:
            return target_start, target_end

        core_start_idx = -1
        core_end_idx = -1
        for i, sub in enumerate(subtitles):
            if sub['end'] > target_start and sub['start'] < target_end:
                if core_start_idx == -1:
                    core_start_idx = i
                core_end_idx = i

        if core_start_idx == -1:
            print("   ⚠️ 警告: 该时间段内无匹配字幕,将使用原始时间戳。")
            return target_start, target_end

        new_start_idx = max(0, core_start_idx - pre_count)
        new_end_idx = min(len(subtitles) - 1, core_end_idx + post_count)

        expanded_start = subtitles[new_start_idx]['start']
        expanded_end = subtitles[new_end_idx]['end']

        final_start = min(expanded_start, target_start)
        final_end = max(expanded_end, target_end)
        return final_start, final_end

    @staticmethod
    def auto_wrap_text(text, max_len):
        clean_text = text.replace('\r', '').replace('\n', '').replace('\\N', '')
        if len(clean_text) <= max_len:
            return clean_text
        result = []
        for i in range(0, len(clean_text), max_len):
            result.append(clean_text[i : i + max_len])
        return '\n'.join(result)

    def reformat_ass_file(self, file_path, max_len):
        if not os.path.exists(file_path):
            return

        s = self.config['subtitle']
        if s.get('orientation', 'horizontal') == 'vertical':
            current_res_x = 1080
            current_res_y = 1920
        else:
            current_res_x = 1920
            current_res_y = 1080

        def _make_style(name, primary, outline):
            return (
                f"Style: {name},{s['font_family']},{s['font_size']},"
                f"{primary},{primary},{outline},-1,"
                f"-1,0,0,0,100,100,0,0,1,{s['outline_width']},{s['shadow_depth']},2,10,10,{s['margin_v']},1\n"
            )

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        new_lines = []
        style_written = False
        for line in lines:
            if line.startswith('PlayResX:'):
                new_lines.append(f"PlayResX: {current_res_x}\n")
            elif line.startswith('PlayResY:'):
                new_lines.append(f"PlayResY: {current_res_y}\n")
            elif line.startswith('Style:') and not style_written:
                style_written = True
                new_lines.append(_make_style("Default", s['primary_color'], s['outline_color']))
                for m_name, m_primary, m_outline in SubtitleUtils.MEMBER_STYLES:
                    new_lines.append(_make_style(m_name, m_primary, m_outline))
            elif line.startswith('Style:'):
                continue
            elif line.startswith('Dialogue:'):
                parts = line.split(',', 9)
                if len(parts) == 10:
                    original_text = parts[9].strip()
                    wrapped_text = SubtitleUtils.auto_wrap_text(original_text, max_len)
                    final_text = wrapped_text.replace('\n', '\\N')
                    parts[9] = final_text + '\n'
                    new_lines.append(','.join(parts))
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.writelines(new_lines)

    def create_ass_file(self, subtitles, output_path, start_offset, end_offset, max_char_len):
        s = self.config['subtitle']

        if s.get('orientation', 'horizontal') == 'vertical':
            play_res_x = 1080
            play_res_y = 1920
        else:
            play_res_x = 1920
            play_res_y = 1080

        def _make_style(name, primary, outline):
            return (
                f"Style: {name},{s['font_family']},{s['font_size']},"
                f"{primary},{primary},{outline},-1,"
                f"-1,0,0,0,100,100,0,0,1,{s['outline_width']},{s['shadow_depth']},2,10,10,{s['margin_v']},1"
            )

        style_lines = [_make_style("Default", s['primary_color'], s['outline_color'])]
        for m_name, m_primary, m_outline in SubtitleUtils.MEMBER_STYLES:
            style_lines.append(_make_style(m_name, m_primary, m_outline))

        header = f"""[Script Info]
Title: Auto Clip
ScriptType: v4.00+
PlayResX: {play_res_x}
PlayResY: {play_res_y}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
""" + '\n'.join(style_lines) + f"""

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        clip_duration = end_offset - start_offset
        valid_count = 0

        for sub in subtitles:
            if sub['end'] > start_offset and sub['start'] < end_offset:
                rel_start = max(0, sub['start'] - start_offset)
                rel_end = min(clip_duration, sub['end'] - start_offset)
                start_str = SubtitleUtils.sec_to_ass_time(rel_start)
                end_str = SubtitleUtils.sec_to_ass_time(rel_end)
                
                raw_text = sub['text']
                style = "Default"
                # 检测 [发言人] 标签，应用成员专属样式
                import re as _re
                speaker_match = _re.match(r'\[(嘉然|贝拉|乃琳|心宜|思诺)\]\s*', raw_text)
                if speaker_match:
                    style = speaker_match.group(1)
                    raw_text = raw_text[speaker_match.end():]
                wrapped_text = SubtitleUtils.auto_wrap_text(raw_text, max_len=max_char_len)
                text = wrapped_text.replace('\n', '\\N')

                events.append(f"Dialogue: 0,{start_str},{end_str},{style},,0,0,0,,{text}")
                valid_count += 1
        
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            f.write(header + '\n'.join(events))
        return valid_count
