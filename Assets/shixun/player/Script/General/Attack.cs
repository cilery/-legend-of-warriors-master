using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.TextCore.Text;

public class Attack : MonoBehaviour
{
    public float damage; ///�˺�

    public float attackRange;

    public float attackRate;

    private void OnTriggerEnter2D(Collider2D collision)
    {
        collision.GetComponent<Character>()?.TakeDamage(this);
        if (collision.CompareTag("enemy") || collision.CompareTag("Boss"))
        {
            frameFroze.Instance.HitPause(GameObject.FindWithTag("Player").GetComponentInParent<FrozeDate>().attackPause);
            frameFroze.Instance.shakeCamera();
        }
    }

  

}
