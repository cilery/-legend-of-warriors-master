from __future__ import annotations

import copy
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC_NS = "http://schemas.openxmlformats.org/drawingml/2006/picture"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

NS = {"w": W_NS}

ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)
ET.register_namespace("wp", WP_NS)
ET.register_namespace("a", A_NS)
ET.register_namespace("pic", PIC_NS)


def qn(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def clone_paragraph_template(template: ET.Element) -> ET.Element:
    return copy.deepcopy(template)


def clear_non_ppr_children(paragraph: ET.Element) -> None:
    for child in list(paragraph):
        if child.tag != qn(W_NS, "pPr"):
            paragraph.remove(child)


def make_text_paragraph(template: ET.Element, text: str) -> ET.Element:
    paragraph = clone_paragraph_template(template)
    clear_non_ppr_children(paragraph)

    run = ET.Element(qn(W_NS, "r"))
    template_rpr = template.find("./w:r/w:rPr", NS)
    if template_rpr is not None:
        run.append(copy.deepcopy(template_rpr))

    text_node = ET.SubElement(run, qn(W_NS, "t"))
    text_node.text = text
    paragraph.append(run)
    return paragraph


def make_image_paragraph(template: ET.Element, rid: str, doc_pr_id: int, name: str, cx: int, cy: int) -> ET.Element:
    paragraph = clone_paragraph_template(template)
    clear_non_ppr_children(paragraph)

    run = ET.SubElement(paragraph, qn(W_NS, "r"))
    drawing = ET.SubElement(run, qn(W_NS, "drawing"))
    inline = ET.SubElement(
        drawing,
        qn(WP_NS, "inline"),
        {"distT": "0", "distB": "0", "distL": "114300", "distR": "114300"},
    )
    ET.SubElement(inline, qn(WP_NS, "extent"), {"cx": str(cx), "cy": str(cy)})
    ET.SubElement(inline, qn(WP_NS, "effectExtent"), {"l": "0", "t": "0", "r": "0", "b": "0"})
    ET.SubElement(inline, qn(WP_NS, "docPr"), {"id": str(doc_pr_id), "name": name, "descr": name})
    c_nv = ET.SubElement(inline, qn(WP_NS, "cNvGraphicFramePr"))
    ET.SubElement(c_nv, qn(A_NS, "graphicFrameLocks"), {"noChangeAspect": "1"})

    graphic = ET.SubElement(inline, qn(A_NS, "graphic"))
    graphic_data = ET.SubElement(graphic, qn(A_NS, "graphicData"), {"uri": "http://schemas.openxmlformats.org/drawingml/2006/picture"})
    pic = ET.SubElement(graphic_data, qn(PIC_NS, "pic"))
    nv_pic_pr = ET.SubElement(pic, qn(PIC_NS, "nvPicPr"))
    ET.SubElement(nv_pic_pr, qn(PIC_NS, "cNvPr"), {"id": str(doc_pr_id), "name": name, "descr": name})
    c_nv_pic_pr = ET.SubElement(nv_pic_pr, qn(PIC_NS, "cNvPicPr"))
    ET.SubElement(c_nv_pic_pr, qn(A_NS, "picLocks"), {"noChangeAspect": "1"})

    blip_fill = ET.SubElement(pic, qn(PIC_NS, "blipFill"))
    ET.SubElement(blip_fill, qn(A_NS, "blip"), {qn(R_NS, "embed"): rid})
    stretch = ET.SubElement(blip_fill, qn(A_NS, "stretch"))
    ET.SubElement(stretch, qn(A_NS, "fillRect"))

    sp_pr = ET.SubElement(pic, qn(PIC_NS, "spPr"))
    xfrm = ET.SubElement(sp_pr, qn(A_NS, "xfrm"))
    ET.SubElement(xfrm, qn(A_NS, "off"), {"x": "0", "y": "0"})
    ET.SubElement(xfrm, qn(A_NS, "ext"), {"cx": str(cx), "cy": str(cy)})
    prst = ET.SubElement(sp_pr, qn(A_NS, "prstGeom"), {"prst": "rect"})
    ET.SubElement(prst, qn(A_NS, "avLst"))

    return paragraph


def parse_relationships(path: Path) -> tuple[ET.ElementTree, ET.Element]:
    tree = ET.parse(path)
    root = tree.getroot()
    return tree, root


def add_relationship(rel_root: ET.Element, rel_id: str, rel_type: str, target: str) -> None:
    ET.SubElement(
        rel_root,
        qn(REL_NS, "Relationship"),
        {"Id": rel_id, "Type": rel_type, "Target": target},
    )


def next_rel_id(rel_root: ET.Element) -> str:
    max_num = 0
    for rel in rel_root:
        rel_id = rel.attrib.get("Id", "")
        if rel_id.startswith("rId"):
            suffix = rel_id[3:]
            if suffix.isdigit():
                max_num = max(max_num, int(suffix))
    return f"rId{max_num + 1}"


def next_docpr_id(root: ET.Element) -> int:
    max_num = 0
    for docpr in root.findall(".//wp:docPr", {"wp": WP_NS}):
        value = docpr.attrib.get("id")
        if value and value.isdigit():
            max_num = max(max_num, int(value))
    return max_num + 1


def main() -> None:
    base = Path(r"D:\codex_workspace\legend-of-warriors-master")
    candidates = [p for p in base.iterdir() if p.suffix.lower() == ".docx" and not p.name.startswith("~$")]
    input_path = None
    for candidate in candidates:
        if "已补充模块设计" in candidate.name:
            input_path = candidate
            break
    if input_path is None:
        raise RuntimeError("Cannot find the source docx with supplemented module design.")

    output_path = base / "（已插入模块结构图）候磊-基于Unity的冒险探索RPG游戏设计与实现.docx"
    diagram_dir = base / "paper_module_diagrams"

    temp_dir = Path(tempfile.mkdtemp(prefix="docx_insert_diagrams_"))
    try:
        with zipfile.ZipFile(input_path, "r") as zin:
            zin.extractall(temp_dir)

        document_xml = temp_dir / "word" / "document.xml"
        rels_xml = temp_dir / "word" / "_rels" / "document.xml.rels"
        media_dir = temp_dir / "word" / "media"
        media_dir.mkdir(parents=True, exist_ok=True)

        tree = ET.parse(document_xml)
        root = tree.getroot()
        body = root.find("w:body", NS)
        if body is None:
            raise RuntimeError("Cannot find document body.")

        rel_tree, rel_root = parse_relationships(rels_xml)

        paragraphs = [node for node in body if node.tag == qn(W_NS, "p")]
        texts = [paragraph_text(p) for p in paragraphs]

        image_template = next(
            p
            for p in paragraphs
            if p.find(".//w:drawing", NS) is not None
        )
        caption_template = next(
            p
            for p in paragraphs
            if paragraph_text(p).strip() == "图4-1 系统模块结构图"
        )
        normal_template = next(
            p
            for p in paragraphs
            if "结合系统的实际实现内容" in paragraph_text(p)
        )

        insert_after_paragraphs = [
            "玩家角色控制模块是系统的核心交互模块",
            "游戏UI界面模块主要负责向玩家提供可视化的信息展示与功能交互",
            "数据管理模块主要负责系统运行过程中各类关键数据的统一存储、读取与恢复",
            "战斗交互模块承担游戏的核心玩法逻辑",
            "场景管理模块主要负责主菜单场景与游戏场景之间的切换",
            "动画管理模块主要负责角色、敌人、场景机关及界面切换等对象的动态表现",
        ]

        captions = [
            "图4-2 玩家角色控制模块结构图",
            "图4-3 游戏UI界面模块结构图",
            "图4-4 数据管理模块结构图",
            "图4-5 战斗交互模块结构图",
            "图4-6 场景管理模块结构图",
            "图4-7 动画管理模块结构图",
        ]

        svg_files = [
            "01_player_control_module.svg",
            "02_ui_module.svg",
            "03_data_module.svg",
            "04_combat_module.svg",
            "05_scene_module.svg",
            "06_animation_module.svg",
        ]

        next_id = next_docpr_id(root)
        body_children = list(body)

        for anchor_prefix, caption, svg_name in zip(insert_after_paragraphs, captions, svg_files):
            current_paragraphs = [node for node in body if node.tag == qn(W_NS, "p")]
            current_texts = [paragraph_text(p) for p in current_paragraphs]
            anchor_paragraph = next(p for p, t in zip(current_paragraphs, current_texts) if t.startswith(anchor_prefix))
            insert_pos = list(body).index(anchor_paragraph) + 1

            svg_path = diagram_dir / svg_name
            media_name = svg_name
            shutil.copyfile(svg_path, media_dir / media_name)

            rel_id = next_rel_id(rel_root)
            add_relationship(
                rel_root,
                rel_id,
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
                f"media/{media_name}",
            )

            image_paragraph = make_image_paragraph(
                image_template,
                rel_id,
                next_id,
                svg_name,
                5753100,
                3600000,
            )
            next_id += 1
            caption_paragraph = make_text_paragraph(caption_template, caption)
            blank_paragraph = make_text_paragraph(normal_template, "")

            body.insert(insert_pos, image_paragraph)
            body.insert(insert_pos + 1, caption_paragraph)
            body.insert(insert_pos + 2, blank_paragraph)

        replacements = [
            ("该游戏的部分场景地图如下图4-2所示：", "该游戏的部分场景地图如下图4-8所示："),
            ("图 4-2 游戏场景地图", "图 4-8 游戏场景地图"),
            ("部分游戏角色帧动画如下图4-3所示：", "部分游戏角色帧动画如下图4-9所示："),
            ("图 4-3 游戏角色帧动画", "图 4-9 游戏角色帧动画"),
            ("部分敌人帧动画如下图4-4所示：", "部分敌人帧动画如下图4-10所示："),
            ("图 4-4 敌人帧动画", "图 4-10 敌人帧动画"),
            ("分别如下图4-5和4-6所示：", "分别如下图4-11和4-12所示："),
            ("图4-5 主菜单UI", "图4-11 主菜单UI"),
            ("图 4-5 主菜单UI", "图 4-11 主菜单UI"),
            ("图4-6 游场景常驻UI", "图4-12 游场景常驻UI"),
            ("图 4-6 游场景常驻UI", "图 4-12 游场景常驻UI"),
        ]

        for paragraph in body.findall("w:p", NS):
            for text_node in paragraph.findall(".//w:t", NS):
                if not text_node.text:
                    continue
                updated = text_node.text
                for old, new in replacements:
                    updated = updated.replace(old, new)
                text_node.text = updated

        tree.write(document_xml, encoding="utf-8", xml_declaration=True)
        rel_tree.write(rels_xml, encoding="utf-8", xml_declaration=True)

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
