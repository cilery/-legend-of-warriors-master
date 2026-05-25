using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Defense : MonoBehaviour
{
    public BossFSM boss;
    public GameObject Player;
    private PlayControl playControl;
    private Animator animator;
    private void Awake()
    {
        
        animator = Player.GetComponent<Animator>();
        playControl = Player.GetComponent<PlayControl>();
    }

    private void OnTriggerEnter2D(Collider2D collision)
    {
        if(collision.gameObject.CompareTag("enemyAttack"))
        {
           
            playControl.defensePrefect = true;
            animator.SetBool("defensePrefect", true);
           


        }
     
    }
}
