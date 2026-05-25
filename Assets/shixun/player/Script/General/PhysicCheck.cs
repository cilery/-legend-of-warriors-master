using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PhysicCheck : MonoBehaviour
{
    public LayerMask layerMask;
    public bool isCollider = true;
    //public float checkRaduis;
    //public void Update(){
    //    check();
    //}

    public bool check()
    {
      
        //isGround = Physics2D.OverlapCircle(transform.position, checkRaduis, layerMask);
        isCollider = this.GetComponent<BoxCollider2D>().IsTouchingLayers(layerMask);
        //GameObject.Find("HeroPlayer").GetComponent<PlayControl>().isCollider = isCollider;
        return isCollider;
        //bool i = GameObject.Find("HeroPlayer").GetComponent<PlayControl>().isCollider;
        //GameObject.Find("HeroPlayer").GetComponent<PlayControl>().isCollider = isCollider;
    }

}
