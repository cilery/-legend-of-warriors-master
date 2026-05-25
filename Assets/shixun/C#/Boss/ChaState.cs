using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// ×·»÷×´Ì¬
/// </summary>
public class ChaState : State
{
    private BossDate boss;
    private BossFSM manage;

    private float time;

    public ChaState(BossFSM _manage)
    {
        this.manage = _manage;
        this.boss = manage.boss;


    }
    public void OnEnter()
    {
        time = 0;
        boss.amt.Play("Walk");
        boss.audioManage.clip = boss.walkAudio;

    }

    public void OnExit()
    {

    }

    public void OnUpDate()
    {
        time += Time.deltaTime;
        manage.FlipTo(boss.traget);
        if (Mathf.Abs(boss.traget.transform.position.x - manage.transform.position.x) > 1f)
            manage.transform.position = Vector2.MoveTowards(manage.transform.position, boss.traget.transform.position, boss.chaseSpeed * Time.deltaTime);
        else
            manage.TransitionState(StateID.retreat);
        if (Isattack.IsAttack)
        {
            manage.TransitionState((StateID)Random.Range(4, 6));
        }

        if (time >= 1)
        {
            boss.audioManage.Play();
            time = 0;
        }

    }
}