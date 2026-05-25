using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// 远程技能释放状态
/// </summary>
public class controlState : State
{
    private BossDate boss;
    private BossFSM manage;



    private float time;
    public controlState(BossFSM _manage)
    {

        this.manage = _manage;
        this.boss = manage.boss;
    }
    public void OnEnter()
    {

        boss.amt.Play("Cast");
        boss.audioManage.clip = boss.cotrolAudio;
        boss.audioManage.Play();
    }

    public void OnExit()
    {

    }

    public void OnUpDate()
    {
        boss.amt.Play("Cast");
    }
}
