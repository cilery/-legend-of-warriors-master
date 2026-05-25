using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// À¶É«buffer×´Ì¬
/// </summary>
public class buleState : State
{

    private BossDate boss;
    private BossFSM manage;

    private float time;

    public buleState(BossFSM _manage)
    {
        this.manage = _manage;
        this.boss = manage.boss;


    }
    public void OnEnter()
    {
        time = 10f;
        boss.amt.Play("Hurt-NoEffect");
        manage.SR.color = new Color(0, 0, manage.sr.b, 1);
        boss.audioManage.clip = boss.buleAudio;
        boss.audioManage.Play();
    }

    public void OnExit()
    {

        manage.SR.color = new Color(manage.sr.r, manage.sr.g, manage.sr.b, 1);
    }

    public void OnUpDate()
    {
        manage.SR.color = new Color(0, 0, manage.sr.b, 1);
        time -= Time.deltaTime;
        if (time <= 0)
        {
            manage.TransitionState(StateID.Idle);

        }
    }
}
