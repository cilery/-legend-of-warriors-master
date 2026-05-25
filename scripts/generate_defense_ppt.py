#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generate a graduation defense PPTX aligned with the final thesis content.

This script uses only the Python standard library and writes a minimal OOXML
PowerPoint package, so it does not depend on python-pptx.
"""

from __future__ import annotations

import html
import os
import struct
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from xml.etree import ElementTree as ET


EMU_PER_INCH = 914400
SLIDE_W = 12192000  # 13.333 in, 16:9
SLIDE_H = 6858000   # 7.5 in, 16:9
XMLNS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
XMLNS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XMLNS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"
DCMITYPE_NS = "http://purl.org/dc/dcmitype/"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
DERMS_NS = "http://purl.org/dc/terms/"

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "基于Unity的冒险探索RPG游戏设计与实现-毕业答辩PPT-候磊.pptx"

THESIS_TITLE = "基于Unity的冒险探索RPG游戏设计与实现"
SUBJECT_LINE = "Unity 2022.3 LTS  ·  2D Adventure RPG  ·  毕业论文答辩"
AUTHOR_LINE = "答辩人：候磊    专业：计算机科学与技术    学号：202214070203"

COLORS = {
    "bg_dark": "0B1120",
    "bg_light": "F8FAFC",
    "card": "FFFFFF",
    "card_alt": "F1F5F9",
    "border": "D7E0EA",
    "accent": "0EA5E9",
    "accent_dark": "082F49",
    "accent_soft": "E0F2FE",
    "green": "10B981",
    "amber": "F59E0B",
    "indigo": "4F46E5",
    "red": "EF4444",
    "text": "0F172A",
    "muted": "475569",
    "muted_light": "94A3B8",
    "white": "FFFFFF",
}

FONT_LATIN = "Calibri"
FONT_EA = "Microsoft YaHei"
FONT_CS = "Arial"


@dataclass
class TextLine:
    text: str
    size: int = 20
    color: str = COLORS["text"]
    bold: bool = False
    align: str = "l"


@dataclass
class Element:
    kind: str
    x: int
    y: int
    w: int
    h: int
    name: str = ""
    fill: Optional[str] = None
    line: Optional[str] = None
    line_width: int = 12700
    geom: str = "rect"
    lines: List[TextLine] = field(default_factory=list)
    path: Optional[Path] = None
    valign: str = "t"
    margin: Tuple[int, int, int, int] = (91440, 91440, 45720, 45720)


@dataclass
class Slide:
    title: str
    bg: str = COLORS["bg_light"]
    elements: List[Element] = field(default_factory=list)


def emu(inches: float) -> int:
    return int(round(inches * EMU_PER_INCH))


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def png_size(path: Path) -> Tuple[int, int]:
    with path.open("rb") as fh:
        header = fh.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Unsupported PNG image")
    return struct.unpack(">II", header[16:24])


def jpeg_size(path: Path) -> Tuple[int, int]:
    with path.open("rb") as fh:
        data = fh.read()
    if data[:2] != b"\xff\xd8":
        raise ValueError("Unsupported JPEG image")
    idx = 2
    while idx < len(data):
        while idx < len(data) and data[idx] == 0xFF:
            idx += 1
        if idx >= len(data):
            break
        marker = data[idx]
        idx += 1
        if marker in (0xD8, 0xD9):
            continue
        if idx + 2 > len(data):
            break
        seg_len = struct.unpack(">H", data[idx:idx + 2])[0]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            if idx + 7 > len(data):
                break
            height = struct.unpack(">H", data[idx + 3:idx + 5])[0]
            width = struct.unpack(">H", data[idx + 5:idx + 7])[0]
            return width, height
        idx += seg_len
    raise ValueError("Could not read JPEG size")


def image_size(path: Path) -> Tuple[int, int]:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return png_size(path)
    if suffix in (".jpg", ".jpeg"):
        return jpeg_size(path)
    raise ValueError("Unsupported image type: %s" % path.suffix)


def fit_image(path: Path, box_x: int, box_y: int, box_w: int, box_h: int, padding: int = emu(0.10)) -> Tuple[int, int, int, int]:
    img_w, img_h = image_size(path)
    usable_w = max(box_w - padding * 2, emu(0.2))
    usable_h = max(box_h - padding * 2, emu(0.2))
    ratio = min(usable_w / img_w, usable_h / img_h)
    draw_w = int(round(img_w * ratio))
    draw_h = int(round(img_h * ratio))
    draw_x = box_x + (box_w - draw_w) // 2
    draw_y = box_y + (box_h - draw_h) // 2
    return draw_x, draw_y, draw_w, draw_h


def text_box(x: int, y: int, w: int, h: int, lines: Sequence[TextLine], fill: Optional[str] = None,
             line: Optional[str] = None, geom: str = "rect", name: str = "TextBox",
             valign: str = "t", margin: Tuple[int, int, int, int] = (91440, 91440, 45720, 45720)) -> Element:
    return Element(kind="textbox", x=x, y=y, w=w, h=h, fill=fill, line=line, geom=geom, name=name,
                   lines=list(lines), valign=valign, margin=margin)


def shape_box(x: int, y: int, w: int, h: int, fill: str, line: Optional[str] = None, geom: str = "rect",
              name: str = "Shape") -> Element:
    return Element(kind="shape", x=x, y=y, w=w, h=h, fill=fill, line=line, geom=geom, name=name)


def picture(path: Path, x: int, y: int, w: int, h: int, name: str = "Picture") -> Element:
    return Element(kind="picture", x=x, y=y, w=w, h=h, path=path, name=name)


def add_standard_chrome(slide: Slide, page_no: int) -> None:
    slide.elements.append(shape_box(emu(0.55), emu(0.40), emu(0.14), emu(0.56), COLORS["accent"], name="Accent"))
    slide.elements.append(text_box(
        emu(0.78), emu(0.30), emu(7.3), emu(0.72),
        [TextLine(slide.title, size=28, bold=True)],
        name="SlideTitle",
        margin=(0, 0, 0, 0),
    ))
    slide.elements.append(text_box(
        emu(9.35), emu(0.36), emu(3.35), emu(0.28),
        [TextLine("毕业论文答辩  |  Unity 2D Adventure RPG", size=11, color=COLORS["muted"], align="r")],
        name="TopRight",
        margin=(0, 0, 0, 0),
    ))
    slide.elements.append(shape_box(emu(0.55), emu(7.05), emu(12.10), emu(0.018), COLORS["border"], name="FooterLine"))
    slide.elements.append(text_box(
        emu(12.25), emu(7.07), emu(0.35), emu(0.18),
        [TextLine(str(page_no), size=11, color=COLORS["muted_light"], align="r")],
        name="PageNo",
        margin=(0, 0, 0, 0),
    ))


def add_image_card(slide: Slide, frame_x: int, frame_y: int, frame_w: int, frame_h: int, image_path: Path,
                   caption: Optional[str] = None) -> None:
    slide.elements.append(shape_box(frame_x, frame_y, frame_w, frame_h, COLORS["card"], COLORS["border"], name="ImageFrame"))
    ix, iy, iw, ih = fit_image(image_path, frame_x, frame_y, frame_w, frame_h - (emu(0.28) if caption else 0))
    slide.elements.append(picture(image_path, ix, iy, iw, ih))
    if caption:
        slide.elements.append(text_box(
            frame_x + emu(0.12), frame_y + frame_h - emu(0.26), frame_w - emu(0.24), emu(0.16),
            [TextLine(caption, size=11, color=COLORS["muted"], align="c")],
            name="ImageCaption",
            margin=(0, 0, 0, 0),
        ))


def build_slides() -> List[Slide]:
    img_use_case = ROOT / "系统功能用例图_优化版_紧凑裁剪版.png"
    img_flow = ROOT / "系统总体流程图_论文风格_优化版.png"
    img_data = ROOT / "数据管理UML类图_黑白论文版.png"
    img_ui = ROOT / "UI界面交互UML顺序图_最终无交叉版.png"
    img_scene = ROOT / "场景管理系统顺序图_黑白论文版.png"
    img_anim = ROOT / "动画管理活动图_黑白论文版.png"
    img_camera = ROOT / "角色镜头相机控制_UML时序图_最终版.png"

    needed = [img_use_case, img_flow, img_data, img_ui, img_scene, img_anim, img_camera]
    missing = [str(p) for p in needed if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing required images:\n" + "\n".join(missing))

    slides: List[Slide] = []

    # Slide 1: cover
    s1 = Slide(title=THESIS_TITLE, bg=COLORS["bg_dark"])
    s1.elements.extend([
        shape_box(emu(0.75), emu(0.85), emu(1.75), emu(0.42), COLORS["accent_dark"], geom="roundRect", name="CoverTag"),
        text_box(emu(0.75), emu(0.85), emu(1.75), emu(0.42), [TextLine("毕业论文答辩", size=16, color=COLORS["white"], bold=True, align="c")],
                 name="CoverTagText", valign="ctr"),
        text_box(
            emu(0.82), emu(1.55), emu(8.0), emu(1.65),
            [
                TextLine("基于Unity的冒险探索", size=30, color=COLORS["white"], bold=True),
                TextLine("RPG游戏设计与实现", size=30, color=COLORS["white"], bold=True),
            ],
            name="CoverTitle",
            margin=(0, 0, 0, 0),
        ),
        text_box(
            emu(0.85), emu(3.40), emu(6.50), emu(0.34),
            [TextLine(SUBJECT_LINE, size=14, color="C7D2FE")],
            name="CoverSubtitle",
            margin=(0, 0, 0, 0),
        ),
        shape_box(emu(0.82), emu(4.70), emu(5.70), emu(1.25), "111827", COLORS["accent"], geom="roundRect", name="InfoCard"),
        text_box(
            emu(1.00), emu(4.98), emu(5.30), emu(0.75),
            [
                TextLine(AUTHOR_LINE, size=16, color=COLORS["white"], bold=True),
                TextLine("核心内容：角色控制 / 战斗交互 / 场景管理 / 数据持久化 / UI与动画", size=13, color="CBD5E1"),
            ],
            name="AuthorInfo",
        ),
        shape_box(emu(9.70), emu(0.88), emu(2.45), emu(5.35), COLORS["accent"], name="CoverAccent1"),
        shape_box(emu(10.10), emu(1.25), emu(1.65), emu(4.60), COLORS["bg_dark"], name="CoverAccent2"),
        text_box(emu(9.90), emu(1.55), emu(1.95), emu(0.52), [TextLine("Unity 2022.3", size=16, color=COLORS["white"], bold=True, align="c")],
                 fill=COLORS["accent_dark"], geom="roundRect", name="Badge1", valign="ctr"),
        text_box(emu(9.90), emu(2.35), emu(1.95), emu(0.52), [TextLine("FSM + Animator", size=16, color=COLORS["white"], bold=True, align="c")],
                 fill=COLORS["green"], geom="roundRect", name="Badge2", valign="ctr"),
        text_box(emu(9.90), emu(3.15), emu(1.95), emu(0.52), [TextLine("Addressables", size=16, color=COLORS["white"], bold=True, align="c")],
                 fill=COLORS["amber"], geom="roundRect", name="Badge3", valign="ctr"),
        text_box(emu(9.90), emu(3.95), emu(1.95), emu(0.52), [TextLine("Cinemachine", size=16, color=COLORS["white"], bold=True, align="c")],
                 fill=COLORS["indigo"], geom="roundRect", name="Badge4", valign="ctr"),
        text_box(emu(9.90), emu(4.75), emu(1.95), emu(0.52), [TextLine("DOTween", size=16, color=COLORS["white"], bold=True, align="c")],
                 fill=COLORS["red"], geom="roundRect", name="Badge5", valign="ctr"),
    ])
    slides.append(s1)

    # Slide 2
    s2 = Slide(title="选题背景与研究意义")
    add_standard_chrome(s2, 2)
    s2.elements.extend([
        text_box(
            emu(0.75), emu(1.22), emu(7.20), emu(4.95),
            [
                TextLine("• 游戏产业持续增长，RPG依靠叙事、探索与成长体验，长期保持较强的玩家吸引力。", size=20),
                TextLine("• Unity 具备跨平台、组件化开发和成熟插件生态，适合中小型团队快速构建完整玩法原型。", size=20),
                TextLine("• 本课题以 2D 冒险探索 RPG 为对象，重点验证角色控制、战斗反馈、场景切换、数据持久化与界面交互的协同实现。", size=20),
                TextLine("• 论文既关注功能落地，也强调工程实践价值，为后续同类项目提供可复用的轻量化设计思路。", size=20),
            ],
            fill=COLORS["card"], line=COLORS["border"], geom="roundRect", name="MeaningBox"
        ),
        text_box(
            emu(8.25), emu(1.28), emu(4.15), emu(1.20),
            [TextLine("技术价值", size=18, color=COLORS["accent_dark"], bold=True),
             TextLine("整合 FSM、Animator、Addressables、Cinemachine、DOTween 等核心技术栈。", size=14, color=COLORS["muted"])],
            fill=COLORS["accent_soft"], line=COLORS["border"], geom="roundRect", name="Value1"
        ),
        text_box(
            emu(8.25), emu(2.82), emu(4.15), emu(1.20),
            [TextLine("实践价值", size=18, color=COLORS["green"], bold=True),
             TextLine("完成从需求分析、系统设计到实现测试的完整毕业设计流程。", size=14, color=COLORS["muted"])],
            fill="ECFDF5", line=COLORS["border"], geom="roundRect", name="Value2"
        ),
        text_box(
            emu(8.25), emu(4.36), emu(4.15), emu(1.20),
            [TextLine("应用价值", size=18, color=COLORS["amber"], bold=True),
             TextLine("形成可运行的 2D RPG 原型，为后续关卡扩展、内容迭代和教学展示提供基础。", size=14, color=COLORS["muted"])],
            fill="FFFBEB", line=COLORS["border"], geom="roundRect", name="Value3"
        ),
    ])
    slides.append(s2)

    # Slide 3
    s3 = Slide(title="研究目标与论文内容")
    add_standard_chrome(s3, 3)
    s3.elements.append(text_box(
        emu(0.75), emu(1.20), emu(5.20), emu(5.10),
        [
            TextLine("研究主线", size=18, color=COLORS["accent_dark"], bold=True),
            TextLine("• 按照“需求分析—总体设计—模块实现—测试验证”的主线展开。", size=18),
            TextLine("• 围绕角色控制、战斗、动画、场景/资源、UI、数据六大核心模块组织论文内容。", size=18),
            TextLine("• 最终形成从主菜单进入、场景探索、敌人战斗到存档读档的完整闭环。", size=18),
            TextLine("• 论文共七章，覆盖相关技术、系统设计、模块实现与测试结论。", size=18),
        ],
        fill=COLORS["card"], line=COLORS["border"], geom="roundRect", name="ResearchBox"
    ))
    add_image_card(s3, emu(6.25), emu(1.20), emu(6.10), emu(5.10), img_use_case, "系统功能用例图")
    slides.append(s3)

    # Slide 4
    s4 = Slide(title="系统总体架构与功能模块")
    add_standard_chrome(s4, 4)
    s4.elements.append(text_box(
        emu(0.75), emu(1.20), emu(4.95), emu(5.10),
        [
            TextLine("分层架构", size=18, color=COLORS["accent_dark"], bold=True),
            TextLine("• 界面与交互层：主菜单、状态显示、暂停与设置反馈。", size=18),
            TextLine("• 流程控制层：主流程调度、场景进入/退出与事件联动。", size=18),
            TextLine("• 核心逻辑层：角色控制、敌人 AI、战斗、动画与相机。", size=18),
            TextLine("• 数据与状态层：运行时状态、场景配置与持久化存档。", size=18),
            TextLine("• 模块间通过事件、接口与统一数据对象协同，体现高内聚、低耦合的设计原则。", size=18),
        ],
        fill=COLORS["card"], line=COLORS["border"], geom="roundRect", name="ArchBox"
    ))
    add_image_card(s4, emu(5.95), emu(1.20), emu(6.40), emu(4.25), img_flow, "系统总体流程图")
    chip_y = emu(5.70)
    chip_w = emu(1.85)
    for idx, (label, color) in enumerate([
        ("角色控制", COLORS["accent"]),
        ("战斗交互", COLORS["green"]),
        ("场景管理", COLORS["amber"]),
        ("数据管理", COLORS["indigo"]),
        ("UI 系统", COLORS["red"]),
        ("动画管理", "0F766E"),
    ]):
        x = emu(0.82) + idx * emu(1.98)
        s4.elements.append(text_box(
            x, chip_y, chip_w, emu(0.46),
            [TextLine(label, size=15, color=COLORS["white"], bold=True, align="c")],
            fill=color, geom="roundRect", name="Chip%d" % (idx + 1), valign="ctr",
            margin=(0, 0, 0, 0),
        ))
    slides.append(s4)

    # Slide 5
    s5 = Slide(title="关键技术与开发环境")
    add_standard_chrome(s5, 5)
    card_specs = [
        ("Unity 2022.3 LTS", "提供场景编辑、组件系统与跨平台开发基础。", COLORS["accent_soft"], COLORS["accent_dark"]),
        ("FSM + Animator", "负责玩家与敌人的状态切换及动画同步。", "ECFDF5", COLORS["green"]),
        ("Rigidbody2D / Collider2D", "用于移动控制、碰撞检测与攻击命中判定。", "FFFBEB", COLORS["amber"]),
        ("Addressables", "完成场景资源打包、异步加载与切换管理。", "EEF2FF", COLORS["indigo"]),
        ("Cinemachine + DOTween", "实现镜头跟随、震动反馈和淡入淡出过渡。", "FEF2F2", COLORS["red"]),
        ("JSON + Newtonsoft.Json", "实现存档读档与关键运行数据恢复。", "F0FDFA", "0F766E"),
    ]
    for idx, (title, body, fill, title_color) in enumerate(card_specs):
        row = idx // 3
        col = idx % 3
        x = emu(0.82) + col * emu(4.12)
        y = emu(1.35) + row * emu(2.18)
        s5.elements.append(text_box(
            x, y, emu(3.72), emu(1.65),
            [TextLine(title, size=18, color=title_color, bold=True),
             TextLine(body, size=14, color=COLORS["muted"])],
            fill=fill, line=COLORS["border"], geom="roundRect", name="TechCard%d" % (idx + 1)
        ))
    s5.elements.append(text_box(
        emu(0.82), emu(5.85), emu(11.35), emu(0.55),
        [TextLine("开发环境：Unity 2022.3 LTS  +  C#  +  Visual Studio 2022", size=16, color=COLORS["muted"], align="c")],
        fill=COLORS["card_alt"], line=COLORS["border"], geom="roundRect", name="EnvCard", valign="ctr",
        margin=(0, 0, 0, 0),
    ))
    slides.append(s5)

    # Slide 6
    s6 = Slide(title="角色控制与战斗系统实现")
    add_standard_chrome(s6, 6)
    s6.elements.append(text_box(
        emu(0.75), emu(1.18), emu(5.10), emu(5.08),
        [
            TextLine("核心实现", size=18, color=COLORS["accent_dark"], bold=True),
            TextLine("• 玩家状态机覆盖待机、移动、跳跃、攻击、技能、受击、死亡等核心状态。", size=18),
            TextLine("• 敌人围绕巡逻、转向、受击、死亡等状态切换，保证行为逻辑清晰。", size=18),
            TextLine("• 攻击命中后完成伤害结算、无敌帧控制、击退反馈，并叠加停顿帧与镜头震动强化打击感。", size=18),
            TextLine("• 通过 Animator 参数与脚本状态协同，实现“输入—逻辑—动画—反馈”统一响应。", size=18),
        ],
        fill=COLORS["card"], line=COLORS["border"], geom="roundRect", name="CombatBox"
    ))
    add_image_card(s6, emu(6.08), emu(1.18), emu(6.25), emu(4.55), img_camera, "角色镜头相机控制 UML 时序图")
    s6.elements.append(text_box(
        emu(6.08), emu(5.90), emu(6.25), emu(0.40),
        [TextLine("状态关键词：待机 / 移动 / 跳跃 / 攻击 / 技能 / 受击 / 死亡", size=14, color=COLORS["accent_dark"], align="c")],
        fill=COLORS["accent_soft"], line=COLORS["border"], geom="roundRect", name="StateStrip", valign="ctr",
        margin=(0, 0, 0, 0),
    ))
    slides.append(s6)

    # Slide 7
    s7 = Slide(title="场景管理与地图探索流程")
    add_standard_chrome(s7, 7)
    s7.elements.append(text_box(
        emu(0.75), emu(1.18), emu(5.05), emu(5.10),
        [
            TextLine("实现思路", size=18, color=COLORS["accent_dark"], bold=True),
            TextLine("• 通过 SceneLoadEventSO 统一发起场景切换请求，避免对象直接耦合底层加载接口。", size=18),
            TextLine("• SceneLoader 负责旧场景卸载、黑幕淡入淡出、异步加载与出生点重定位。", size=18),
            TextLine("• 结合 Addressables 与传送点机制，实现菜单场景与关卡区域之间的平滑流转。", size=18),
            TextLine("• 地图基于 Grid + Tilemap 构建，支撑探索、碰撞边界和区域推进。", size=18),
        ],
        fill=COLORS["card"], line=COLORS["border"], geom="roundRect", name="SceneBox"
    ))
    add_image_card(s7, emu(6.00), emu(1.18), emu(6.33), emu(5.10), img_scene, "场景管理系统 UML 顺序图")
    slides.append(s7)

    # Slide 8
    s8 = Slide(title="数据管理与存档读档设计")
    add_standard_chrome(s8, 8)
    s8.elements.append(text_box(
        emu(0.75), emu(1.18), emu(5.00), emu(4.35),
        [
            TextLine("组织方式", size=18, color=COLORS["accent_dark"], bold=True),
            TextLine("• 采用“统一数据对象 + 统一管理器 + 接口注册”的组织方式。", size=18),
            TextLine("• 重点保存场景 ID、角色位置、生命值以及部分对象状态。", size=18),
            TextLine("• 保存时统一采集对象状态，序列化为 JSON；读取时恢复角色与场景关键数据。", size=18),
            TextLine("• 通过数据分层区分静态配置、运行时状态与持久化存档，降低模块耦合。", size=18),
        ],
        fill=COLORS["card"], line=COLORS["border"], geom="roundRect", name="DataBox"
    ))
    s8.elements.append(text_box(
        emu(0.75), emu(5.72), emu(5.00), emu(0.55),
        [TextLine("三层数据架构：静态资源/场景配置  ·  运行时状态  ·  持久化存档", size=15, color=COLORS["accent_dark"], align="c")],
        fill=COLORS["accent_soft"], line=COLORS["border"], geom="roundRect", name="DataStrip", valign="ctr",
        margin=(0, 0, 0, 0),
    ))
    add_image_card(s8, emu(6.05), emu(1.18), emu(6.28), emu(5.10), img_data, "数据管理 UML 类图")
    slides.append(s8)

    # Slide 9
    s9 = Slide(title="UI 交互与动画表现")
    add_standard_chrome(s9, 9)
    s9.elements.append(text_box(
        emu(0.75), emu(1.18), emu(4.80), emu(5.10),
        [
            TextLine("表现层设计", size=18, color=COLORS["accent_dark"], bold=True),
            TextLine("• UGUI 构建主菜单、暂停界面、状态显示与设置交互。", size=18),
            TextLine("• PlayerAnimation、HurtAnimation 等脚本根据状态参数驱动 Animator 播放。", size=18),
            TextLine("• DOTween 负责黑幕过渡与界面渐变，保证场景切换和界面反馈更流畅。", size=18),
            TextLine("• UI、动画与逻辑模块通过事件与状态同步，提升操作响应和沉浸感。", size=18),
        ],
        fill=COLORS["card"], line=COLORS["border"], geom="roundRect", name="UIBox"
    ))
    add_image_card(s9, emu(5.78), emu(1.18), emu(6.55), emu(2.40), img_ui, "UI 界面交互 UML 顺序图")
    add_image_card(s9, emu(5.78), emu(3.88), emu(6.55), emu(2.40), img_anim, "动画管理活动图")
    slides.append(s9)

    # Slide 10
    s10 = Slide(title="系统测试与结果分析")
    add_standard_chrome(s10, 10)
    table_x = emu(0.85)
    table_y = emu(1.35)
    col1_w = emu(3.55)
    col2_w = emu(7.70)
    row_h = emu(0.63)
    s10.elements.append(shape_box(table_x, table_y, col1_w, row_h, COLORS["accent_dark"], name="Head1"))
    s10.elements.append(shape_box(table_x + col1_w, table_y, col2_w, row_h, COLORS["accent_dark"], name="Head2"))
    s10.elements.append(text_box(table_x, table_y, col1_w, row_h, [TextLine("测试项目", size=17, color=COLORS["white"], bold=True, align="c")],
                                 name="HeadText1", valign="ctr", margin=(0, 0, 0, 0)))
    s10.elements.append(text_box(table_x + col1_w, table_y, col2_w, row_h, [TextLine("测试结果", size=17, color=COLORS["white"], bold=True, align="c")],
                                 name="HeadText2", valign="ctr", margin=(0, 0, 0, 0)))
    rows = [
        ("主菜单与 UI 联动", "开始游戏、暂停、继续、返回主菜单等流程能够正常触发。"),
        ("角色移动与跳跃", "状态切换稳定，角色移动、跳跃和落地动画衔接正常。"),
        ("普通攻击与技能释放", "命中判定有效，伤害与受击反馈能够正确触发。"),
        ("敌人 AI 与死亡流程", "巡逻、转向、受击与死亡状态切换基本正常。"),
        ("场景切换", "传送、加载、卸载与出生点重定位形成闭环。"),
        ("存档与读档", "能够恢复场景、角色位置和生命值等关键数据。"),
    ]
    for idx, (left, right) in enumerate(rows):
        y = table_y + row_h + idx * row_h
        fill = COLORS["card"] if idx % 2 == 0 else COLORS["card_alt"]
        s10.elements.append(shape_box(table_x, y, col1_w, row_h, fill, COLORS["border"], name="RowL%d" % idx))
        s10.elements.append(shape_box(table_x + col1_w, y, col2_w, row_h, fill, COLORS["border"], name="RowR%d" % idx))
        s10.elements.append(text_box(table_x + emu(0.12), y + emu(0.06), col1_w - emu(0.24), row_h - emu(0.12),
                                     [TextLine(left, size=16, color=COLORS["text"], bold=True)],
                                     name="RowLT%d" % idx, margin=(0, 0, 0, 0)))
        s10.elements.append(text_box(table_x + col1_w + emu(0.12), y + emu(0.06), col2_w - emu(0.24), row_h - emu(0.12),
                                     [TextLine(right, size=15, color=COLORS["muted"])],
                                     name="RowRT%d" % idx, margin=(0, 0, 0, 0)))
    s10.elements.append(text_box(
        emu(0.85), emu(6.10), emu(11.25), emu(0.58),
        [TextLine("测试结论：论文涉及的各核心模块均能完成预期基本功能，系统原型具备稳定的主流程闭环。", size=16, color=COLORS["accent_dark"], bold=True, align="c")],
        fill=COLORS["accent_soft"], line=COLORS["border"], geom="roundRect", name="TestSummary", valign="ctr",
        margin=(0, 0, 0, 0),
    ))
    slides.append(s10)

    # Slide 11
    s11 = Slide(title="结论与后续展望")
    add_standard_chrome(s11, 11)
    s11.elements.append(text_box(
        emu(0.85), emu(1.40), emu(5.55), emu(4.80),
        [
            TextLine("研究结论", size=20, color=COLORS["accent_dark"], bold=True),
            TextLine("• 完成基于 Unity 的 2D 冒险探索 RPG 原型设计与实现。", size=18),
            TextLine("• 验证了模块化架构在角色控制、战斗、场景与数据管理中的可行性。", size=18),
            TextLine("• 测试结果表明系统在主流程、交互联动和存档恢复方面具有较好稳定性。", size=18),
        ],
        fill=COLORS["card"], line=COLORS["border"], geom="roundRect", name="ConclusionCard"
    ))
    s11.elements.append(text_box(
        emu(6.75), emu(1.40), emu(5.55), emu(4.80),
        [
            TextLine("后续展望", size=20, color=COLORS["green"], bold=True),
            TextLine("• 丰富关卡内容、敌人类型和探索交互元素。", size=18),
            TextLine("• 优化连招、技能表现与战斗节奏，进一步提升手感。", size=18),
            TextLine("• 持续完善移动端适配、性能调优与数据管理机制。", size=18),
        ],
        fill="ECFDF5", line=COLORS["border"], geom="roundRect", name="OutlookCard"
    ))
    s11.elements.append(text_box(
        emu(1.10), emu(6.18), emu(10.80), emu(0.36),
        [TextLine("本项目更适合作为可扩展的玩法原型与毕业设计实践成果，后续仍具备进一步工程化与内容化拓展空间。", size=15, color=COLORS["muted"], align="c")],
        name="ConclusionNote", margin=(0, 0, 0, 0),
    ))
    slides.append(s11)

    # Slide 12
    s12 = Slide(title="致谢", bg=COLORS["bg_dark"])
    s12.elements.extend([
        shape_box(emu(0.80), emu(1.30), emu(0.16), emu(2.75), COLORS["accent"], name="ThanksBar"),
        text_box(
            emu(1.20), emu(1.50), emu(8.00), emu(1.20),
            [TextLine("感谢各位老师批评指正", size=32, color=COLORS["white"], bold=True)],
            name="ThanksTitle", margin=(0, 0, 0, 0),
        ),
        text_box(
            emu(1.22), emu(3.05), emu(7.30), emu(0.55),
            [TextLine("答辩人：候磊  |  论文题目：基于Unity的冒险探索RPG游戏设计与实现", size=16, color="CBD5E1")],
            name="ThanksSub", margin=(0, 0, 0, 0),
        ),
        shape_box(emu(9.35), emu(1.28), emu(2.55), emu(4.65), COLORS["accent"], name="ThanksAccent1"),
        shape_box(emu(9.72), emu(1.62), emu(1.80), emu(3.98), COLORS["bg_dark"], name="ThanksAccent2"),
        text_box(emu(9.92), emu(2.20), emu(1.40), emu(0.55), [TextLine("Unity", size=18, color=COLORS["white"], bold=True, align="c")],
                 fill=COLORS["accent_dark"], geom="roundRect", name="ThanksBadge1", valign="ctr", margin=(0, 0, 0, 0)),
        text_box(emu(9.92), emu(3.08), emu(1.40), emu(0.55), [TextLine("RPG", size=18, color=COLORS["white"], bold=True, align="c")],
                 fill=COLORS["green"], geom="roundRect", name="ThanksBadge2", valign="ctr", margin=(0, 0, 0, 0)),
        text_box(emu(9.92), emu(3.96), emu(1.40), emu(0.55), [TextLine("Defense", size=18, color=COLORS["white"], bold=True, align="c")],
                 fill=COLORS["amber"], geom="roundRect", name="ThanksBadge3", valign="ctr", margin=(0, 0, 0, 0)),
    ])
    slides.append(s12)

    return slides


def run_props(size: int, color: str, bold: bool = False) -> str:
    bold_attr = ' b="1"' if bold else ""
    return (
        f'<a:rPr lang="zh-CN" sz="{size * 100}"{bold_attr}>'
        f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
        f'<a:latin typeface="{FONT_LATIN}"/><a:ea typeface="{FONT_EA}"/><a:cs typeface="{FONT_CS}"/>'
        f'</a:rPr>'
    )


def textbox_xml(el: Element, shape_id: int) -> str:
    fill_xml = f'<a:solidFill><a:srgbClr val="{el.fill}"/></a:solidFill>' if el.fill else "<a:noFill/>"
    if el.line:
        line_xml = (
            f'<a:ln w="{el.line_width}"><a:solidFill><a:srgbClr val="{el.line}"/></a:solidFill>'
            f'<a:prstDash val="solid"/></a:ln>'
        )
    else:
        line_xml = "<a:ln><a:noFill/></a:ln>"
    body_pr = (
        f'<a:bodyPr wrap="square" anchor="{el.valign}" '
        f'lIns="{el.margin[0]}" rIns="{el.margin[1]}" tIns="{el.margin[2]}" bIns="{el.margin[3]}"/>'
    )
    paragraphs = []
    for line in el.lines:
        rp = run_props(line.size, line.color, line.bold)
        paragraphs.append(
            f'<a:p><a:pPr algn="{line.align}"/><a:r>{rp}<a:t>{esc(line.text)}</a:t></a:r>'
            f'<a:endParaRPr lang="zh-CN" sz="{line.size * 100}"/></a:p>'
        )
    return (
        f'<p:sp>'
        f'<p:nvSpPr><p:cNvPr id="{shape_id}" name="{esc(el.name or ("TextBox " + str(shape_id)))}"/>'
        f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{el.x}" y="{el.y}"/><a:ext cx="{el.w}" cy="{el.h}"/></a:xfrm>'
        f'<a:prstGeom prst="{el.geom}"><a:avLst/></a:prstGeom>{fill_xml}{line_xml}</p:spPr>'
        f'<p:txBody>{body_pr}<a:lstStyle/>{"".join(paragraphs)}</p:txBody>'
        f'</p:sp>'
    )


def shape_xml(el: Element, shape_id: int) -> str:
    line_xml = (
        f'<a:ln w="{el.line_width}"><a:solidFill><a:srgbClr val="{el.line}"/></a:solidFill><a:prstDash val="solid"/></a:ln>'
        if el.line else "<a:ln><a:noFill/></a:ln>"
    )
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="{esc(el.name or ("Shape " + str(shape_id)))}"/>'
        f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{el.x}" y="{el.y}"/><a:ext cx="{el.w}" cy="{el.h}"/></a:xfrm>'
        f'<a:prstGeom prst="{el.geom}"><a:avLst/></a:prstGeom>'
        f'<a:solidFill><a:srgbClr val="{el.fill or COLORS["card"]}"/></a:solidFill>{line_xml}</p:spPr></p:sp>'
    )


def picture_xml(el: Element, shape_id: int, rel_id: str) -> str:
    return (
        f'<p:pic>'
        f'<p:nvPicPr><p:cNvPr id="{shape_id}" name="{esc(el.name or ("Picture " + str(shape_id)))}"/>'
        f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
        f'<p:blipFill><a:blip r:embed="{rel_id}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
        f'<p:spPr><a:xfrm><a:off x="{el.x}" y="{el.y}"/><a:ext cx="{el.w}" cy="{el.h}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
        f'</p:pic>'
    )


def slide_xml(slide: Slide, media_map: Dict[Path, str]) -> Tuple[str, str]:
    parts = []
    rels = [
        ('rId1', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout', '../slideLayouts/slideLayout1.xml')
    ]
    shape_id = 2
    image_rid = 2

    for el in slide.elements:
        if el.kind == "textbox":
            parts.append(textbox_xml(el, shape_id))
            shape_id += 1
        elif el.kind == "shape":
            parts.append(shape_xml(el, shape_id))
            shape_id += 1
        elif el.kind == "picture":
            rid = f"rId{image_rid}"
            image_rid += 1
            target = '../media/' + media_map[el.path]  # type: ignore[index]
            rels.append((rid, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image', target))
            parts.append(picture_xml(el, shape_id, rid))
            shape_id += 1

    slide_doc = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<p:sld xmlns:a="{XMLNS_A}" xmlns:r="{XMLNS_R}" xmlns:p="{XMLNS_P}">'
        f'<p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="{slide.bg}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
        f'<p:spTree>'
        f'<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        f'<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        f'{"".join(parts)}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
    )

    rel_xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', f'<Relationships xmlns="{REL_NS}">']
    for rid, rel_type, target in rels:
        rel_xml.append(f'<Relationship Id="{rid}" Type="{rel_type}" Target="{target}"/>')
    rel_xml.append('</Relationships>')
    return slide_doc, ''.join(rel_xml)


def content_types_xml(slide_count: int) -> str:
    overrides = [
        ('/ppt/presentation.xml', 'application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml'),
        ('/ppt/presProps.xml', 'application/vnd.openxmlformats-officedocument.presentationml.presProps+xml'),
        ('/ppt/viewProps.xml', 'application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml'),
        ('/ppt/tableStyles.xml', 'application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml'),
        ('/ppt/theme/theme1.xml', 'application/vnd.openxmlformats-officedocument.theme+xml'),
        ('/ppt/slideMasters/slideMaster1.xml', 'application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml'),
        ('/ppt/slideLayouts/slideLayout1.xml', 'application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml'),
        ('/docProps/core.xml', 'application/vnd.openxmlformats-package.core-properties+xml'),
        ('/docProps/app.xml', 'application/vnd.openxmlformats-officedocument.extended-properties+xml'),
    ]
    for idx in range(1, slide_count + 1):
        overrides.append((f'/ppt/slides/slide{idx}.xml', 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml'))
    items = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Default Extension="png" ContentType="image/png"/>',
        '<Default Extension="jpg" ContentType="image/jpeg"/>',
        '<Default Extension="jpeg" ContentType="image/jpeg"/>',
    ]
    for part_name, content_type in overrides:
        items.append(f'<Override PartName="{part_name}" ContentType="{content_type}"/>')
    items.append('</Types>')
    return ''.join(items)


def root_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="{REL_NS}">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        '</Relationships>'
    )


def app_xml(slide_count: int) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
        'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
        f'<Application>Microsoft Office PowerPoint</Application><Slides>{slide_count}</Slides><Notes>0</Notes>'
        '<HiddenSlides>0</HiddenSlides><MMClips>0</MMClips><ScaleCrop>false</ScaleCrop>'
        '<HeadingPairs><vt:vector size="2" baseType="variant"><vt:variant><vt:lpstr>幻灯片标题</vt:lpstr></vt:variant>'
        f'<vt:variant><vt:i4>{slide_count}</vt:i4></vt:variant></vt:vector></HeadingPairs>'
        f'<TitlesOfParts><vt:vector size="{slide_count}" baseType="lpstr">'
        + ''.join(f'<vt:lpstr>Slide {i}</vt:lpstr>' for i in range(1, slide_count + 1))
        + '</vt:vector></TitlesOfParts><Company></Company><LinksUpToDate>false</LinksUpToDate>'
        '<SharedDoc>false</SharedDoc><HyperlinksChanged>false</HyperlinksChanged><AppVersion>16.0000</AppVersion>'
        '</Properties>'
    )


def core_xml() -> str:
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<cp:coreProperties xmlns:cp="{CP_NS}" xmlns:dc="{DC_NS}" xmlns:dcterms="{DERMS_NS}" '
        f'xmlns:dcmitype="{DCMITYPE_NS}" xmlns:xsi="{XSI_NS}">'
        f'<dc:title>{esc(THESIS_TITLE)} - 毕业答辩PPT</dc:title>'
        '<dc:creator>OpenAI Codex</dc:creator><cp:lastModifiedBy>OpenAI Codex</cp:lastModifiedBy>'
        f'<dcterms:created xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:created>'
        f'<dcterms:modified xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:modified>'
        '</cp:coreProperties>'
    )


def presentation_xml(slide_count: int) -> str:
    sld_ids = ''.join(
        f'<p:sldId id="{256 + idx}" r:id="rId{idx + 2}"/>' for idx in range(slide_count)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<p:presentation xmlns:a="{XMLNS_A}" xmlns:r="{XMLNS_R}" xmlns:p="{XMLNS_P}" saveSubsetFonts="1" autoCompressPictures="0">'
        '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
        f'<p:sldIdLst>{sld_ids}</p:sldIdLst>'
        f'<p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}"/><p:notesSz cx="6858000" cy="9144000"/>'
        '<p:defaultTextStyle/>'
        '</p:presentation>'
    )


def presentation_rels_xml(slide_count: int) -> str:
    rels = [
        ('rId1', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster', 'slideMasters/slideMaster1.xml')
    ]
    for idx in range(slide_count):
        rels.append((f'rId{idx + 2}', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide', f'slides/slide{idx + 1}.xml'))
    rels.extend([
        (f'rId{slide_count + 2}', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps', 'presProps.xml'),
        (f'rId{slide_count + 3}', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps', 'viewProps.xml'),
        (f'rId{slide_count + 4}', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles', 'tableStyles.xml'),
    ])
    xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', f'<Relationships xmlns="{REL_NS}">']
    for rid, rel_type, target in rels:
        xml.append(f'<Relationship Id="{rid}" Type="{rel_type}" Target="{target}"/>')
    xml.append('</Relationships>')
    return ''.join(xml)


def view_props_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<p:viewPr xmlns:a="{XMLNS_A}" xmlns:r="{XMLNS_R}" xmlns:p="{XMLNS_P}">'
        '<p:normalViewPr horizBarState="restored" vertBarState="restored"><p:restoredLeft sz="15620"/>'
        '<p:restoredTop sz="94660"/></p:normalViewPr><p:slideViewPr/><p:notesTextViewPr/>'
        '<p:gridSpacing cx="780288" cy="780288"/></p:viewPr>'
    )


def pres_props_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<p:presentationPr xmlns:a="{XMLNS_A}" xmlns:r="{XMLNS_R}" xmlns:p="{XMLNS_P}">'
        '<p:showPr showNarration="1" loop="0" useTimings="0"/></p:presentationPr>'
    )


def table_styles_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<a:tblStyleLst xmlns:a="{XMLNS_A}" def="{{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}}"/>'
    )


def theme_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<a:theme xmlns:a="{XMLNS_A}" name="Codex Thesis Theme">'
        '<a:themeElements>'
        '<a:clrScheme name="Codex Colors">'
        '<a:dk1><a:srgbClr val="0F172A"/></a:dk1>'
        '<a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>'
        '<a:dk2><a:srgbClr val="1E293B"/></a:dk2>'
        '<a:lt2><a:srgbClr val="E2E8F0"/></a:lt2>'
        '<a:accent1><a:srgbClr val="0EA5E9"/></a:accent1>'
        '<a:accent2><a:srgbClr val="10B981"/></a:accent2>'
        '<a:accent3><a:srgbClr val="F59E0B"/></a:accent3>'
        '<a:accent4><a:srgbClr val="4F46E5"/></a:accent4>'
        '<a:accent5><a:srgbClr val="EF4444"/></a:accent5>'
        '<a:accent6><a:srgbClr val="0F766E"/></a:accent6>'
        '<a:hlink><a:srgbClr val="2563EB"/></a:hlink>'
        '<a:folHlink><a:srgbClr val="7C3AED"/></a:folHlink>'
        '</a:clrScheme>'
        '<a:fontScheme name="Codex Fonts">'
        f'<a:majorFont><a:latin typeface="{FONT_LATIN}"/><a:ea typeface="{FONT_EA}"/><a:cs typeface="{FONT_CS}"/></a:majorFont>'
        f'<a:minorFont><a:latin typeface="{FONT_LATIN}"/><a:ea typeface="{FONT_EA}"/><a:cs typeface="{FONT_CS}"/></a:minorFont>'
        '</a:fontScheme>'
        '<a:fmtScheme name="Codex Formats">'
        '<a:fillStyleLst>'
        '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
        '<a:solidFill><a:schemeClr val="lt1"/></a:solidFill>'
        '<a:solidFill><a:schemeClr val="lt2"/></a:solidFill>'
        '</a:fillStyleLst>'
        '<a:lineStyleLst>'
        '<a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln>'
        '<a:ln w="25400" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln>'
        '<a:ln w="38100" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln>'
        '</a:lineStyleLst>'
        '<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>'
        '<a:bgFillStyleLst>'
        '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
        '<a:solidFill><a:schemeClr val="lt1"/></a:solidFill>'
        '<a:solidFill><a:schemeClr val="lt2"/></a:solidFill>'
        '</a:bgFillStyleLst>'
        '</a:fmtScheme></a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>'
    )


def slide_master_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<p:sldMaster xmlns:a="{XMLNS_A}" xmlns:r="{XMLNS_R}" xmlns:p="{XMLNS_P}">'
        '<p:cSld name="Master"><p:bg><p:bgRef idx="1001"><a:schemeClr val="bg1"/></p:bgRef></p:bg>'
        '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        '</p:spTree></p:cSld>'
        '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
        '<p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst>'
        '<p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>'
    )


def slide_master_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="{REL_NS}">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>'
        '</Relationships>'
    )


def slide_layout_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<p:sldLayout xmlns:a="{XMLNS_A}" xmlns:r="{XMLNS_R}" xmlns:p="{XMLNS_P}" type="blank" preserve="1">'
        '<p:cSld name="Blank Layout"><p:spTree>'
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'
    )


def slide_layout_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="{REL_NS}">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>'
        '</Relationships>'
    )


def collect_media(slides: Sequence[Slide]) -> Dict[Path, str]:
    media_map: Dict[Path, str] = {}
    counter = 1
    for slide in slides:
        for el in slide.elements:
            if el.kind == "picture" and el.path is not None and el.path not in media_map:
                media_map[el.path] = "image%d%s" % (counter, el.path.suffix.lower())
                counter += 1
    return media_map


def validate_pptx(pptx_path: Path, expected_slides: int) -> None:
    with zipfile.ZipFile(pptx_path, "r") as zf:
        names = set(zf.namelist())
        required = {
            "[Content_Types].xml",
            "_rels/.rels",
            "docProps/app.xml",
            "docProps/core.xml",
            "ppt/presentation.xml",
            "ppt/_rels/presentation.xml.rels",
            "ppt/slideMasters/slideMaster1.xml",
            "ppt/slideLayouts/slideLayout1.xml",
            "ppt/theme/theme1.xml",
        }
        missing = required - names
        if missing:
            raise RuntimeError("PPTX is missing required parts: %s" % ", ".join(sorted(missing)))
        slide_files = [n for n in names if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
        if len(slide_files) != expected_slides:
            raise RuntimeError("Expected %d slides, found %d" % (expected_slides, len(slide_files)))
        for name in names:
            if name.endswith(".xml") or name.endswith(".rels"):
                ET.fromstring(zf.read(name))


def generate() -> Path:
    slides = build_slides()
    media_map = collect_media(slides)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml(len(slides)))
        zf.writestr("_rels/.rels", root_rels_xml())
        zf.writestr("docProps/app.xml", app_xml(len(slides)))
        zf.writestr("docProps/core.xml", core_xml())
        zf.writestr("ppt/presentation.xml", presentation_xml(len(slides)))
        zf.writestr("ppt/_rels/presentation.xml.rels", presentation_rels_xml(len(slides)))
        zf.writestr("ppt/viewProps.xml", view_props_xml())
        zf.writestr("ppt/presProps.xml", pres_props_xml())
        zf.writestr("ppt/tableStyles.xml", table_styles_xml())
        zf.writestr("ppt/theme/theme1.xml", theme_xml())
        zf.writestr("ppt/slideMasters/slideMaster1.xml", slide_master_xml())
        zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", slide_master_rels_xml())
        zf.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout_xml())
        zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", slide_layout_rels_xml())

        for idx, slide in enumerate(slides, start=1):
            s_xml, r_xml = slide_xml(slide, media_map)
            zf.writestr(f"ppt/slides/slide{idx}.xml", s_xml)
            zf.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", r_xml)

        for src, target_name in media_map.items():
            zf.write(src, f"ppt/media/{target_name}")

    validate_pptx(OUTPUT, len(slides))
    return OUTPUT


if __name__ == "__main__":
    out = generate()
    print(out)
