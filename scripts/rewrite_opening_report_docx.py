# -*- coding: utf-8 -*-
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


def clear_paragraph(paragraph: ET.Element) -> None:
    for child in list(paragraph):
        if child.tag != qn("pPr"):
            paragraph.remove(child)


def make_paragraph(template: ET.Element, text: str) -> ET.Element:
    paragraph = copy.deepcopy(template)
    clear_paragraph(paragraph)

    run = ET.Element(qn("r"))
    template_rpr = template.find("./w:r/w:rPr", NS)
    if template_rpr is not None:
        run.append(copy.deepcopy(template_rpr))

    text_node = ET.SubElement(run, qn("t"))
    if text.startswith(" ") or text.endswith(" "):
        text_node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    text_node.text = text
    paragraph.append(run)
    return paragraph


def set_cell_text(cell: ET.Element, text: str) -> None:
    paragraphs = cell.findall("./w:p", NS)
    if not paragraphs:
        return
    template = paragraphs[0]
    new_paragraph = make_paragraph(template, text)
    for child in list(cell):
        if child.tag == qn("p"):
            cell.remove(child)
    cell.append(new_paragraph)


def set_cell_lines(cell: ET.Element, lines: list[str]) -> None:
    paragraphs = cell.findall("./w:p", NS)
    if not paragraphs:
        return
    template = paragraphs[0]
    for child in list(cell):
        if child.tag == qn("p"):
            cell.remove(child)
    for line in lines:
        cell.append(make_paragraph(template, line))


def main() -> None:
    input_path = Path(
        r"E:\毕业论文批改资料\开题报告\（答辩）候磊-开题报告-基于Unity的冒险探索RPG游戏设计与实现 (1).docx"
    )
    output_path = Path(
        r"D:\codex_workspace\legend-of-warriors-master\（答辩）候磊-开题报告-基于Unity的冒险探索RPG游戏设计与实现-优化统一版.docx"
    )

    purpose_lines = [
        "Unity作为成熟的跨平台游戏引擎，具备可视化开发、组件化架构和插件生态完善等优势，已成为中小型2D/3D游戏开发的重要工具。",
        "本课题基于Unity 2022.3 LTS开展设计与实现，围绕角色控制、战斗交互、场景切换、数据存档和界面表现等核心环节，构建一套结构清晰、可扩展、可复用的2D冒险探索RPG实现方案。",
        "从游戏类型来看，RPG的核心价值在于探索驱动、战斗反馈与角色成长体验。",
        "本课题聚焦“冒险探索+战斗交互”的核心玩法，结合场景推进、存档读档、传送点切换和敌人交互等机制，力求在有限资源条件下实现完整的玩法闭环，提升玩家的沉浸感与操作反馈。",
        "从工程实践来看，本课题将围绕FSM有限状态机、Animator动画系统、物理碰撞检测、UGUI界面系统、Addressables异步资源加载、Cinemachine镜头控制、DOTween动画过渡以及JSON数据持久化等技术展开，实现角色、敌人、场景、UI和数据模块的协同运行，并为后续功能扩展与维护提供清晰的结构基础。",
    ]

    status_lines = [
        "国内外对Unity游戏开发、RPG战斗系统、状态机控制、场景切换和数据持久化等方向已形成较为丰富的研究成果。",
        "国外研究更强调引擎能力、交互体验与商业化落地，Unity凭借跨平台特性、UGUI与插件生态，在2D/3D游戏开发中具有广泛应用。",
        "国内相关研究主要集中在Unity引擎应用、2D角色扮演游戏设计、关卡触发、战斗系统和移动端适配等方面。",
        "现有文献表明，FSM、物理碰撞、场景触发器、镜头跟随、界面交互与本地存档等技术已经在不少项目中得到验证，但多数学位论文和工程案例往往侧重单一模块，系统级整合与玩法闭环设计仍有进一步优化空间。",
        "结合本课题的实现目标，论文采用模块化设计思路，将角色控制、战斗交互、场景管理、动画表现、UI展示和数据存储统一到同一套工程架构中，既保留Unity成熟技术栈的可落地性，也突出冒险探索RPG在操作手感、反馈表现和场景推进上的整体体验。",
        "参考文献：",
        "宣雨松. Unity3D 游戏开发. 北京: 人民邮电出版社, 2012.",
        "Unity3D Technologies. Unity3D 4.x 从入门到精通. 北京: 中国铁道出版社, 2013.",
        "吴正源. 基于Unity3D的MMORPG移动端游戏设计与实现[D]. 华中科技大学, 2022.",
        "路宜松. 基于Unity引擎的2D角色扮演游戏的设计与实现[D]. 沈阳理工大学, 2021.",
        "何柳青. 基于Unity3D的动作角色扮演游戏战斗系统研究与开发[J]. 现代信息科技, 2023, 7(24):1-5.",
        "杨淮敏, 邱树伟. 基于Unity3D的冒险游戏的设计与实现[J]. 现代计算机, 2023, 29(13):73-78.",
        "施长征. 基于Unity3D的关卡触发器系统的设计与实现[D]. 南京大学, 2016.",
        "郭沛. 中国网络游戏行业历史与展望[J]. 现代营销(经营版), 2020, 328(04):35-36.",
        "区泽宇, 李晶, 魏菊霞, 等. 基于Unity3D游戏的设计与开发[J]. 无线互联科技, 2019.",
    ]

    content_lines = [
        "本研究旨在基于Unity引擎设计并实现一款2D冒险探索RPG游戏。系统采用组件化与模块化相结合的设计思路，围绕角色控制、战斗交互、场景管理、动画表现、UI交互和数据存储等核心模块构建完整的游戏框架，形成“探索-战斗-反馈-推进”的核心玩法闭环。",
        "在具体实现上，角色控制模块基于输入系统与有限状态机管理待机、移动、跳跃、攻击、受击和死亡等状态，并通过Animator完成动画切换；战斗交互模块负责攻击判定、伤害计算、击退与受击反馈，并结合敌人状态机实现基础AI行为；场景管理模块基于Addressables与SceneLoader完成主菜单、关卡场景和Boss场景的异步加载、卸载与传送点切换；数据管理模块通过DataManager统一处理角色位置、场景信息和存档数据，并以JSON形式实现本地持久化；UI模块则基于UGUI与DOTween实现血条、技能状态、菜单面板和过渡效果；动画与镜头模块结合Cinemachine、Animator与DOTween，提升画面表现和打击反馈。",
        "本课题拟解决的主要问题包括：角色多状态切换与动画同步问题、模块化架构下的低耦合与可扩展问题、场景切换与存档读档的数据一致性问题、战斗反馈与镜头表现的统一问题，以及在保持表现效果前提下的基础性能优化问题。",
        "最终目标是实现一个功能完整、逻辑闭环、结构清晰的2D冒险探索RPG原型，为后续扩展关卡、敌人类型和玩法机制打下基础。",
    ]

    method_lines = [
        "研究方法上，本课题主要采用文献综述、系统分析与设计、原型迭代开发以及测试验证相结合的方式开展。",
        "文献综述法用于整理Unity游戏开发、FSM状态机、场景管理、UI交互、数据持久化等相关研究，为系统设计提供理论依据；系统分析与设计用于明确各功能模块的输入、输出与协作关系，形成清晰的架构划分；原型迭代开发用于先实现核心玩法闭环，再逐步完善场景、UI和反馈表现；测试验证则通过功能测试与性能测试检查角色控制、战斗交互、场景切换和存档读档等关键流程的正确性与稳定性。",
        "研究条件方面，本项目的开发环境为Unity 2022.3.5f1c1与Visual Studio 2022，使用C#作为主要开发语言，并结合UGUI、Addressables、Cinemachine、DOTween以及Newtonsoft.Json等插件和库完成实现。项目所需的2D资源、动画资源、场景资源和音频资源已具备基础素材条件，能够支撑原型开发与功能验证。",
        "可能存在的问题主要包括：FSM状态设计不合理导致逻辑复杂、场景切换与存档数据同步出错、镜头与动画反馈调试成本较高，以及功能范围控制不当导致开发周期超出预期。针对上述问题，本文将采用模块化设计、分阶段开发与多轮测试调优的方式加以解决。",
    ]

    temp_dir = Path(tempfile.mkdtemp(prefix="rewrite_opening_report_"))
    try:
        with zipfile.ZipFile(input_path, "r") as zin:
            zin.extractall(temp_dir)

        document_xml = temp_dir / "word" / "document.xml"
        tree = ET.parse(document_xml)
        root = tree.getroot()
        body = root.find("w:body", NS)
        if body is None:
            raise RuntimeError("Cannot find document body.")

        tables = [node for node in body if node.tag == qn("tbl")]
        if not tables:
            raise RuntimeError("Cannot find opening report table.")
        table = tables[0]
        rows = table.findall("./w:tr", NS)
        if len(rows) < 6:
            raise RuntimeError("Unexpected opening report table structure.")

        cells = [rows[i].find("./w:tc", NS) for i in range(5)]
        if any(cell is None for cell in cells):
            raise RuntimeError("Missing expected table cells.")

        set_cell_lines(cells[0], ["选题的目的和意义", *purpose_lines])
        set_cell_lines(cells[1], ["综述国内外对本论题的研究动态（附主要参考文献）", *status_lines])
        set_cell_lines(cells[2], ["三、研究的基本内容，拟解决的主要问题", "1、研究的基本内容", *content_lines])
        set_cell_lines(cells[3], ["四、研究方法、研究条件和可能存在的问题", "1、研究方法", *method_lines])
        set_cell_lines(
            cells[4],
            [
                "五、进度安排",
                "2025.9.1至2025.9.30  确定论文选题，下达任务。",
                "2025.10.1至2025.10.31  熟悉任务、明确工作方向，收集查阅相关文档，撰写开题报告。",
                "2025.11.1至2026.1.31  完成系统需求分析和概要设计说明书，完成论文框架结构，并编制核心程序代码、完成调试和单元测试，同时完成论文第一稿。",
                "2026.2.1至2026.3.20  完成系统全部程序代码并再次调试，解决遗留问题，完成论文整体撰写并提交第二稿。",
                "2026.3.21至2026.4.30  根据反馈意见修改完善系统及论文，并提交第三稿。",
                "2026年5月中上旬  收集毕业答辩相关材料，做好答辩准备。",
            ],
        )

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
