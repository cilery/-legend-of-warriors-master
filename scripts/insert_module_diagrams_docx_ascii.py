from __future__ import annotations

import copy
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

NS = {"w": W_NS, "wp": WP_NS}

ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)
ET.register_namespace("wp", WP_NS)
ET.register_namespace("a", A_NS)
ET.register_namespace("pic", PIC_NS)


def qn(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def clear_non_ppr_children(paragraph: ET.Element) -> None:
    for child in list(paragraph):
        if child.tag != qn(W_NS, "pPr"):
            paragraph.remove(child)


def make_text_paragraph(template: ET.Element, text: str) -> ET.Element:
    paragraph = copy.deepcopy(template)
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
    paragraph = copy.deepcopy(template)
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


def next_rel_id(rel_root: ET.Element) -> str:
    max_num = 0
    for rel in rel_root:
        rel_id = rel.attrib.get("Id", "")
        if rel_id.startswith("rId") and rel_id[3:].isdigit():
            max_num = max(max_num, int(rel_id[3:]))
    return f"rId{max_num + 1}"


def next_docpr_id(root: ET.Element) -> int:
    max_num = 0
    for docpr in root.findall(".//wp:docPr", NS):
        value = docpr.attrib.get("id")
        if value and value.isdigit():
            max_num = max(max_num, int(value))
    return max_num + 1


def add_relationship(rel_root: ET.Element, rel_id: str, rel_type: str, target: str) -> None:
    ET.SubElement(
        rel_root,
        qn(REL_NS, "Relationship"),
        {"Id": rel_id, "Type": rel_type, "Target": target},
    )


def replace_text_nodes(root: ET.Element, replacements: list[tuple[str, str]]) -> None:
    for text_node in root.findall(".//w:t", {"w": W_NS}):
        value = text_node.text
        if not value:
            continue
        new_value = value
        for old, new in replacements:
            new_value = new_value.replace(old, new)
        text_node.text = new_value


def main() -> None:
    base = Path(r"D:\codex_workspace\legend-of-warriors-master")
    docxs = [p for p in base.iterdir() if p.suffix.lower() == ".docx" and not p.name.startswith("~$")]
    docxs.sort(key=lambda p: p.stat().st_size, reverse=True)
    input_path = docxs[0]
    output_path = base / "paper_with_inserted_module_diagrams.docx"
    diagram_dir = base / "paper_module_diagrams"

    temp_dir = Path(tempfile.mkdtemp(prefix="docx_insert_ascii_"))
    try:
        with zipfile.ZipFile(input_path, "r") as zin:
            zin.extractall(temp_dir)

        document_xml = temp_dir / "word" / "document.xml"
        rels_xml = temp_dir / "word" / "_rels" / "document.xml.rels"
        media_dir = temp_dir / "word" / "media"
        media_dir.mkdir(parents=True, exist_ok=True)

        tree = ET.parse(document_xml)
        root = tree.getroot()
        body = root.find("w:body", {"w": W_NS})
        if body is None:
            raise RuntimeError("body not found")

        rel_tree = ET.parse(rels_xml)
        rel_root = rel_tree.getroot()

        paragraphs = [node for node in body if node.tag == qn(W_NS, "p")]

        image_template = paragraphs[183]
        caption_template = paragraphs[184]
        blank_template = paragraphs[182]

        diagram_specs = [
            (188, "01_player_control_module.svg", "图4-3 玩家角色控制模块结构图"),
            (190, "02_ui_module.svg", "图4-4 游戏UI界面模块结构图"),
            (192, "03_data_module.svg", "图4-5 数据管理模块结构图"),
            (194, "04_combat_module.svg", "图4-6 战斗交互模块结构图"),
            (196, "05_scene_module.svg", "图4-7 场景管理模块结构图"),
            (198, "06_animation_module.svg", "图4-8 动画管理模块结构图"),
        ]

        next_id = next_docpr_id(root)

        for anchor_index, svg_name, caption in diagram_specs:
            current_paragraphs = [node for node in body if node.tag == qn(W_NS, "p")]
            anchor_paragraph = current_paragraphs[anchor_index]
            insert_pos = list(body).index(anchor_paragraph) + 1

            src_svg = diagram_dir / svg_name
            dst_name = svg_name
            shutil.copyfile(src_svg, media_dir / dst_name)

            rel_id = next_rel_id(rel_root)
            add_relationship(
                rel_root,
                rel_id,
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
                f"media/{dst_name}",
            )

            image_paragraph = make_image_paragraph(image_template, rel_id, next_id, svg_name, 5753100, 3600000)
            next_id += 1
            caption_paragraph = make_text_paragraph(caption_template, caption)
            blank_paragraph = make_text_paragraph(blank_template, "")

            body.insert(insert_pos, image_paragraph)
            body.insert(insert_pos + 1, caption_paragraph)
            body.insert(insert_pos + 2, blank_paragraph)

        replacements = [
            ("图4-2 系统模块结构图", "图4-2 系统总体模块结构图"),
            ("该游戏的部分场景地图如下图4-2所示：", "该游戏的部分场景地图如下图4-9所示："),
            ("图 4-2 游戏场景地图", "图 4-9 游戏场景地图"),
            ("部分游戏角色帧动画如下图4-3所示：", "部分游戏角色帧动画如下图4-10所示："),
            ("图 4-3 游戏角色帧动画", "图 4-10 游戏角色帧动画"),
            ("部分敌人帧动画如下图4-4所示：", "部分敌人帧动画如下图4-11所示："),
            ("图 4-4 敌人帧动画", "图 4-11 敌人帧动画"),
            ("分别如下图4-5和4-6所示：", "分别如下图4-12和4-13所示："),
            ("图4-5 主菜单UI", "图4-12 主菜单UI"),
            ("图 4-5 主菜单UI", "图 4-12 主菜单UI"),
            ("图4-6 游场景常驻UI", "图4-13 游场景常驻UI"),
            ("图 4-6 游场景常驻UI", "图 4-13 游场景常驻UI"),
        ]
        replace_text_nodes(root, replacements)

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
