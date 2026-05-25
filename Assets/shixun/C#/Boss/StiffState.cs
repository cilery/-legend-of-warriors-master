using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// 被完美格挡的状态
/// </summary>
public class StiffState : State
{


    private BossDate boss;
    private BossFSM manage;

    private float time;
    public StiffState(BossFSM _manage)
    {

        this.manage = _manage;
        this.boss = manage.boss;
    }
    public void OnEnter()
    {
        boss.amt.Play("Stiff");
        boss.audioManage.clip = boss.stiffAudio;
        boss.audioManage.Play();
    }

    public void OnExit()
    {

    }

    public void OnUpDate()
    {

    }
}