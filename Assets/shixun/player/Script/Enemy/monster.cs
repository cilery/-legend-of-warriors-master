using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class monster : Enemy
{
    public override void Move()
    {
        if(isGround && !wait)
            base.Move();
        animator.SetBool("run", !invulnerable);
    }
}
