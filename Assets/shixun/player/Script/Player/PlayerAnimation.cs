using System.Collections;
using System.Collections.Generic;
using Unity.Mathematics;
using UnityEngine;

public class PlayerAnimation : MonoBehaviour
{
    private Animator animator;

    private Rigidbody2D rg;

    private PlayControl playControl;

    private Character character;

    private void Awake()
    {
        animator = GetComponent<Animator>();
        rg = GetComponent<Rigidbody2D>();
        playControl = GetComponent<PlayControl>();
        character = GetComponent<Character>();
    }

    private void Update()
    {
        SetAnimation();
    }

    public void SetAnimation()
    {
        animator.SetFloat("run", Mathf.Abs(rg.velocity.x));
        animator.SetFloat("jump", rg.velocity.y);
        animator.SetBool("isCollider", playControl.isGround);
        animator.SetBool("static", character.invulnerable);
        animator.SetBool("isDead", playControl.isDead);
        animator.SetBool("isAttack", playControl.isAttack);
        animator.SetBool("isWall_Forward", playControl.isWall_Forward&&(!playControl.isGround));
        animator.SetBool("defensePrefect", playControl.defensePrefect);
        //animator.SetBool("isGround",playControl.isGround);
    }

    public void PlayHurt()
    {
        animator.SetTrigger("hurt");
    }

    public void PlayAttack()
    {
        animator.SetTrigger("attack");
    }

    public void PlayDefense()
    {
        animator.SetTrigger("defense");
    }

    public void PlayDodge()
    {
        animator.SetTrigger("dodge");
    }

    public void PlaySkill01()
    {
        animator.SetBool("skill01", true);
    }

    public void PlaySkill02()
    {
        animator.SetBool("skill02", true);
    }

    public void ColorChange(ColorType color)  //技能动画buffer颜色的改变
    {
        animator.SetInteger("color", (int)color);
    }
}
