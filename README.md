# 2026.6.26 更新 — 软件化改造完成

## 当前状态

项目已从脚本集合改造为**带图形界面的桌面软件壳**。核心功能可用，后续方向是打磨体验 + 接入更完整的剪辑能力。

### 入口
- **Windows 双击 `run_app.bat` 启动**
- `app_launcher.py` 是主界面，tkinter + tkinterdnd2 构建

### 工作流（两种路径）
1. **BV 号下载**：填 BV 号 → yutto 下载视频+弹幕+字幕 → 字幕纠错 → 弹幕分析 → 自动切片
2. **已有视频**：拖视频到输入目录 → 必剪免费 ASR 生成字幕 → 字幕纠错 → 弹幕分析 → 自动切片
- 每个步骤有状态图标，失败会弹窗问跳过/重试/停止
- 必剪 ASR (`utils/bcut_asr.py`) 免费、无需 API Key、无需翻墙

### 关键依赖
- FFmpeg（系统安装）
- yutto（B站下载，`pip install yutto`）
- requests, Pillow, yt-dlp
- DeepSeek 官方 API（弹幕分析用，`deepseek-v4-pro`）

### 已做改动清单
1. `app_launcher.py` — 完整图形工作台（步骤流程、双路径、状态追踪、弹窗跳过、拖放入文件、日志写文件）
2. `run_app.bat` — Windows 双击启动，自动查找 Python
3. `utils/bcut_asr.py` — 必剪免费语音识别，直接嵌入项目
4. `core/subtitle_utils.py` — ASS 字幕内置 6 种成员样式（嘉然/贝拉/乃琳/心宜/思诺/ASOUL）
5. `danmu_method/get_data_by_danmu.py` — API 默认改为 DeepSeek 官方、UTF-8 编码
6. `Auto_clip.py` — 环境变量驱动路径
7. `utils/ASRCorrector.py` — 递归处理子目录
8. `utils/get_danmu.py` / `get_all.py` — 环境变量覆盖默认值
9. `requirements.txt` — 补充 yt-dlp
10. `app_config.json` — 自动保存/加载界面配置
11. `workspace/logs/` — 每次启动生成带时间戳的日志文件

### 待完善
- 窗口布局在小屏幕上可能偏大
- 下拉目录列表依赖手动刷新
- 必剪 ASR 偶尔有速率限制
- 弹幕分析的质量依赖 LLM API 配置和 Prompt

### 参考项目
- Kdenlive（多轨字幕编辑，已下载可配合使用）
- VideoCaptioner（已提取其必剪 ASR 模块嵌入）
- OpenCut（界面参考）

---

# 🎞️ A-SOUL 自动化切片工具 (Asoul-Auto-Clip)

![FFmpeg](https://img.shields.io/badge/Dependency-FFmpeg-green)
![License](https://img.shields.io/badge/license-MIT-orange)

> **极速切片，解放双手！专为 A-SOUL 切片设计的自动化生产线。**
> 
> 双击 `run_app.bat` 启动工作台，填入 BV 号或拖入视频，一键自动生成切片。

## ✨ 核心功能

*   **🖥️ 图形工作台**：`app_launcher.py` 提供完整 GUI，步骤清晰，状态可见
*   **🔽 一键下载**：填 BV 号自动下载 B站视频 + 弹幕 + 字幕（基于 yutto）
*   **🎙️ 免费 ASR**：内置必剪语音识别，无字幕视频也能自动生成字幕
*   **🧠 弹幕分析**：弹幕密度算法定位高光时刻 + DeepSeek API 生成标题文案
*   **🎨 多成员字幕**：ASS 字幕预置嘉然/贝拉/乃琳/心宜/思诺/ASOUL 专属配色
*   **🛠️ 配套工具**：字幕纠错字典、时间轴对齐、提示词模板编辑

---

## 📦 安装与环境配置

### 1. 系统依赖
必须安装 **FFmpeg** 并添加到 PATH：
- **Windows**: [下载 FFmpeg](https://ffmpeg.org/download.html) → 解压 → `bin` 目录加入系统环境变量

验证：终端输入 `ffmpeg -version` 不报错

### 2. Python 依赖
```bash
pip install -r requirements.txt
pip install yutto pydub tkinterdnd2
```

### 3. AI 接口（可选但推荐）
弹幕分析需要 DeepSeek API：
- 注册 [platform.deepseek.com](https://platform.deepseek.com) 获取 API Key
- 在工作台「高级配置」中填入，点「测试连接」验证

---

## 🚀 快速开始

### 方式一：BV 号全自动
1. 双击 `run_app.bat`
2. 选择「BV号下载」
3. 填入 B站视频 BV 号
4. 点「一键运行全部流程」
5. 切片输出在 `workspace/clip_output/`

### 方式二：已有视频
1. 把视频拖到工作台的拖放区
2. 选择「已有视频（必剪免费ASR）」
3. 点「一键运行全部流程」

### 用 Kdenlive 精修
生成切片后点「用 Kdenlive 打开」→ 导入视频和 ASS 字幕 → 在字幕管理器中给不同成员分配不同轨道和配色

---

## 📂 项目结构

```text
ASoulAutoClip/
├── app_launcher.py              # 🚀 图形工作台主入口
├── run_app.bat                  # Windows 双击启动
├── Auto_clip.py                 # 自动切片核心
├── Data_source.txt              # 剪辑片段元数据
├── requirements.txt             # Python 依赖
├── core/                        # 核心模块
│   ├── video_processor.py       # 视频处理
│   ├── subtitle_utils.py        # 字幕生成（含多成员样式）
│   ├── cover_generator.py       # 封面生成
│   └── ...
├── danmu_method/                # 弹幕分析
│   └── get_data_by_danmu.py     # 弹幕密度 + LLM 分析
├── prompt_method/               # LLM 提示词模板
├── utils/                       # 工具箱
│   ├── bcut_asr.py              # 必剪免费 ASR
│   ├── ASRCorrector.py          # 字幕纠错
│   ├── get_all.py               # B站下载器
│   ├── get_danmu.py             # 弹幕下载器
│   └── asr_dict.txt             # 纠错字典
├── assets/font/                 # 字体文件
└── workspace/
    ├── video_input/             # 素材目录
    ├── clip_output/             # 切片输出
    └── logs/                    # 运行日志
```

---

## 📂 项目结构

```text
ASoulAutoClip/
├── assets/                       # 静态资源 (字体、图片素材)
├── danmu_method/                 # [核心] 弹幕分析算法模块
├── prompt_method/                # [核心] LLM 提示词模板
├── utils/                        # 工具箱
│   ├── ASRCorrector.py           # 字幕纠错工具
│   ├── get_danmu.py              # 弹幕下载器
│   ├── edit_data_source.py       # 时间轴对齐工具
│   ├── get_font_family_name.py   # 获取字体家族名称，用于填入主程序
|   └── asr_dict.txt              # 字幕纠错字典
├── workspace/                    # 工作区
│   ├── clip_output/              # 剪辑片段输出
|   └── video_input/              # 放入视频、字幕、弹幕文件等素材
├── Auto_clip.py                  # 🚀 主程序入口
├── Data_source.txt               # [数据] 剪辑片段元数据
├── requirements.txt              # Python 依赖
└── README.md                     # 说明文档
```

---

## 🚀 使用指南 (Workflow)

### 第一步：素材准备

运行工具前，请确保以下文件已就位：
1.  **录播视频文件**（完整视频）
2.  **字幕文件**（`.srt` 或 `.txt`）
3.  **元数据文件**（`Data_source.txt`）

#### 1. 视频下载
推荐使用以下工具获取 Bilibili 录播视频：
- [SnapAny](https://snapany.com/zh/bilibili) / [效率坊](https://www.xiaolvfang.com/) / [ShowBL](https://www.showbl.com/lab/bilibili/) / [kedou](https://www.kedou.life/extract/bilibili)
- 或者使用 [B站录播姬](https://github.com/Bililive/BililiveRecorder) 自行录制。

#### 2. 字幕下载与处理
推荐使用 **vCaptions** 插件下载字幕：
- [Edge 插件下载](https://microsoftedge.microsoft.com/addons/detail/vcaptions-%E7%BB%99%E4%BB%BB%E6%84%8F%E7%BD%91%E7%AB%99%E8%A7%86%E9%A2%91%E6%B7%BB%E5%8A%A0%E5%AD%97%E5%B9%95%E5%88%97%E8%A1%A8/lignnlhlpiefmcjkdkmfjdckhlaiajan?hl=zh-CN)
- [Chrome 插件下载](https://chromewebstore.google.com/detail/vcaptions-%E7%BB%99%E4%BB%BB%E6%84%8F%E7%BD%91%E7%AB%99%E8%A7%86%E9%A2%91%E6%B7%BB%E5%8A%A0%E5%AD%97%E5%B9%95%E5%88%97%E8%A1%A8/bciglihaegkdhoogebcdblfhppoilclp?hl=zh-CN&utm_source=ext_sidebar)

或者使用在线提取：[飞鱼多字幕工具](https://www.feiyudo.com/caption/subtitle/bilibili)

> **⚠️ 注意**：获取字幕后，请务必运行 `utils/ASRCorrector.py` 对字幕进行自动纠错，以提高识别准确率。

---

### 第二步：生成高光片段元数据 (核心)

你需要将高光时刻的元数据填入 `Data_source.txt`。本仓库提供两种自动化生成方法：

#### 📊 方法对比

| 特性 | 方法一：LLM 提示词法 | 方法二：弹幕热度法 |
| :--- | :--- | :--- |
| **原理** | 依靠直播字幕 + 大模型语义理解 | 依靠弹幕密度波峰 + 字幕辅助 |
| **优点** | **无需接口**，可利用 Gemini/GPT 高级推理能力；<br>适用范围广（任意视频）。 | **客观真实**，反映观众实时反应；<br>全自动化，无需手动提问。 |
| **缺点** | 依赖字幕质量；无法识别纯画面/动作梗。 | 必须有大量弹幕（仅限官方录播）；<br>需要调用 LLM API (消耗 Token)。 |
| **适用场景**| 字幕清晰、对话为主的直播 | 官方大型直播、弹幕互动多的场次 |

#### 📥 `Data_source.txt` 数据格式示例
无论使用哪种方法，最终填入的数据格式必须如下：

```json
[
  {
    "timestamp": "00:49:52-00:50:16",
    "title": "破防了！嘉然自曝演唱会蹦迪因身高太矮被淹没",
    "summary": "嘉然分享独自看演唱会的尴尬经历...",
    "cover_text_1": "站起也被淹没",
    "cover_text_2": "警告一次",
    "highlight_reason": "嘉然自嘲身高梗，节目效果强烈。"
  }
]
```

#### 👉 操作流程

**方法一：LLM 提示词法 (prompt_method)**
1.  找到 `prompt_method` 文件夹。
2.  将**纠错后的字幕文件**作为附件，配合对应的 Prompt 发送给高级大模型（推荐 GPT-5, Claude 4.5, Gemini 3.0 Pro, 豆包等）。
3.  将模型生成的 JSON 数据复制到 `Data_source.txt`。

**方法二：弹幕热度法 (danmu_method)**
1.  获取直播弹幕：
    *   运行 `utils/get_danmu.py` 下载。
    *   或者使用其他方法，用第三方工具转换弹幕格式（如 XML 格式需转换为 ASS 格式，[转换工具](https://tiansh.github.io/us-danmaku/bilibili/)）。
2.  将 `直播弹幕.ass` 和 `字幕.srt` 放入视频同级目录。
3.  配置并运行 `danmu_method/get_data_by_danmu.py`，程序将自动填充 `Data_source.txt`。

 
> **💡 进阶技巧：官方弹幕 + 非官方视频**
> 如果你想利用官方录播的弹幕热度数据，来剪辑非官方录播的视频（通常存在时间偏差），请在生成数据后额外执行一步：
>
> 运行脚本：`utils/edit_data_source_timestep.py`
>
> **作用**：该脚本会自动修正 `Data_source.txt` 中的时间戳，将其从官方录播时间对齐到你下载的非官方视频时间轴。

---

### 第三步：运行主程序

1.  打开 `Auto_clip.py`，根据注释填写相关文件路径配置。
2.  运行程序。
3.  等待输出文件夹中生成切片视频、切片封面 (10个切片大约耗时2分钟)。

> **提示**：如果对结果不满意，可手动微调 `Data_source.txt` 中的标题或封面内容，再次运行脚本即可。
另外，如果视频中有字幕错误，可以手动在输出文件夹中的 `[相应切片标题].ass` 文件中修改字幕，再次运行脚本即可。

---

## 🔗 传送门 (Resources)

为了方便获取素材，这里整理了常用链接：

### 官方录播源
*   [嘉然 (Diana)](https://space.bilibili.com/672328094/lists/222940?type=series)
*   [贝拉 (Bella)](https://space.bilibili.com/672353429/lists/222938?type=series)
*   [乃琳 (Eileen)](https://space.bilibili.com/672342685/lists/222754?type=series)
*   [心宜 (fiona)](https://space.bilibili.com/3537115310721181/lists/3698069?type=series)
*   [思诺 (gladys)](https://space.bilibili.com/3537115310721781/lists/3692011?type=series)

### 非官方录播
*   [A-SOUL二创计画](https://space.bilibili.com/547510303/upload/video)
*   [奶淇琳周报](https://space.bilibili.com/1729236416/upload/video) | [贝极星周报](https://space.bilibili.com/2114847153/upload/video) | [嘉心糖周报](https://space.bilibili.com/247210788/upload/video)
*   [地海菠萝](https://space.bilibili.com/165364/upload/video) | [天神白娅](https://space.bilibili.com/12416994/upload/video)

---


## ⚠️ 免责声明 (Disclaimer)

1.  本项目为粉丝自制开源工具，**非 A-SOUL 官方项目**。
2.  生成的视频素材版权归 **A-SOUL** 所有。
3.  请在使用本工具进行二创投稿时，遵守 Bilibili 社区规范及 A-SOUL 二创公约。
4.  本项目禁止用于任何商业盈利目的。

---

## 🤝 贡献与支持

欢迎提交 Issue 或 Pull Request！
如果这个项目帮到了你，请给一个 Star ⭐️ 鼓励一下！

---
## 👤 作者
**救一人为侠**  
Bilibili: [点击主页](https://space.bilibili.com/667041249)
