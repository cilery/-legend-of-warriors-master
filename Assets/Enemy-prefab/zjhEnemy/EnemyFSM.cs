using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;

public enum EnemyStateType
{
    EnemyIdle,EnemyPatrol,EnemyChase,React,Attack,Hit,Death,Red,Blue
}
[Serializable]
public class Parameter
{

    public Character chara;
    public int health;
    public float moveSpeed;
    public float chaseSpeed;
    public float idleTime;
    public Transform[] patrolPoints;
    public Transform[] chasePoints;
    public Transform target;//目标的坐标

    ///攻击判断范围  -在OnDrawGizmos中绘制图像
    public LayerMask targetLayer;
    public Transform attackPoint;
    public float attackArea;
//////////



    public Animator animator;

    public AudioEnemy audioenemy;

////////测试用键盘输入看看受伤跟死亡行不行
    public bool getHit;


}

public class EnemyFSM : MonoBehaviour
{
    public Parameter parameter;

    private EnemyIState currentState;



    private Dictionary<EnemyStateType,EnemyIState> states = new Dictionary<EnemyStateType, EnemyIState>();//字典注册所有状态

    // Start is called before the first frame update

    private void Awake() {
        parameter.animator = GetComponent<Animator>();
        parameter.audioenemy = GetComponent<AudioEnemy>();

    }
    void Start()
    {
        states.Add(EnemyStateType.EnemyIdle,new EnemyIdleState(this));
        states.Add(EnemyStateType.EnemyPatrol,new EnemyPatrolState(this));
        states.Add(EnemyStateType.EnemyChase,new EnemyChaseState(this));
        states.Add(EnemyStateType.React,new ReactState(this));
        states.Add(EnemyStateType.Attack,new AttackState(this));
        states.Add(EnemyStateType.Hit,new HitState(this));
        states.Add(EnemyStateType.Death,new DeathState(this));
        states.Add(EnemyStateType.Red,new ERedState(this));
        states.Add(EnemyStateType.Blue,new EBlueState(this));

        TransitionState(EnemyStateType.EnemyIdle);

        //parameter.animator = GetComponent<Animator>();

    }

    // Update is called once per frame
    void Update()
    {
        currentState.OnUpdate();
      
        //getHit   测试hit 和death;
        if (parameter.chara.currentHealth<=0)
        {
            TransitionState(EnemyStateType.Death);
        }
        
    }
    public void enemyDestroy()
    {
        Destroy(gameObject);
    }

    public void EmonyHert(){
        parameter.getHit = true;
        Debug.Log("怪物受伤");
    }


    public void TransitionState(EnemyStateType type) ///切换状态函数
    {
        if(currentState!=null)
            currentState.OnExit();
        currentState = states[type];//设置的默认状态
        currentState.OnEnter();
    }

    public void FlipTo(Transform target)
    {
        if(target!= null)
        {
            if(transform.position.x > target.position.x)
            {
                transform.localScale = new Vector3(-1,1,1);
            }
            else if(transform.position.x < target.position.x)
            {
                transform.localScale = new Vector3(1,1,1);
            }
        }
    }

    //进入触发器范围是自动调用
    private void OnTriggerEnter2D(Collider2D other) {
        if(other.CompareTag("Player"))//判断进入的标签是不是玩家
        {
            parameter.target = other.transform;   //把玩家的Tranform 赋予给target让敌人知道玩家位置
           
        }
        
    }



    private void OnTriggerExit2D(Collider2D other) {
        if(other.CompareTag("Player"))
        {
            parameter.target = null; //退出范围时重置为空
        }
    }

   

    private void OnDrawGizmos() {
        Gizmos.DrawWireSphere(parameter.attackPoint.position,parameter.attackArea);//绘制一个空心圆
        
    }
    

}

