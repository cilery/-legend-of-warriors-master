from __future__ import annotations

import copy
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
ET.register_namespace("w", W_NS)


def qn(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def make_paragraph(template: ET.Element, text: str) -> ET.Element:
    paragraph = copy.deepcopy(template)
    for child in list(paragraph):
        if child.tag != qn("pPr"):
            paragraph.remove(child)

    run = ET.Element(qn("r"))
    template_rpr = template.find("./w:r/w:rPr", NS)
    if template_rpr is not None:
        run.append(copy.deepcopy(template_rpr))

    text_node = ET.SubElement(run, qn("t"))
    text_node.text = text
    paragraph.append(run)
    return paragraph


def main() -> None:
    input_path = Path(
        r"D:\codex_workspace\legend-of-warriors-master\paper-working-copy.docx"
    )
    output_path = Path(
        r"D:\codex_workspace\legend-of-warriors-master\（已补充模块设计）候磊-基于Unity的冒险探索RPG游戏设计与实现.docx"
    )

    module_overview_text = (
        "结合前文需求分析与系统总体架构，本系统按照“高内聚、低耦合、便于扩展”的原则，将游戏功能划分为"
        "玩家角色控制、游戏UI界面、数据管理、战斗交互、场景管理和动画管理六个核心模块。各模块之间通过"
        "事件触发、状态同步和数据共享的方式协同运行：玩家角色控制模块负责接收输入并驱动角色行为，是核心"
        "操作入口；战斗交互模块围绕攻击判定与伤害结算构成核心玩法循环；场景管理模块负责关卡切换与流程推进；"
        "动画管理模块负责角色、敌人与场景对象的视觉反馈；游戏UI界面模块承担信息展示与交互反馈；数据管理"
        "模块则为角色属性、场景进度和存档读档提供统一的数据支撑。通过上述划分，系统在满足功能完整性的同时，"
        "也能够有效降低不同功能之间的耦合程度，便于后续进行独立调试、功能扩展与维护。"
    )

    detail_texts = [
        "结合系统的实际实现内容，各功能模块在概要设计阶段不仅需要完成职责划分，还需要明确各自的输入、输出及与其他模块之间的协作关系。通过对核心功能模块进行独立设计，可以为后续的详细实现、调试测试和功能扩展提供清晰的结构基础。",
        "1.玩家角色控制功能模块设计",
        "玩家角色控制模块是系统的核心交互模块，主要负责处理玩家输入、角色移动、跳跃、攻击、格挡、翻滚、技能释放以及角色朝向切换等行为。该模块以有限状态机为控制基础，将待机、奔跑、跳跃、攻击、受击和死亡等状态进行封装，并结合Rigidbody2D、Collider2D及物理检测脚本完成接地判断、墙体检测和位移控制。模块输入主要为键盘或手柄操作信号，输出为角色状态变化、位移结果和动作触发信息，同时还需要向战斗模块、动画模块和UI模块同步角色当前状态，从而保证操作响应的及时性与行为逻辑的一致性。",
        "2.游戏UI界面功能模块设计",
        "游戏UI界面模块主要负责向玩家提供可视化的信息展示与功能交互，包括主菜单、暂停菜单、角色生命值与能量值显示、技能冷却显示、道具数量提示以及场景过渡黑幕等内容。该模块基于UGUI构建，结合DOTween实现按钮缩放、面板渐隐渐显和状态切换动画，使界面交互更加自然。模块从玩家角色控制、战斗交互、场景管理和数据管理模块接收状态数据，并实时刷新对应控件内容；同时将按钮点击、继续游戏、退出或设置等操作回传给流程控制与场景管理逻辑，形成完整的人机交互闭环。",
        "3.数据管理系统概要设计",
        "数据管理模块主要负责系统运行过程中各类关键数据的统一存储、读取与恢复，是保障游戏连续性和可回溯性的基础支撑模块。该模块以数据对象和统一接口为核心，对角色位置、当前场景、角色属性、道具信息以及存档点状态等内容进行组织，并通过JSON序列化方式写入本地持久化路径。为降低模块间耦合，系统要求需要持久化的对象实现统一存档接口，再由数据管理器统一注册和调度，从而实现自动存档、读档恢复、跨场景数据共享及异常情况下的数据保护。",
        "4.战斗交互系统功能模块设计",
        "战斗交互模块承担游戏的核心玩法逻辑，主要负责攻击判定、受击反馈、伤害计算、敌人行为响应及技能效果处理等内容。该模块一方面根据玩家角色控制模块和敌人状态控制逻辑触发的攻击事件，结合碰撞体、触发器和攻击范围检测完成命中判定；另一方面依据角色属性、技能状态与敌人状态进行伤害结算，并将结果同步给动画模块和UI模块，用于播放受击、死亡、镜头震动及数值反馈效果。通过将判定逻辑与表现逻辑适度分离，模块既能够保证战斗手感，也便于后续增加连击、技能组合和Boss机制等扩展功能。",
        "5.场景管理系统功能模块设计",
        "场景管理模块主要负责主菜单场景与游戏场景之间的切换、不同地图区域的跳转以及场景加载前后的流程组织。该模块以统一的场景加载事件为入口，在接收到传送点或菜单操作请求后，先记录目标场景和出生位置，再依次完成黑幕过渡、旧场景卸载、新场景异步加载、玩家重定位和相机边界刷新等操作，从而保证场景切换过程平滑、稳定。与此同时，场景管理模块还承担一定的流程调度职责，需要与UI模块、数据模块和相机控制模块保持联动，以保障探索推进的连续性和系统状态的一致性。",
        "6.动画管理系统功能模块设计",
        "动画管理模块主要负责角色、敌人、场景机关及界面切换等对象的动态表现，是提升游戏沉浸感和反馈质量的重要模块。该模块依托Animator动画状态机管理待机、移动、攻击、受击和死亡等动画片段的播放与切换，并结合动画事件在关键帧触发攻击判定、技能释放、音效播放或特效生成，实现行为逻辑与视觉表现的一致。对于界面切换和场景过渡，模块还结合DOTween完成淡入淡出、位移和缩放等动画效果，使系统在整体表现上更加流畅自然。",
    ]

    temp_dir = Path(tempfile.mkdtemp(prefix="paper_docx_edit_"))
    try:
        with zipfile.ZipFile(input_path, "r") as zin:
            zin.extractall(temp_dir)

        document_xml = temp_dir / "word" / "document.xml"
        tree = ET.parse(document_xml)
        root = tree.getroot()
        body = root.find("w:body", NS)
        if body is None:
            raise RuntimeError("Cannot find document body.")

        paragraphs = [node for node in body if node.tag == qn("p")]
        texts = [paragraph_text(p) for p in paragraphs]

        idx_core = texts.index("系统核心功能模块设计")
        idx_division = texts.index("系统功能模块划分")
        idx_detail = texts.index("系统功能模块详细说明")
        idx_first_item = texts.index("1.玩家角色控制功能模块设计")
        idx_next_section = texts.index("系统模块详细设计和实现")

        template_body = paragraphs[idx_division - 1]
        template_heading = paragraphs[idx_first_item]

        blank_after_division = paragraphs[idx_division + 1]
        body.insert(list(body).index(blank_after_division), make_paragraph(template_body, module_overview_text))
        body.remove(blank_after_division)

        remove_targets = paragraphs[idx_detail + 1 : idx_next_section]
        first_remove = remove_targets[0]
        insert_at = list(body).index(first_remove)

        new_paragraphs = []
        for i, text in enumerate(detail_texts):
            template = template_heading if i % 2 == 1 else template_body
            if i == 0:
                template = template_body
            new_paragraphs.append(make_paragraph(template, text))

        for offset, paragraph in enumerate(new_paragraphs):
            body.insert(insert_at + offset, paragraph)

        for paragraph in remove_targets:
            body.remove(paragraph)

        tree.write(document_xml, encoding="utf-8", xml_declaration=True)

        if output_path.exists():
            output_path.unlink()

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for file_path in temp_dir.rglob("*"):
                if file_path.is_file():
                    zout.write(file_path, file_path.relative_to(temp_dir))

        print(f"UPDATED_DOCX={output_path}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
