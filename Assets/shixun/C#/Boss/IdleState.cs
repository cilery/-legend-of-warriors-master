using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// 待机状态
/// </summary>
public class IdleState : State
{

    private BossDate boss;
    private BossFSM manage;

    private float time;


    public IdleState(BossFSM _manage)
    {
        this.manage = _manage;
        this.boss = manage.boss;
    }
    public void OnEnter()
    {
        time = Random.Range(1, 3);
        manage.FlipTo(boss.traget);
        boss.amt.Play("Idle");
    }

    public void OnExit()
    {

    }

    public void OnUpDate()
    {

        boss.rb.velocity = Vector2.zero;
        manage.FlipTo(boss.traget);
        boss.amt.Play("Idle");

        time -= Time.deltaTime;



        //Debug.Log(time);


        if (time >= 1f && time < 3 && Input.GetMouseButtonDown(0) && Mathf.Abs(boss.traget.transform.position.x - manage.transform.position.x) <= 5f)
        {

            manage.TransitionState(StateID.vanish);
        }

        else if (time <= 0)
            manage.TransitionState((StateID)Random.Range(0, 3));


        ///待机时角色进入攻击范围进行攻击
    }
}

