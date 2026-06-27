# ZhiJiangAutoClip 会话交接

## 项目概述

A-SOUL / 闪耀舞台 直播自动切片工具，带 tkinter GUI。输入 BV 号或拖入视频 → 自动下载/ASR 生成字幕 → 弹幕分析高光 → AI 生成标题 → ffmpeg 切片 + 封面。

**仓库**: https://github.com/AlpaCaoYT/ZhiJiangAutoClip
**核心文件**: `app_launcher.py` (~2240行), `Auto_clip.py`, `danmu_method/get_data_by_danmu.py`
**启动**: 双击 `run_app.bat`

## 当前状态（2026-06-27）

### 最近优化（2026-06-27）
- **字幕编辑器分批渲染**: 每批 60 条，`after()` 调度，进度标签实时显示，消除数百条字幕的 UI 卡死
- **精确模式前置校验**: 第3步前自动检测字幕是否有发言人标记，无标记则暂停 + 弹出编辑器
- **文件名智能归类**: `_organize_files` 优先从视频文件名检测成员名，心宜/思诺视频自动分到对应目录
- **浏览文件防错**: `_browse_file` 验证 target_dir 非空，不再触发完整 `_check_environment`（避免文件被移动）
- **日志复制增强**: `clipboard_clear` + `clipboard_append`，支持 Ctrl+C 和右键菜单
- **文件自由选择**: 字幕/弹幕路径旁增加「浏览」按钮，可手动选择文件并自动复制到素材目录
- **精确模式联动**: 选择「模式2 精确」自动开启分析暂停 + 弹出字幕发言人编辑器
- **防套娃路径**: BV 下载固定到顶层 `素材/`，`_organize_files` 仅在根目录触发
- **代码去重/清理**: SubtitleUtils 统一时间解析，`_setup_auto_clip_config()` 消除配置重复，移除死代码

### 已实现的核心功能
- **GUI 工作台**: 双模式（BV号/已有视频）+ 4步流程 + 一键运行 + 终止按钮
- **智能文件整理**: 按成员/CP/日期自动归类到 `素材/心宜/6月26日xxx/` 子文件夹
- **四级 ASR 链路**: 必剪(秒测) → faster-whisper GPU large-v3 → WhisperAPI
  - GPU: RTX 4070, CUDA, 模型存 `models/` 目录（G盘）
  - 自动繁→简转换（zhconv）
- **弹幕分析**: 弹幕密度 + DeepSeek AI 生成标题/摘要/封面文字
  - 滑动窗口 O(n) 算法
  - 5层 JSON 解析回退
  - 自动检测单播/双播/团播/枝江大团播，匹配对应提示词
- **双模式分析**:
  - 模式1: 模糊，不推测发言人
  - 模式2: 字幕发言人编辑器（逐条指定+成员配色+批量设置）
- **LLM 字幕校核**: 快速单次 API 调用修正成员名/术语
- **成员知识库**: 5位成员+CP+代表色，全部提示词严格对齐
- **故障诊断**: 11项检测 + 错误分类 + 修复建议

### 字幕颜色
| 嘉然 | 贝拉 | 乃琳 | 心宜 | 思诺 |
|------|------|------|------|------|
| #FF69B4 | #9B59B6 | #3498DB | #FF1493 | #EEA0D7 |

### 已安装依赖
- faster-whisper large-v3 (GPU float16)
- zhconv (繁→简)
- sv-ttk (暗色主题)
- nvidia-cublas-cu12 (GPU DLL)
- funasr/modelscope 未成功（需VS Build Tools编译editdistance，已从ASR链移除）

### 已知待修复
1. `素材/__no_danmaku__` 文件夹需手动删除（已从代码逻辑移除）
2. 必剪 Bcut ASR 仍不可用（B站API返回 `'data'` KeyError）
3. `.gitignore` 已覆盖 `素材/` `切片输出/` `models/` `crash_*.log`

### 隐私状态
- `app_config.json` 在 .gitignore，含 API Key 和 SESSDATA，未入仓
- `素材/` `切片输出/` `models/` 不入仓
- `app_config.example.json` 是模板文件（已入仓）

### 常用命令
```powershell
# 安装依赖（清华镜像）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 单独安装GPU支持
pip install nvidia-cublas-cu12 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 推送（强制）
git push --force origin master:main
```
