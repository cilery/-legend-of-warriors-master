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
    if text.startswith(" ") or text.endswith(" "):
        text_node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    text_node.text = text
    paragraph.append(run)
    return paragraph


def make_code_paragraph(template: ET.Element, lines: list[str]) -> ET.Element:
    paragraph = copy.deepcopy(template)
    for child in list(paragraph):
        if child.tag != qn("pPr"):
            paragraph.remove(child)

    run = ET.Element(qn("r"))
    template_rpr = template.find("./w:r/w:rPr", NS)
    if template_rpr is not None:
        run.append(copy.deepcopy(template_rpr))

    for index, line in enumerate(lines):
        text_node = ET.SubElement(run, qn("t"))
        if line.startswith(" ") or line.endswith(" "):
            text_node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        text_node.text = line
        if index != len(lines) - 1:
            ET.SubElement(run, qn("br"))

    paragraph.append(run)
    return paragraph


def find_index(texts: list[str], target: str) -> int:
    for index, text in enumerate(texts):
        if text == target:
            return index
    for index, text in enumerate(texts):
        if target in text:
            return index
    raise ValueError(f"Cannot find paragraph: {target}")


def replace_between(
    body: ET.Element,
    paragraphs: list[ET.Element],
    texts: list[str],
    start_heading: str,
    end_marker: str,
    new_paragraphs: list[ET.Element],
) -> None:
    start_index = find_index(texts, start_heading)
    end_index = find_index(texts, end_marker)
    remove_targets = paragraphs[start_index + 1 : end_index]
    if not remove_targets:
        return

    insert_at = list(body).index(remove_targets[0])
    for offset, paragraph in enumerate(new_paragraphs):
        body.insert(insert_at + offset, paragraph)

    for paragraph in remove_targets:
        body.remove(paragraph)


def insert_before_text(
    body: ET.Element,
    paragraphs: list[ET.Element],
    texts: list[str],
    before_text: str,
    new_paragraphs: list[ET.Element],
) -> None:
    target_index = find_index(texts, before_text)
    insert_at = list(body).index(paragraphs[target_index])
    for offset, paragraph in enumerate(new_paragraphs):
        body.insert(insert_at + offset, paragraph)


def build_body_paragraphs(body_template: ET.Element, texts: list[str]) -> list[ET.Element]:
    return [make_paragraph(body_template, text) for text in texts]


def build_code_block(body_template: ET.Element, lines: list[str]) -> list[ET.Element]:
    return [
        make_paragraph(body_template, "关键代码如下："),
        make_code_paragraph(body_template, lines),
    ]


def main() -> None:
    input_path = Path(
        r"D:\codex_workspace\legend-of-warriors-master\（已补充模块设计）候磊-基于Unity的冒险探索RPG游戏设计与实现.docx"
    )
    output_path = Path(
        r"D:\codex_workspace\legend-of-warriors-master\（详细设计与实现已改写）候磊-基于Unity的冒险探索RPG游戏设计与实现.docx"
    )

    temp_dir = Path(tempfile.mkdtemp(prefix="rewrite_detail_docx_"))
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

        heading_index = find_index(texts, "敌人状态控制设计实现")
        heading_template = paragraphs[heading_index]
        body_template = paragraphs[heading_index + 1]

        enemy_section = build_body_paragraphs(
            body_template,
            [
                "敌人状态控制模块主要负责普通敌人的巡逻移动、碰撞检测、转向等待以及受击后的行为中断，是战斗交互系统中最基础的一层行为逻辑。结合项目当前实现，敌人对象由 Enemy 脚本维护移动速度、朝向、受击状态和无敌计时器等运行数据，并通过 BaseState 抽象类约束不同状态的进入、更新和退出逻辑，从而避免将全部行为堆叠在同一个更新流程中。",
                "在状态组织方式上，项目目前重点完成了基于 monsterPatrolState 的巡逻逻辑。敌人激活后默认进入巡逻状态，在 FixedUpdate 中按照当前朝向持续移动；与此同时，系统会通过地面检测点和前方墙体检测点实时获取碰撞结果。当检测到前方存在障碍物，或者前方已经离开可行走地面时，状态逻辑不会立即强制翻转，而是先把 wait 标记置为 true，再借助短时无敌计时器形成一个简短的停顿过程，待计时结束后再统一完成转向。",
                "这种“检测—停顿—翻转”的处理方式，一方面能够避免敌人在边缘位置来回抖动，另一方面也让巡逻行为的视觉表现更加自然。除此之外，Enemy 脚本还通过 isHurt、isDead 等标记与动画控制器联动，当敌人处于受击或死亡状态时，基础移动会被暂时中断，从而保证状态切换与表现结果保持一致。部分敌人状态机和状态控制设置如图5-1、5-2所示：",
            ],
        ) + build_code_block(
            body_template,
            [
                "public void waitCounter()",
                "{",
                "    if (wait)",
                "    {",
                "        invulner.TriggerInvulnerable();",
                "        invulner.updateIn();",
                "        if (!invulner.invulnerable)",
                "        {",
                "            wait = false;",
                "            transform.parent.localScale = new Vector3(faceDir.x, 1, 1);",
                "        }",
                "    }",
                "}",
            ],
        )

        damage_section = [
            make_paragraph(heading_template, "伤害、受击与死亡反馈设计实现"),
            *build_body_paragraphs(
                body_template,
                [
                    "在战斗结算层面，项目将攻击判定、伤害扣减、受击反馈和死亡处理组织为一个连续的交互闭环。攻击发起后，带有 Attack 组件的判定区域会在触发器接触时检测目标是否包含 Character 组件；若检测成功，则调用 TakeDamage() 执行伤害结算。这样做可以把“命中判定”和“数值处理”拆分到不同脚本中完成，既方便复用，也便于后续扩展不同攻击类型。",
                    "伤害结算完成后，Character 会先判断当前是否处于无敌状态，若未处于无敌状态，则根据 damage 数值扣减生命值，并启动短暂无敌计时，防止角色在同一帧或极短时间内被重复命中。当生命值仍大于零时，系统通过 OnTakeDamage 事件通知动画和位移模块执行受击动作；当生命值归零时，则直接触发 OnDie 事件，切换到死亡表现。对于敌人而言，Enemy 脚本会在 OnTakeDamage() 中设置 hurt 标记并施加击退力；对于玩家而言，PlayControl 也会根据攻击来源方向附加受击位移，从而增强战斗反馈的层次感。",
                    "为了进一步突出命中瞬间的打击感，Attack 脚本还在攻击命中敌人或 Boss 时叠加了停顿帧与镜头震动反馈，使数值变化、动画播放和屏幕表现形成统一响应。整体来看，该模块虽然实现结构相对简洁，但已经完成了“命中检测—扣血—无敌帧保护—受击击退—死亡反馈”的基本战斗闭环。",
                ],
            ),
            *build_code_block(
                body_template,
                [
                    "public void TakeDamage(Attack attack)",
                    "{",
                    "    if (invulner.invulnerable) return;",
                    "    if (currentHealth > attack.damage)",
                    "    {",
                    "        currentHealth -= attack.damage;",
                    "        invulner.TriggerInvulnerable();",
                    "        OnTakeDamage?.Invoke(attack.transform);",
                    "    }",
                    "    else",
                    "    {",
                    "        currentHealth = 0;",
                    "        OnDie?.Invoke();",
                    "    }",
                    "}",
                ],
            ),
        ]

        player_animation_section = build_body_paragraphs(
            body_template,
            [
                "玩家角色动画状态机负责把输入控制、物理状态和战斗事件同步到可视化动作表现中，是角色操控体验的重要组成部分。结合当前项目实现，PlayControl 负责接收输入系统中的移动、跳跃、攻击、防御、闪避和技能指令，并以 isAttack、isDefense、isDodge、isSkill、isHurt、isDead 等状态变量记录角色当前行为；PlayerAnimation 则在每帧读取这些状态，并统一写入 Animator 参数，驱动对应动画片段切换。",
                "在基础运动表现方面，角色主要通过 Rigidbody2D 的速度变化来区分待机、奔跑、起跳和下落等动作。脚本会根据水平速度设置 run 参数，根据竖直速度设置 jump 参数，并结合地面检测结果决定是否处于接地状态，这样动画状态机就能较准确地反映角色的移动节奏。与此同时，角色的朝向翻转在移动逻辑中同步完成，因此人物在左右移动时能够直接切换表现方向，保证动作与操作一致。",
                "在战斗表现方面，普通攻击、防御、闪避和两个技能都不是单纯依赖单一动画触发器，而是与输入限制、位移控制和无敌时间共同作用。例如攻击期间会锁定部分操作，技能释放时会启动独立计时器并同步刷新 UI 冷却显示，受击状态则会强制清除攻击或技能中的部分动画标记。通过这种方式，项目将角色控制逻辑和 Animator 状态机有效衔接起来，使动作切换既具备响应速度，也具备较好的可维护性。玩家角色状态机和状态控制设置如图5-3、5-4所示：",
            ],
        ) + build_code_block(
            body_template,
            [
                "public void SetAnimation()",
                "{",
                "    animator.SetFloat(\"run\", Mathf.Abs(rg.velocity.x));",
                "    animator.SetFloat(\"jump\", rg.velocity.y);",
                "    animator.SetBool(\"isCollider\", playControl.isGround);",
                "    animator.SetBool(\"static\", character.invulnerable);",
                "    animator.SetBool(\"isDead\", playControl.isDead);",
                "    animator.SetBool(\"isAttack\", playControl.isAttack);",
                "    animator.SetBool(\"isWall_Forward\", playControl.isWall_Forward && (!playControl.isGround));",
                "    animator.SetBool(\"defensePrefect\", playControl.defensePrefect);",
                "}",
            ],
        )

        scene_section = build_body_paragraphs(
            body_template,
            [
                "场景管理模块主要负责菜单场景与游戏场景之间的切换、不同区域地图之间的传送，以及切换前后的流程协调。结合当前实现，传送点对象不会直接调用底层加载接口，而是通过 SceneLoadEventSO 统一发出场景加载请求，把目标场景、角色目标位置和是否启用淡入淡出效果一并传递给 SceneLoader 处理。这样能够把交互入口与场景调度逻辑解耦，便于后续扩展新的传送对象或菜单入口。",
                "在加载流程上，SceneLoader 会先通过 isLoading 标记判断当前是否已经处于加载过程，避免重复触发请求导致多次切换叠加。如果当前存在已加载场景，系统将先执行旧场景卸载流程：先触发黑幕渐入，再广播卸载事件，随后卸载旧场景并暂时隐藏玩家对象。旧场景处理完成后，再通过 Addressables 的异步接口以 Additive 模式加载目标场景，从而保证切换过程相对平滑，减少突兀感。",
                "当目标场景加载完成后，系统会更新当前场景引用，将玩家移动到预设出生点，重新激活角色对象，并根据需要触发淡出效果。若进入的是可游玩场景，还会进一步广播 afterSceneLoadedEvent，用于刷新相机边界和界面显示状态。因此，该模块不仅承担了地图切换功能，也在一定程度上充当了场景流程调度中心。游戏场景管理模块如图5-5所示：",
            ],
        ) + build_code_block(
            body_template,
            [
                "private void OnLoadRequestEvent(GameSceneSO locationToLoad, Vector3 posToGo, bool fadeScreen)",
                "{",
                "    if (isLoading) return;",
                "    isLoading = true;",
                "    sceneToLoad = locationToLoad;",
                "    positionToGo = posToGo;",
                "    this.fadeScreen = fadeScreen;",
                "    if (currentLoadedScene != null)",
                "        StartCoroutine(UnLoadPreviousScene());",
                "    else",
                "        LoadNewScene();",
                "}",
            ],
        )

        data_section = build_body_paragraphs(
            body_template,
            [
                "游戏数据管理模块用于保存和恢复场景切换后的关键运行信息，是保证冒险流程连续性的基础支撑。结合当前项目实现，系统采用“统一数据对象 + 统一管理器 + 接口注册”的组织方式：Data 负责保存场景、角色位置和部分浮点数值，DataManager 负责统一调度存档与读档流程，而所有需要参与持久化的对象则通过 ISaveable 接口接入管理体系。",
                "在数据结构上，项目重点保存了当前场景标识、角色位置字典以及生命值等浮点数据。其中，角色位置并未直接序列化 Vector3，而是通过 SerializeVector3 将坐标拆分为 x、y、z 三个字段进行存储，再在读取时恢复为 Unity 可直接使用的向量对象。这样处理虽然增加了一层转换，但可以提高序列化稳定性，也便于在排查存档问题时直接观察数据内容。",
                "在执行流程上，参与存档的对象会在启用时注册到 DataManager 的 saveableList 中，保存时由管理器统一遍历这些对象，依次收集其状态并写入总数据对象，随后再使用 JsonConvert.SerializeObject() 序列化为 JSON 字符串并输出到本地持久化路径。读档时则按照相反顺序将文件内容恢复为数据对象，并分发给各个已注册对象完成状态还原。游戏内存档点设置如图5-6所示：",
            ],
        ) + build_code_block(
            body_template,
            [
                "public void Save()",
                "{",
                "    foreach (var saveable in saveableList)",
                "    {",
                "        saveable.GetSaveData(saveData);",
                "    }",
                "    var resultPath = jsonFolder + \"data.sav\";",
                "    var jsonData = JsonConvert.SerializeObject(saveData);",
                "    if (!File.Exists(resultPath))",
                "        Directory.CreateDirectory(jsonFolder);",
                "    File.WriteAllText(resultPath, jsonData);",
                "}",
            ],
        )

        ui_section = build_body_paragraphs(
            body_template,
            [
                "游戏 UI 界面承担了状态显示、菜单操作和局内反馈三类职责，是玩家感知系统运行状态的主要窗口。结合当前项目实现，界面系统主要由主菜单、暂停面板、Game Over 面板、血量显示、技能冷却显示和音量同步控件组成，整体由 UIManager 统一协调，并通过事件机制与角色控制、场景切换和数据读取逻辑保持联动。",
                "在状态显示部分，PlayerStatBar 负责根据角色生命值百分比刷新主血条，并通过延迟血条营造较为直观的受击反馈效果。与此同时，UIManager 会持续读取玩家两个技能的计时器进度，并通过 Image.fillAmount 的填充比例更新技能图标，使玩家能够及时判断技能是否处于冷却阶段。相比一次性静态显示，这种动态刷新方式更适合动作类 RPG 的即时战斗节奏。",
                "在交互控制部分，项目已实现主菜单焦点设置、暂停界面开关、游戏失败界面弹出以及音量值同步等功能。其中暂停面板的显示与隐藏会直接联动 Time.timeScale，以确保玩家在菜单操作期间暂停游戏进程；场景卸载和读档事件则会同步控制界面显隐状态，从而保证不同流程阶段的界面反馈一致。游戏系统的主菜单 UI 和场景常驻 UI 分别如下图4-5和4-6所示：",
            ],
        ) + build_code_block(
            body_template,
            [
                "private void TogglePausePanel()",
                "{",
                "    if (pausePanel.activeInHierarchy)",
                "    {",
                "        pausePanel.SetActive(false);",
                "        Time.timeScale = 1;",
                "    }",
                "    else",
                "    {",
                "        pauseEvent.RaiseEvent();",
                "        pausePanel.SetActive(true);",
                "        Time.timeScale = 0;",
                "    }",
                "}",
            ],
        )

        camera_section = build_body_paragraphs(
            body_template,
            [
                "玩家角色镜头相机模块主要依赖 Unity 场景组件与少量辅助脚本完成跟随、边界限制和反馈增强，不再额外构建复杂的自定义相机状态机。结合当前项目实现，相机的基础跟随主要由 Cinemachine 虚拟相机负责，使镜头能够持续锁定玩家位置，并在角色移动、跳跃和切换区域时保持相对平滑的过渡效果，从而减少手动插值带来的调试成本。",
                "在场景适配方面，由于不同地图区域的可视边界并不一致，项目通过 CameraControl 脚本在场景加载完成后主动刷新 CinemachineConfiner2D 的边界碰撞体。脚本会查找当前场景中带有 Bounds 标签的限制对象，并将其 Collider2D 重新赋值给相机约束组件，再调用缓存失效方法完成刷新。这样可以保证玩家在进入不同场景后，相机仍然被限制在当前地图的有效显示范围内，避免看到场景外的空白区域。",
                "在战斗反馈方面，镜头系统还与命中反馈逻辑形成配合。攻击命中敌人或 Boss 时，系统会触发短暂的停顿帧和镜头震动效果，使打击结果不只是体现在数值变化上，而是进一步转化为玩家能够直接感知的屏幕反馈。整体来看，该模块虽以引擎组件配置为主，但已经较好地服务于探索与战斗两类核心体验。游戏内玩家角色镜头相机模块设置如图5-7所示：",
            ],
        ) + build_code_block(
            body_template,
            [
                "private void GetNewCameraBounds()",
                "{",
                "    var obj = GameObject.FindGameObjectWithTag(\"Bounds\");",
                "    if (obj == null)",
                "        return;",
                "    confiner2D.m_BoundingShape2D = obj.GetComponent<Collider2D>();",
                "    confiner2D.InvalidateCache();",
                "}",
            ],
        )

        replace_between(
            body,
            paragraphs,
            texts,
            "敌人状态控制设计实现",
            "图 5-1 部分敌人状态机",
            enemy_section,
        )
        replace_between(
            body,
            paragraphs,
            texts,
            "玩家角色动画状态机设计实现",
            "表3-1 游戏角色状态转移表",
            player_animation_section,
        )
        replace_between(
            body,
            paragraphs,
            texts,
            "游戏场景管理设计实现",
            "图 5-5 游戏场景管理模块",
            scene_section,
        )
        replace_between(
            body,
            paragraphs,
            texts,
            "游戏数据管理设计实现",
            "图 5-6 游戏内存档点设置",
            data_section,
        )
        replace_between(
            body,
            paragraphs,
            texts,
            "游戏UI界面的设计实现",
            "图 4-5 主菜单UI",
            ui_section,
        )
        replace_between(
            body,
            paragraphs,
            texts,
            "玩家角色镜头相机模块设计实现",
            "图 5-7 玩家角色镜头相机模块设置",
            camera_section,
        )
        insert_before_text(
            body,
            paragraphs,
            texts,
            "玩家角色动画状态机设计实现",
            damage_section,
        )

        tree.write(document_xml, encoding="utf-8", xml_declaration=True)

        if output_path.exists():
            output_path.unlink()

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for file_path in temp_dir.rglob("*"):
                if file_path.is_file():
                    zout.write(file_path, file_path.relative_to(temp_dir))

        print(f"OUTPUT_DOCX={output_path}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
