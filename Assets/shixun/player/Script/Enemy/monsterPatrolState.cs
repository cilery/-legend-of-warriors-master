using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using static UnityEngine.RuleTile.TilingRuleOutput;

public class monsterPatrolState : BaseState
{
    public override void OnEnter(Enemy enemy)
    {
        currentEnemy = enemy;
    }

    public override void LogicUpdate()
    {
        if (currentEnemy.isWall_Forward || !currentEnemy.isGround)
        {
            currentEnemy.wait = true;
        }
    }

    public override void PhysicsUpdate()
    {
        
    }

    public override void OnExit()
    {

    }
}
