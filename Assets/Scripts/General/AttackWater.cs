using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AttackWater : MonoBehaviour
{
    public float damage;


    private void OnTriggerStay2D(Collider2D collision)
    {
        if(collision.GetComponent<Character>() == null)
        {
            Debug.Log(collision.name);
        }
        if (this.GetComponent<controlWater>().abool)
        {

            collision.GetComponent<Character>()?.TakeDamageWater(this);
            Debug.Log("在水里");
            this.GetComponent<controlWater>().abool = false;
        }
        

    }
    
}
