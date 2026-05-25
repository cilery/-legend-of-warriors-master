using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// 角色对敌人三消元素的添加
/// </summary>
public class testBuffer : MonoBehaviour
{
    private PlayControl play;

    private ColorType newColor;
    private void Awake()
    {


        play = GetComponentInParent<PlayControl>();
       

    }
    void OnTriggerEnter2D(Collider2D other)
    {
      
     

            other.GetComponent<colorWay>().Put(play.color);///调用三消的Put方法


        newColor = (ColorType)Random.Range(0, 3);
        if (play.color == newColor)
        {
            play.Invulnerable();
            play.color = newColor;
        }
        else
        {
             play.color = newColor;
        }
        

    }
}
