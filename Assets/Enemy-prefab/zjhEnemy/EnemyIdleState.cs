using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class EnemyIdleState : EnemyIState
{
    private EnemyFSM manager;
    private Parameter parameter;

    private float timer;

    public EnemyIdleState(EnemyFSM manager)
    {
        this.manager = manager;
        this.parameter = manager.parameter; 
    }

    public void OnEnter()
    {
        parameter.animator.Play("Idle");
    }
    public void OnUpdate()
    {
        timer += Time.deltaTime;

        /////////测试 hit death的
        if(parameter.getHit) //转换Hit状态
        {
            manager.TransitionState(EnemyStateType.Hit);
        }


        if(parameter.target != null && 
            parameter.target.position.x >=parameter.chasePoints[0].position.x &&
            parameter.target.position.x <= parameter.chasePoints[1].position.x)
        {
            manager.TransitionState(EnemyStateType.React);
        }

        if(timer >= parameter.idleTime)
        {
            manager.TransitionState(EnemyStateType.EnemyPatrol);
        }
    }
    public void OnExit()
    {
        timer = 0;
    }
}

public class EnemyPatrolState : EnemyIState
{
    private EnemyFSM manager;
    private Parameter parameter;

    private int patrolPosition;

    public EnemyPatrolState(EnemyFSM manager)
    {
        this.manager = manager;
        this.parameter = manager.parameter;
    }

    public void OnEnter()
    {
        parameter.animator.Play("Walk");
    }
    public void OnUpdate()
    {
        manager.FlipTo(parameter.patrolPoints[patrolPosition]);

        manager.transform.position = Vector2.MoveTowards(manager.transform.position,
            parameter.patrolPoints[patrolPosition].position,parameter.moveSpeed * Time.deltaTime);
        
        /////////测试 hit death的
        if(parameter.getHit) //转换Hit状态
        {
            manager.TransitionState(EnemyStateType.Hit);
        }


        if(parameter.target != null && 
            parameter.target.position.x >=parameter.chasePoints[0].position.x &&
            parameter.target.position.x <= parameter.chasePoints[1].position.x)
        {
            manager.TransitionState(EnemyStateType.React);
        }

        if(Vector2.Distance(manager.transform.position,parameter.patrolPoints[patrolPosition].position)<.1f)
        {
            manager.TransitionState(EnemyStateType.EnemyPatrol);
        }    
    }
    public void OnExit()
    {
        patrolPosition++;
        
        if(patrolPosition >= parameter.patrolPoints.Length)
        {
            patrolPosition = 0;
        }
    }
}

public class EnemyChaseState : EnemyIState  ///追击状态
{
    private EnemyFSM manager;
    private Parameter parameter;

    public EnemyChaseState(EnemyFSM manager)
    {
        this.manager = manager;
        this.parameter = manager.parameter;
    }

    public void OnEnter()
    {
       parameter.animator.Play("Walk");
    }
    public void OnUpdate()
    {
        manager.FlipTo(parameter.target);
        if(parameter.target)

          manager.transform.position = Vector2.MoveTowards(manager.transform.position,
            parameter.target.position,parameter.chaseSpeed * Time.deltaTime);
        
        /////////测试 hit death的
        if(parameter.getHit) //转换Hit状态
        {
            manager.TransitionState(EnemyStateType.Hit);
        }
        
        //追击目标超出范围或者失去目标时切换到Idle状态继续巡逻
        if(parameter.target == null || manager.transform.position.x < parameter.chasePoints[0].position.x
        || manager.transform.position.x > parameter.chasePoints[1].position.x)
        {
            manager.TransitionState(EnemyStateType.EnemyIdle);
        }
        //切换攻击状态
        if(Physics2D.OverlapCircle(parameter.attackPoint.position,parameter.attackArea,parameter.targetLayer))
        {
            manager.TransitionState(EnemyStateType.Attack);
        }

    }
    public void OnExit()
    {

    }

    
}
public class ReactState : EnemyIState
{
    private EnemyFSM manager;
    private Parameter parameter;

    private AnimatorStateInfo info; //动画播放进度

    public ReactState(EnemyFSM manager)
    {
        this.manager = manager;
        this.parameter = manager.parameter;
    }

    public void OnEnter()
    {
       parameter.animator.Play("React");
    }
    public void OnUpdate()
    {
        info = parameter.animator.GetCurrentAnimatorStateInfo(0);

        /////////测试 hit death的
        if(parameter.getHit) //转换Hit状态
        {
            manager.TransitionState(EnemyStateType.Hit);
        }


        if(info.normalizedTime >= .95f)
        {
            manager.TransitionState(EnemyStateType.EnemyChase);
        }
    }
    public void OnExit()
    {

    }

    
}
public class AttackState : EnemyIState
{
    private EnemyFSM manager;
    private Parameter parameter;

    private AnimatorStateInfo info;

    public AttackState(EnemyFSM manager)
    {
        this.manager = manager;
        this.parameter = manager.parameter;
    }

    public void OnEnter()
    {
        parameter.animator.Play("Attack");
        parameter.audioenemy.AudioAttack();

    }
    public void OnUpdate()
    {
        info = parameter.animator.GetCurrentAnimatorStateInfo(0);

        /////////测试 hit death的
        if(parameter.getHit) //转换Hit状态
        {
            manager.TransitionState(EnemyStateType.Hit);
        }


        if(info.normalizedTime >= .95f)
        {
            manager.TransitionState(EnemyStateType.EnemyChase);
        }
    }
    public void OnExit()
    {

    }
    
}

public class HitState : EnemyIState
{
    private EnemyFSM manager;
    private Parameter parameter;

    private AnimatorStateInfo info;

    public HitState(EnemyFSM manager)
    {
        this.manager = manager;
        this.parameter = manager.parameter;
    }

    public void OnEnter()
    {
        parameter.animator.Play("Hit");
        parameter.audioenemy.Audiohit();

    }
    public void OnUpdate()
    {
        info = parameter.animator.GetCurrentAnimatorStateInfo(0);
        if(info.normalizedTime >= .95f)
        {
        // if(parameter.chara.currentHealth<=0)
        // {
        //     manager.TransitionState(EnemyStateType.Death);
        // }
        // else
        // {
            ///锁定玩家
            parameter.target = GameObject.FindWithTag("Player").transform;

            manager.TransitionState(EnemyStateType.EnemyChase);
        // }
        }
      
    }
    public void OnExit()
    {
        parameter.getHit = false;
    }
}

public class DeathState : EnemyIState
{
    private EnemyFSM manager;
    private Parameter parameter;

    private AnimatorStateInfo info;

    public DeathState(EnemyFSM manager)
    {
        this.manager = manager;
        this.parameter = manager.parameter;
    }

    public void OnEnter()
    {
        parameter.animator.Play("Death");
        
    }
    public void OnUpdate()
    {
        info = parameter.animator.GetCurrentAnimatorStateInfo(0);
        if (info.normalizedTime >= .9f)
        {
            manager.enemyDestroy();
        }
    }
    public void OnExit()
    {

    }
}


public class ERedState : EnemyIState
{
    private EnemyFSM manager;
    private Parameter parameter;

    private float time;

    private AnimatorStateInfo info;

    public ERedState(EnemyFSM manager)
    {
        this.manager = manager;
        this.parameter = manager.parameter;
    }

    public void OnEnter()
    {
        time = 0.5f;
        parameter.animator.Play("Hit");
        parameter.chara.currentHealth -= 200;
    }
    public void OnUpdate()
    {
        time -= Time.deltaTime;
        if (time <= 0)
        {
            manager.TransitionState(EnemyStateType.EnemyIdle);
        }
    }
    public void OnExit()
    {

    }


}


public class EBlueState : EnemyIState
{
    private EnemyFSM manager;
    private Parameter parameter;

    private float time;

    private AnimatorStateInfo info;

    public EBlueState(EnemyFSM manager)
    {
        this.manager = manager;
        this.parameter = manager.parameter;
    }

    public void OnEnter()
    {
        time = 10;
        parameter.animator.Play("Blue");
    }
    public void OnUpdate()
    {
        time -= Time.deltaTime;
        if (time <= 0)
        {
            
            manager.TransitionState(EnemyStateType.EnemyIdle);

        }
    }
    public void OnExit()
    {

    }


}



