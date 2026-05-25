using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// ºóÍËµÄ×´Ì¬
/// </summary>
public class retreatState : State
{

    private BossDate boss;
    private BossFSM manage;

    private float time;
    private float time2;
    public retreatState(BossFSM _manage)
    {

        this.manage = _manage;
        this.boss = manage.boss;
    }
    public void OnEnter()
    {
        time2 = 0;
        time = Random.Range(1, 4);
        boss.amt.Play("retreat");
    }

    public void OnExit()
    {

    }

    public void OnUpDate()
    {
        time2 += Time.deltaTime;
        time -= Time.deltaTime;
        manage.FlipTo(boss.traget);

        boss.rb.velocity = new Vector2(((manage.transform.position.x - boss.traget.transform.position.x) / Mathf.Abs((manage.transform.position.x - boss.traget.transform.position.x))) * boss.retreatSpeed, boss.rb.velocity.y);
        if (Isattack.IsAttack && Random.Range(2, 4) % 2 == 0)
        {
            manage.TransitionState((StateID)Random.Range(4, 6));
        }

        if (time <= 0)
        {
            manage.TransitionState(StateID.Idle);
        }

        if (time2 >= 1)
        {
            boss.audioManage.Play();
            time2 = 0;
        }

    }
}