using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HurtAnimation : StateMachineBehaviour
{


    // OnStateEnter is called when a transition starts and the state machine starts to evaluate this state
    //override public void OnStateEnter(Animator animator, AnimatorStateInfo stateInfo, int layerIndex)
    //{
    //    //animator.GetComponent<PlayControl>().setRb(Vector2.zero);
    //}

    // OnStateUpdate is called on each Update frame between OnStateEnter and OnStateExit callbacks
    override public void OnStateUpdate(Animator animator, AnimatorStateInfo stateInfo, int layerIndex)
    {
        //animator.GetComponent<PlayControl>().setRb(Vector2.zero);
        animator.GetComponent<Animator>().SetBool("isAttack", false);
        animator.GetComponent<Animator>().SetBool("skill01", false);
        animator.GetComponent<Animator>().SetBool("skill02", false);
    }

    // OnStateExit is called when a transition ends and the state machine finishes evaluating this state
    override public void OnStateExit(Animator animator, AnimatorStateInfo stateInfo, int layerIndex)
    {
        animator.GetComponent<PlayControl>().isHurt = false;
        animator.GetComponent<PlayControl>().isSkill = false;
    }

    // OnStateMove is called right after Animator.OnAnimatorMove()
    //override public void OnStateMove(Animator animator, AnimatorStateInfo stateInfo, int layerIndex)
    //{
    //    // Implement code that processes and affects root motion
    //}

    // OnStateIK is called right after Animator.OnAnimatorIK()
    //override public void OnStateIK(Animator animator, AnimatorStateInfo stateInfo, int layerIndex)
    //{
    //    // Implement code that sets up animation IK (inverse kinematics)
    //}
}
