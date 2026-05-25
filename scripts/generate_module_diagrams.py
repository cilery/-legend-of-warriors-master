from __future__ import annotations

from pathlib import Path


OUT_DIR = Path(r"D:\codex_workspace\legend-of-warriors-master\paper_module_diagrams")

PAGE_W = 1600
PAGE_H = 720
TITLE_Y = 34

ROOT_W = 560
ROOT_H = 78
ROOT_X = (PAGE_W - ROOT_W) // 2
ROOT_Y = 54

GROUP_W = 250
GROUP_H = 74
GROUP_Y = 205
GROUP_XS = [95, 675, 1255]

ITEM_W = 150
ITEM_H = 72
ITEM_Y = 455
ITEM_X_GROUPS = [
    [80, 220, 360],
    [660, 800, 940],
    [1240, 1380, 1520],
]

FONT_FAMILY = "SimSun, Songti SC, Noto Serif CJK SC, serif"


MODULES = [
    {
        "file": "01_player_control_module.svg",
        "title": "玩家角色控制模块结构图",
        "root": "玩家角色控制模块",
        "groups": [
            ("输入控制模块", ["移动输入", "交互输入", "状态切换"]),
            ("角色运动模块", ["移动与跳跃", "朝向翻转", "地形检测"]),
            ("角色行为模块", ["攻击与防御", "技能释放", "受击与死亡"]),
        ],
    },
    {
        "file": "02_ui_module.svg",
        "title": "游戏UI界面模块结构图",
        "root": "游戏UI界面模块",
        "groups": [
            ("菜单界面模块", ["主菜单", "暂停菜单", "设置界面"]),
            ("状态显示模块", ["生命值显示", "能量值显示", "技能与道具"]),
            ("界面反馈模块", ["按钮反馈", "面板切换", "过渡黑幕"]),
        ],
    },
    {
        "file": "03_data_module.svg",
        "title": "数据管理模块结构图",
        "root": "数据管理模块",
        "groups": [
            ("数据采集模块", ["角色数据", "场景数据", "道具数据"]),
            ("存档处理模块", ["数据序列化", "本地读写", "存档与读档"]),
            ("数据调度模块", ["对象注册", "数据恢复", "跨场景共享"]),
        ],
    },
    {
        "file": "04_combat_module.svg",
        "title": "战斗交互模块结构图",
        "root": "战斗交互模块",
        "groups": [
            ("攻击判定模块", ["碰撞检测", "范围判定", "技能命中"]),
            ("伤害计算模块", ["属性计算", "伤害结算", "死亡判定"]),
            ("战斗反馈模块", ["受击反馈", "镜头震动", "音效特效"]),
        ],
    },
    {
        "file": "05_scene_module.svg",
        "title": "场景管理模块结构图",
        "root": "场景管理模块",
        "groups": [
            ("场景加载模块", ["加载请求", "场景卸载", "异步加载"]),
            ("场景切换模块", ["出生点记录", "角色重定位", "流程控制"]),
            ("场景联动模块", ["黑幕过渡", "相机刷新", "界面联动"]),
        ],
    },
    {
        "file": "06_animation_module.svg",
        "title": "动画管理模块结构图",
        "root": "动画管理模块",
        "groups": [
            ("角色动画模块", ["移动动画", "攻击动画", "受击死亡"]),
            ("对象动画模块", ["敌人动画", "机关动画", "特效动画"]),
            ("动画事件模块", ["帧事件触发", "音效触发", "界面过渡"]),
        ],
    },
]


def wrap_text(text: str, max_chars: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        if len(current) >= max_chars:
            lines.append(current)
            current = ch
        else:
            current += ch
    if current:
        lines.append(current)
    return lines


def text_block(x: int, y: int, w: int, h: int, text: str, font_size: int, max_chars: int) -> str:
    lines = wrap_text(text, max_chars)
    line_h = int(font_size * 1.45)
    total_h = line_h * len(lines)
    start_y = y + (h - total_h) / 2 + font_size
    return "\n".join(
        f'<text x="{x + w / 2:.1f}" y="{start_y + i * line_h:.1f}" font-family="{FONT_FAMILY}" '
        f'font-size="{font_size}" text-anchor="middle" fill="#000000">{line}</text>'
        for i, line in enumerate(lines)
    )


def rect(x: int, y: int, w: int, h: int, stroke_w: int = 2) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFFFFF" stroke="#000000" stroke-width="{stroke_w}"/>'


def line(x1: float, y1: float, x2: float, y2: float, stroke_w: int = 2) -> str:
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#000000" stroke-width="{stroke_w}"/>'


def group_center_x(group_index: int) -> float:
    return GROUP_XS[group_index] + GROUP_W / 2


def item_center_x(group_index: int, item_index: int) -> float:
    return ITEM_X_GROUPS[group_index][item_index]


def render_module(module: dict) -> str:
    parts: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W}" height="{PAGE_H}" viewBox="0 0 {PAGE_W} {PAGE_H}">',
        f'<rect x="0" y="0" width="{PAGE_W}" height="{PAGE_H}" fill="#FFFFFF"/>',
        f'<text x="{PAGE_W / 2:.1f}" y="{TITLE_Y}" font-family="{FONT_FAMILY}" font-size="28" text-anchor="middle" fill="#000000">{module["title"]}</text>',
    ]

    parts.append(rect(ROOT_X, ROOT_Y, ROOT_W, ROOT_H))
    parts.append(text_block(ROOT_X, ROOT_Y, ROOT_W, ROOT_H, module["root"], 28, 14))

    root_cx = ROOT_X + ROOT_W / 2
    root_bottom = ROOT_Y + ROOT_H
    upper_bus_y = 145
    parts.append(line(root_cx, root_bottom, root_cx, upper_bus_y))
    parts.append(line(group_center_x(0), upper_bus_y, group_center_x(2), upper_bus_y))

    for group_idx, (group_name, items) in enumerate(module["groups"]):
        gx = GROUP_XS[group_idx]
        gy = GROUP_Y
        gcx = group_center_x(group_idx)
        parts.append(line(gcx, upper_bus_y, gcx, gy))
        parts.append(rect(gx, gy, GROUP_W, GROUP_H))
        parts.append(text_block(gx, gy, GROUP_W, GROUP_H, group_name, 24, 10))

        lower_bus_y = 390
        parts.append(line(gcx, gy + GROUP_H, gcx, lower_bus_y))
        parts.append(line(item_center_x(group_idx, 0), lower_bus_y, item_center_x(group_idx, 2), lower_bus_y))

        for item_idx, item in enumerate(items):
            cx = item_center_x(group_idx, item_idx)
            ix = int(cx - ITEM_W / 2)
            parts.append(line(cx, lower_bus_y, cx, ITEM_Y))
            parts.append(rect(ix, ITEM_Y, ITEM_W, ITEM_H))
            parts.append(text_block(ix, ITEM_Y, ITEM_W, ITEM_H, item, 22, 8))

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for module in MODULES:
        svg = render_module(module)
        (OUT_DIR / module["file"]).write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
