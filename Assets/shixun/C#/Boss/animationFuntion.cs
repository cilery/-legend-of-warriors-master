using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// boss动画帧事件
/// </summary>
public class animationFuntion : MonoBehaviour  //
{

    private BossFSM manage;
    public VoidEventSO GameOverEvent;



    private void Awake()
    {
        manage = GetComponent<BossFSM>();



    }
    public void attackExit() //普通攻击结束时调用的方法
    {

        manage.TransitionState(StateID.Idle);

    }

    public void VanishEnd()  //隐身动画结束时调用的方法
    {
        manage.boss.amt.Play("Empty");

        manage.SR.color = new Color(manage.sr.r, manage.sr.g, manage.sr.b, 0);



        manage.TransitionState(StateID.appear);
    }
    public void appearEnd()//现身动画结束时调用的方法
    {
        manage.gameObject.layer = LayerMask.NameToLayer("enemy");

        manage.TransitionState(StateID.Idle);
    }

    public void fireAttEnd()//附加火魔法攻击动画结束时调用的方法
    {

        manage.TransitionState(StateID.Idle);

    }

    public void controlEnd()//控制技能动画结束时调用的方法
    {
        Instantiate(manage.control, new Vector3(manage.boss.traget.transform.position.x, manage.boss.traget.transform.position.y + 3f), Quaternion.identity);

        manage.TransitionState(StateID.Idle);
    }

    public void frameShake()
    {
        frameFroze.Instance.shakeCamera();
    }
        
    public void stiffEnd()
    {
        manage.TransitionState(StateID.Idle);
    }
    public void deathEnd()
    {
        Destroy(manage.gameObject);
        GameOverEvent.RaiseEvent();
    }

    public void attackAudio()
    {
        manage.boss.audioManage.clip = manage.boss.attackAudio;
        manage.boss.audioManage.Play();
    }
}
