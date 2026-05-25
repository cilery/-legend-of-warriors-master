from __future__ import annotations

import copy
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


def clear_non_ppr_children(paragraph: ET.Element) -> None:
    for child in list(paragraph):
        if child.tag != qn("pPr"):
            paragraph.remove(child)


def make_paragraph(template: ET.Element, text: str) -> ET.Element:
    paragraph = copy.deepcopy(template)
    clear_non_ppr_children(paragraph)

    run = ET.Element(qn("r"))
    template_rpr = template.find("./w:r/w:rPr", NS)
    if template_rpr is not None:
        run.append(copy.deepcopy(template_rpr))

    text_node = ET.SubElement(run, qn("t"))
    text_node.text = text
    paragraph.append(run)
    return paragraph


def main() -> None:
    base = Path(r"D:\codex_workspace\legend-of-warriors-master")
    input_path = base / "（已插入模块结构图-修正版）候磊-基于Unity的冒险探索RPG游戏设计与实现.docx"
    output_path = base / "（概要设计与模块图已修正）候磊-基于Unity的冒险探索RPG游戏设计与实现.docx"

    new_texts = {
        188: "玩家角色控制模块在概要设计中主要划分为输入控制模块、角色运动模块和角色行为模块三部分。输入控制模块负责接收玩家的移动、交互等操作指令，并将输入信息传递给后续控制流程；角色运动模块负责根据输入结果组织角色的移动、跳跃、朝向翻转及地形检测等基础运动逻辑，保证角色在场景中的行动连续性；角色行为模块则负责对攻击、防御、技能释放以及受击、死亡等行为进行统一管理。通过上述划分，玩家角色控制模块能够形成“输入采集—运动处理—行为响应”的完整控制链路。",
        193: "游戏UI界面模块在概要设计中主要由菜单界面模块、状态显示模块和界面反馈模块构成。菜单界面模块负责组织主菜单、暂停菜单和设置界面等基础交互入口；状态显示模块用于展示角色生命值、能量值以及技能和道具等关键信息，使玩家能够及时获取当前游戏状态；界面反馈模块则负责按钮响应、面板切换和过渡黑幕等界面表现，用于增强交互的清晰性与流畅性。通过这种划分，UI模块能够同时承担信息展示、界面组织与交互反馈三类职责。",
        198: "数据管理模块在概要设计中主要由数据采集模块、存档处理模块和数据调度模块组成。数据采集模块负责整理角色数据、场景数据和道具数据等需要统一维护的核心信息；存档处理模块负责对采集到的数据进行序列化、本地读写以及存档与读档处理，以保证游戏进度能够被持久保存；数据调度模块则负责对象注册、数据恢复和跨场景共享等工作，使各类数据在不同系统之间能够保持一致。该模块划分体现了“数据收集—数据存储—数据分发”的总体设计思路。",
        203: "战斗交互模块在概要设计中主要包括攻击判定模块、伤害计算模块和战斗反馈模块。攻击判定模块负责完成碰撞检测、范围判定和技能命中识别，用于确定战斗行为是否生效；伤害计算模块负责依据相关规则完成伤害结算、状态变化和死亡判定；战斗反馈模块则负责将判定和计算结果转化为受击反馈、镜头震动以及音效特效等表现内容。通过这样的模块划分，战斗系统能够形成由“判定—计算—反馈”组成的闭环结构，从而保证战斗过程既完整又清晰。",
        208: "场景管理模块在概要设计中主要由场景加载模块、场景切换模块和场景联动模块组成。场景加载模块负责处理加载请求、场景卸载与异步加载等基础流程；场景切换模块负责组织出生点记录、角色重定位和整体流程控制，以保证玩家在不同区域之间切换时逻辑连续；场景联动模块则负责处理黑幕过渡、相机刷新和界面联动等配套内容，使场景切换过程在视觉与状态上保持一致。该模块结构体现了场景系统从加载、切换到联动的整体组织方式。",
        213: "动画管理模块在概要设计中主要划分为角色动画模块、对象动画模块和动画事件模块。角色动画模块负责组织角色在移动、攻击和受击死亡等情形下的动画表现；对象动画模块负责管理敌人动画、机关动画和特效动画等场景中其他对象的动态表现；动画事件模块则负责在动画播放过程中处理帧事件触发、音效触发以及界面过渡等联动内容。通过以上划分，动画管理模块能够对角色、对象和事件三类表现要素进行分层组织，从而为系统提供统一的视觉反馈支撑。",
    }

    temp_dir = Path(tempfile.mkdtemp(prefix="update_module_desc_"))
    try:
        with zipfile.ZipFile(input_path, "r") as zin:
            zin.extractall(temp_dir)

        document_xml = temp_dir / "word" / "document.xml"
        tree = ET.parse(document_xml)
        root = tree.getroot()
        body = root.find("w:body", NS)
        if body is None:
            raise RuntimeError("Document body not found")

        paragraphs = [node for node in body if node.tag == qn("p")]
        template = paragraphs[188]

        for idx, text in new_texts.items():
            new_para = make_paragraph(template, text)
            body.insert(list(body).index(paragraphs[idx]), new_para)
            body.remove(paragraphs[idx])

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
