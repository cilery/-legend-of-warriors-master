using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class findPlayer : MonoBehaviour
{
   public EnemyFSM en;
    private void OnTriggerEnter2D(Collider2D other) {
       
        if(other.CompareTag("Player"))//判断进入的标签是不是玩家
        {
            en.parameter.target = other.transform;   //把玩家的Tranform 赋予给target让敌人知道玩家位置
           
        }
         Debug.Log(1);
    }
    private void OnTriggerExit2D(Collider2D other) {
        if(other.CompareTag("Player"))
        {
            en.parameter.target = null; //退出范围时重置为空
        }
    }

    private void OnDrawGizmos() {
        Gizmos.DrawWireSphere(en.parameter.attackPoint.position,en.parameter.attackArea);//绘制一个空心圆
        
    }
}
