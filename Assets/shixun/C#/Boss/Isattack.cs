using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// ÅÐ¶ÏÊÇ·ñ½øÈë¹¥»÷·¶Î§
/// </summary>
public class Isattack : MonoBehaviour
{
    private static bool isAttack;


    private static Isattack isattack;

    public static Isattack _Isattack { get => isattack; set => isattack = value; }
    public static bool IsAttack { get => isAttack; set => isAttack = value; }

    private void OnTriggerEnter2D(Collider2D collision)
    {
        if (collision.CompareTag("Player"))
        {
            IsAttack = true;
        }
    }

    private void OnTriggerStay2D(Collider2D collision)
    {
        if (collision.CompareTag("Player"))
        {
            IsAttack = true;
        }
    }
    private void OnTriggerExit2D(Collider2D collision)
    {
        if (collision.CompareTag("Player"))
        {
            IsAttack = false;
        }
    }

    
}
