using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class deathState : State
{
    private BossDate boss;
    private BossFSM manage;


    public deathState(BossFSM _manage)
    {

        this.manage = _manage;
        this.boss = manage.boss;
    }
    public void OnEnter()
    {
        boss.amt.Play("Death-NoEffect");
        
    }

    public void OnExit()
    {
       
    }

    public void OnUpDate()
    {
       
    }
}
