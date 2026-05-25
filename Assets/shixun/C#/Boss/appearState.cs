using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// 现身开始状态
/// </summary>
public class appearState : State
{

    private BossDate boss;
    private BossFSM manage;

    private float time;
    public appearState(BossFSM _manage)
    {

        this.manage = _manage;
        this.boss = manage.boss;
    }
    public void OnEnter()
    {

        time = Random.Range(5, 8); //现身时机
    }

    public void OnExit()
    {

        time = 0;
    }

    public void OnUpDate()
    {

        time -= Time.deltaTime;
        if (time <= 0)
        {
            manage.SR.color = new Color(manage.sr.r, manage.sr.g, manage.sr.b, 1);//改变透明度来达到现身效果
            boss.audioManage.clip = boss.vanishAudio;
            boss.audioManage.Play();
            boss.amt.Play("presence");

        }
        else
        {
            manage.FlipTo(boss.traget);


            manage.transform.position = new Vector2(Random.Range(-4.4f, 63), manage.transform.position.y);
        }
    }
}

