using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// ¹¥»÷×´Ì¬
/// </summary>
public class attState : State
{
    private BossDate boss;
    private BossFSM manage;




    public attState(BossFSM _manage)
    {
        this.manage = _manage;
        this.boss = manage.boss;
    }
    public void OnEnter()
    {
        boss.rb.velocity = Vector2.zero;
        boss.amt.Play("Attack-NoEffect");
    }

    public void OnExit()
    {

    }

    public void OnUpDate()
    {

    }


}
