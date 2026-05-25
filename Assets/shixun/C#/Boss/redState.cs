using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class redState : State
{
    private BossDate boss;
    private BossFSM manage;



    private float time;
    public redState(BossFSM _manage)
    {

        this.manage = _manage;
        this.boss = manage.boss;
    }
    public void OnEnter()
    {
        time = 0.5f;
        boss.amt.Play("Hurt");
        boss.audioManage.clip = boss.redAudio;
        boss.audioManage.Play();
        boss.chara.currentHealth -= 200;
    }

    public void OnExit()
    {

    }

    public void OnUpDate()
    {
        time -= Time.deltaTime;
        if (time <= 0)
        {
            manage.TransitionState(StateID.Idle);
        }
    }
}
