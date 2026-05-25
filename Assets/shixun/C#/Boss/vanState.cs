using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// ÒþÉí¿ªÊ¼×´Ì¬
/// </summary>
public class vanState : State
{
    private BossDate boss;
    private BossFSM manage;


    public vanState(BossFSM _manage)
    {

        this.manage = _manage;
        this.boss = manage.boss;
    }
    public void OnEnter()
    {
        manage.gameObject.layer = LayerMask.NameToLayer("other");
        boss.amt.Play("Death");
        boss.audioManage.clip = boss.vanishAudio;
        boss.audioManage.Play();
    }

    public void OnExit()
    {

    }

    public void OnUpDate()
    {

    }
}
