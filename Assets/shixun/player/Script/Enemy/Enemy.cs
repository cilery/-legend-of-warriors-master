using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;

public class Enemy : MonoBehaviour
{
    Rigidbody2D rb;
    protected Animator animator;

    [Header("速度")]
    public float normalSpeed;
    public float chaseSpeed;
    public float currentSpeed;
    public Vector3 faceDir;

    [Header("碰撞")]
    public bool isGround;
    public bool isWall_Forward;
    public bool isWall_Back;
    public bool isHurt;
    public bool isDead;
    public float hurtForce;
    public bool wait;

    [Header("拉取")]
    public GameObject ground;
    public GameObject wall_Forward;
    public GameObject wall_Back;

    [Header("计时器")]
    public bool invulnerable;
    public float invulnerableDuration;
    public float invulnerableCounter;
    [HideInInspector] public Invulner invulner;//计时器

    private Vector3 i;
    private BaseState baseState;

    private void Awake()
    {
        invulner = new Invulner();
        isGround = true;
        isWall_Forward = false;
        wait = false;
        isHurt = false;
        isDead = false;
        rb = transform.parent.GetComponent<Rigidbody2D>();
        animator = GetComponent<Animator>();
        currentSpeed = normalSpeed;
        invulner.invulnerableDuration = invulnerableDuration;
    }

    private void OnEnable()
    {
        baseState = new monsterPatrolState();
        baseState.OnEnter(this);
    }

    private void Update()
    {
        faceDir = new Vector3(-transform.parent.localScale.x, 0, 0);

        ////碰撞
        isGround = ground.GetComponent<PhysicCheck>().check();
        isWall_Forward = wall_Forward.GetComponent<PhysicCheck>().check();
        //isWall_Back = wall_Back.GetComponent<PhysicCheck>().isCollider;
        invulnerableCounter = invulner.invulnerableCounter;


        //if (isWall_Forward || !isGround)
        //{
        //    invulner.TriggerInvulnerable();
        //    invulner.updateIn();
        //    if (!invulner.invulnerable)
        //    {
        //        transform.parent.localScale = new Vector3(faceDir.x, 1, 1);
        //    }
        //}


        invulnerable = invulner.invulnerable;
        baseState.LogicUpdate();
        waitCounter();
        
    }

    public void waitCounter()
    {
        if (wait)
        {
            invulner.TriggerInvulnerable();
            invulner.updateIn();
            if (!invulner.invulnerable)
            {
                wait = false;
                transform.parent.localScale = new Vector3(faceDir.x, 1, 1);
            }
        }
    }

    private void FixedUpdate()
    {
        baseState.PhysicsUpdate();
        if (!isHurt)
        {
            Move();
        }
        
    }

    private void OnDisable()
    {
        baseState.OnExit();
    }

    public virtual void Move()
    {
        rb.velocity = new Vector2(currentSpeed * faceDir.x * Time.deltaTime, rb.velocity.y);
        if (i == transform.parent.position && !invulnerable)
        {
            rb.AddForce(transform.parent.up * 6, ForceMode2D.Impulse);
        }
        i = transform.parent.position;
        
    }

    public void OnTakeDamage(Transform tf)
    {
        float x = tf.position.x - transform.parent.position.x;
        x = x == 0 ? transform.parent.localScale.x : Mathf.Abs(x) / -x;
        //Debug.Log(x);
        transform.parent.localScale = new Vector3(x, 1, 1);
        isHurt = true;
        animator.SetBool("hurt", true);
        Vector2 dir = new Vector2(x, 0);
        rb.AddForce(dir * hurtForce, ForceMode2D.Impulse);
    }

    public void OnDie()
    {
        gameObject.layer = 2;
        isDead = true;
        animator.SetBool("dead", true);
    }

    public void DestroyAfterAnimation()
    {
        Destroy(this.gameObject);
    }
}
