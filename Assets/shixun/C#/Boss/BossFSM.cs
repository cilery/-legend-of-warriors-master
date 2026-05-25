using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// boss状态枚举类
/// </summary>
/// 

public enum StateID   
{
    Idle, control, Chase, vanish,  attack,  fireAttack,  appear ,   Stiff,    retreat,    bule,       red,       death
 ///待机， 远程  ，追击 ，消失 ， 攻击， 火附魔攻击 ， 现身 ， 被弹反， 后退 ， 蓝元素状态，红元素状态，死亡
}
public enum ColorType
{
    RED,
    BLUE,
    GREEN,
    EMPTY

};
/// <summary>
/// boss 数值
/// </summary>
[Serializable]
public class BossDate 
{
  
    public Character chara;

    public float chaseSpeed; //移动速度

    public float retreatSpeed;//后退速度
    public Animator amt;   //boss动画状态机

    public Rigidbody2D rb; // boss 刚体

    public Transform traget ; //boss追击目标


    public AudioSource audioManage;

    public AudioClip walkAudio;

    public AudioClip attackAudio;

    public AudioClip vanishAudio;

    public AudioClip stiffAudio;

    public AudioClip cotrolAudio;

    public AudioClip redAudio;

    public AudioClip buleAudio;
    public AudioClip deathAudio;

}
/// <summary>
/// boss 状态机
/// </summary>
public class BossFSM : MonoBehaviour  
{

    private Dictionary<StateID, State> StateDic = new Dictionary<StateID, State>();//存放boss状态的字典
    public State currentState;//当前状态
    public BossDate boss = new BossDate();
    

    public SpriteRenderer SR;
    public Color sr;

  
  
    public GameObject control;

    public float damageColorTime = 1f;
  

  
    void Start()
    {
        //注册boss状态到字典中
        StateDic.Add(StateID.Idle,new IdleState(this));
        StateDic.Add(StateID.Chase, new ChaState(this));
        StateDic.Add(StateID.attack, new attState(this));
        StateDic.Add(StateID.vanish, new vanState(this));
        StateDic.Add(StateID.appear, new appearState(this));
        StateDic.Add(StateID.fireAttack, new fireAttState(this));
        StateDic.Add(StateID.control, new controlState(this));
        StateDic.Add(StateID.bule, new buleState(this));
        StateDic.Add(StateID.Stiff, new StiffState(this));
        StateDic.Add(StateID.retreat, new retreatState(this));
        StateDic.Add(StateID.red, new redState(this));
        StateDic.Add(StateID.death, new deathState(this));


        TransitionState(StateID.Idle);
      
        boss.amt = GetComponent<Animator>();
        boss.rb = GetComponent<Rigidbody2D>();
        boss.chara = GetComponent<Character>();
       
         SR = GetComponent<SpriteRenderer>();
        boss.audioManage = GetComponent<AudioSource>();
        sr = SR.color;

    
    }

    // Update is called once per frame
    void Update()
    {
        boss.traget = GameObject.FindWithTag("Player").transform;
        currentState.OnUpDate();  //执行状态类中的OnUpDate方法
     if (boss.chara.currentHealth <= 0)
        {
           TransitionState(StateID.death);
        }
     
    }

    /// <summary>
    /// 转换转态的方法
    /// </summary>
    /// <param name="id"></param>
    public void TransitionState(StateID id) 
    {
        if (currentState != null)
        {
            currentState.OnExit();
        }
        currentState = StateDic[id];
        currentState.OnEnter();
    }

    /// <summary>
    /// 翻转boss朝向
    /// </summary>
    /// <param name="target"></param>
    public void FlipTo(Transform target)
    {
       
        if (target != null)
        {
            if (transform.position.x > target.position.x)
            {
               
                transform.localScale = new Vector2(1, 1);
              


            }
            else if (transform.position.x < target.position.x)
            {
           
                transform.localScale = new Vector2(-1, 1);
              
            
            }


        }
    }
    /// <summary>
    /// 受到攻击时红光闪烁
    /// </summary>
    /// <param name="time"></param>
    public void FlashColor(float time)
    {   ////sprite变红色

        SR.color = Color.red;
        Invoke("ResetColor", time);      /////time时间后执行“函数”
    }

    public void ResetColor()    ////恢复原来颜色
    {
        SR.color = sr;
    }

}
