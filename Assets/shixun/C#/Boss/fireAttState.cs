using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// ¸½Ä§¹¥»÷×´Ì¬
/// </summary>
public class fireAttState : State
{
    private BossDate boss;
    private BossFSM manage;

    private float time;
    public fireAttState(BossFSM _manage)
    {

        this.manage = _manage;
        this.boss = manage.boss;
    }
    public void OnEnter()
    {
        boss.rb.velocity = Vector2.zero;
        manage.FlipTo(boss.traget);
        boss.amt.Play("Attack");
    }

    public void OnExit()
    {
       
    }

    public void OnUpDate()
    {
        boss.amt.Play("Attack");
    }
}
