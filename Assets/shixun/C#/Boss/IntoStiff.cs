using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class IntoStiff : MonoBehaviour
{
    BossFSM mnange;

    private void Awake()
    {
        mnange = GetComponentInParent<BossFSM>();
    }
    private void OnTriggerEnter2D(Collider2D collision)
    {



      
        if (collision.CompareTag("defense"))
        {
            mnange.TransitionState(StateID.Stiff);
        }


    }
}
