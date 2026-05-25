using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;

//场景互动控制
public class Sign : MonoBehaviour
{
    private PlayerInputControl playerInput;
    public GameObject signSprite;
    private IInteractable targetItem;//获得的物体
    private bool canPress;
    private  Animator anim;
    public Transform playerTrans;

    private void Awake() 
    {
        //anim = GetComponentInChildren<Animator>();
        anim = signSprite.GetComponent<Animator>();

        playerInput = new PlayerInputControl();
        playerInput.Enable();//启动
    }
    private void OnEnable()
    {
        InputSystem.onActionChange += OnActionChange;
        playerInput.GamePlayer.Confirm.started += OnConfirm;

    }
    private void OnDisable()
    {
        canPress = false;
    }
    private void OnConfirm(InputAction.CallbackContext obj)
    {
        if (canPress)
        {
            targetItem.TriggerAction();
            GetComponent<AudioDefination>().PlayAudioClip();
        }
    }


    //切换设备
    private void OnActionChange(object obj, InputActionChange actionChange)
    {
        if (actionChange == InputActionChange.ActionStarted)
        {
            //Debug.Log(((InputAction)obj).activeControl.device );

            var d = ((InputAction)obj).activeControl.device;
            switch (d.device)
            {
                case Keyboard:
                    anim.Play("keyboard");
                    break;

            }
        }
    }
    private void OnTriggerStay2D(Collider2D collision)
    {
        if (collision.CompareTag("Interactable"))
        {            
            canPress = true;
            targetItem = collision.GetComponent<IInteractable>();
        }

    }
    private void OnTriggerExit2D(Collider2D collision)
    {
        canPress = false;
    }
    private void Update()
    {
        signSprite.GetComponent<SpriteRenderer>().enabled = canPress;
        signSprite.transform.localScale = playerTrans.localScale;
    }
  
    
}
