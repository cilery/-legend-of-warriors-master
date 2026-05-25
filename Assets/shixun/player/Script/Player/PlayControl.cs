using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.InputSystem;

public class PlayControl : MonoBehaviour
{
    [Header("监听事件")]
    public SceneLoadEventSO sceneLoadEvent;
    public VoidEventSO afterSceneLoadedEvent;
    public VoidEventSO loadDataEvent;
    public VoidEventSO backToMenuEvent;

    [Header("״̬")]
    public PlayerInputControl inputControl;
    public Vector2 inputDirection;
    public float speed;
    public float jumpForce;
    public float dodgeForce;
    public bool isDead;

    private Rigidbody2D rb;
    private PlayerAnimation pa;

    [Header("��ײ")]
    public bool isGround;
    public bool isWall_Forward;
    public bool isWall_Back;
    public bool isAttack;
    public bool isHurt;
    public bool isDefense;
    public bool isDodge;
    public float hurtForce;
    public bool defensePrefect;

    [Header("��ȡ")]
    public GameObject ground;
    public GameObject wall_Forward;
    public GameObject wall_Back;

    [Header("����")]
    public bool isSkill;
    public bool invulnerableSkill01;
    public bool invulnerableSkill02;
    public float skillForce;
    public float invulnerableDurationSkill01;
    public float invulnerableCounterSkill01;
    public float invulnerableDurationSkill02;
    public float invulnerableCounterSkill02;
    private Invulner invulnerSkill01;
    private Invulner invulnerSkill02;
    private Transform[] m;
    public ColorType color;
    public ColorBuffer buffer;
    private void Awake(){
        isDead = false;
        isHurt = false;
        isAttack = false;
        isDefense = false;
        defensePrefect = false;
        isSkill = false;
        invulnerSkill01 = new Invulner();
        invulnerSkill02 = new Invulner();
        invulnerSkill01.invulnerableDuration = invulnerableDurationSkill01;
        invulnerSkill02.invulnerableDuration = invulnerableDurationSkill02;
        m = GetComponentsInChildren<Transform>();
        rb = this.GetComponent<Rigidbody2D>();
        pa = this.GetComponent<PlayerAnimation>();
        inputControl = new PlayerInputControl();
        inputControl.GamePlayer.Jump.started += Jump;
        inputControl.GamePlayer.Attack.started += Attack;
        inputControl.GamePlayer.Defense.started += Defense;
        inputControl.GamePlayer.Dodge.started += Dodge;
        inputControl.GamePlayer.SKill01.started += Skill01;
        inputControl.GamePlayer.Skill02.started += Skill02;
        inputControl.Enable();
        color = (ColorType)Random.Range(0, 3);
    }

    private void Attack(InputAction.CallbackContext obj)
    {

        if (isHurt || isDefense || isDodge || isSkill || isWall_Forward)
            return;
        rb.velocity = Vector2.zero;
        isAttack = true;
        pa.PlayAttack();
        color = (ColorType)Random.Range(0, 3);

    }

    private void Defense(InputAction.CallbackContext obj)
    {
        if (isHurt || isAttack || isDodge || isDefense || isSkill)
            return;
        isDefense = true;
        rb.velocity = Vector2.zero;
        pa.PlayDefense();
    }

    public void Dodge(InputAction.CallbackContext obj)
    {
        if (isHurt || isDodge || isAttack || isDefense || isSkill)
            return;
        isDodge = true;
        rb.velocity = Vector2.zero;
        Vector2 dir = new Vector2(transform.localScale.x, 0).normalized;
        //Debug.Log(dir);
        rb.AddForce(dir * dodgeForce, ForceMode2D.Impulse);
        pa.PlayDodge();
    }

    private void Jump(InputAction.CallbackContext obj){
        if (isGround || isWall_Forward)
        {
            rb.velocity = Vector2.zero;
            rb.AddForce(transform.up * jumpForce, ForceMode2D.Impulse);
        }
    } 

    private void Skill01(InputAction.CallbackContext obj)
    {
        if (isHurt || isDodge || isAttack || isDefense || invulnerSkill01.invulnerable)
            return;
        isSkill = true;
        invulnerSkill01.TriggerInvulnerable();
        pa.PlaySkill01();
    }

    public void Skill01_2()
    {
        rb.velocity = Vector2.zero;
        Vector2 dir = new Vector2(transform.localScale.x, 0).normalized;
        rb.AddForce(dir * skillForce, ForceMode2D.Impulse);
    }

    private void Skill02(InputAction.CallbackContext obj)
    {
        if (isHurt || isDodge || isAttack || isDefense || invulnerSkill02.invulnerable)
            return;
        rb.velocity = Vector2.zero;
        isSkill = true;
        invulnerSkill02.TriggerInvulnerable();
        pa.PlaySkill02();
    }

    private void OnEnable(){
        //inputControl.Enable();
        sceneLoadEvent.LoadRequestEvent += OnLoadEvent;
        afterSceneLoadedEvent.OnEventRaised += OnAfterSceneLoadedEvent;
        loadDataEvent.OnEventRaised += OnLoadDataEvent;
        backToMenuEvent.OnEventRaised += OnLoadDataEvent;
    }

    private void OnDisable(){
        inputControl.Disable();
        sceneLoadEvent.LoadRequestEvent -= OnLoadEvent;
        afterSceneLoadedEvent.OnEventRaised -= OnAfterSceneLoadedEvent;
        loadDataEvent.OnEventRaised -= OnLoadDataEvent;
        backToMenuEvent.OnEventRaised -= OnLoadDataEvent;
    }


    public void Update()
    {
        inputDirection = inputControl.GamePlayer.Move.ReadValue<Vector2>();
        inputDirection.x = inputDirection.x == 0 ? 0 : Mathf.Abs(inputDirection.x) / inputDirection.x;
        inputDirection.y = inputDirection.y == 0 ? 0 : Mathf.Abs(inputDirection.y) / inputDirection.y;
        
        //��ײ
        isGround = ground.GetComponent<PhysicCheck>().check();
        isWall_Forward = wall_Forward.GetComponent<PhysicCheck>().check();
        //isWall_Back = wall_Back.GetComponent<PhysicCheck>().isCollider;

        //��ʱ

        //skill01
        invulnerSkill01.updateIn();
        invulnerableSkill01 = invulnerSkill01.invulnerable;
        invulnerableCounterSkill01 = invulnerSkill01.invulnerableCounter;

        //skill02
        invulnerSkill02.updateIn();
        invulnerableSkill02 = invulnerSkill02.invulnerable;
        invulnerableCounterSkill02 = invulnerSkill02.invulnerableCounter;



        pa.ColorChange(color);
        if (buffer.gameObject.activeInHierarchy == true)
        {
            buffer.SetColor(color);
        }

        //Debug.Log(isHurt);
    }

    private void FixedUpdate(){
        if(!isHurt && !isAttack && !isDefense && !defensePrefect && !isDodge && !isSkill)
            Move();
    }

    //场景加载过程停止控制
    private void OnLoadEvent(GameSceneSO arg0, Vector3 arg1, bool arg2)
    {
        inputControl.GamePlayer.Disable();
    }
    private void OnLoadDataEvent()
    {
        //isDead = false;
        PlayBack();
    }

    //加载结束后启动控制
    private void OnAfterSceneLoadedEvent()
    {
        inputControl.GamePlayer.Enable();
    }


    public void Move(){
        rb.velocity = new Vector2(inputDirection.x * speed * Time.deltaTime, rb.velocity.y);
        if(inputDirection.x > 0)
            transform.localScale = new Vector3(1, 1, 1);
        else if(inputDirection.x < 0)
            transform.localScale = new Vector3(-1, 1, 1);
    }

    public void GetHurt(Transform tf)
    {
        isHurt = true;
        rb.velocity = Vector2.zero;
        Vector2 dir = new Vector2(tf.position.x - transform.position.x, 0).normalized;
        //Debug.Log(dir);
        rb.AddForce(dir * hurtForce, ForceMode2D.Impulse);
    }

    public void PlayDead()
    {
        isDead = true;
        inputControl.GamePlayer.Disable();
        //Debug.Log(1);
    }

    private void PlayBack()
    {
        isDead = false;
        //inputControl.GamePlayer.Enable();
    }

    public void setRb(Vector2 vector2)
    {
        rb.velocity = vector2;
    }

    public void Invulnerable()
    {
        invulnerSkill01.invulnerable = false;
    }
}
