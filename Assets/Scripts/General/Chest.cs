using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Chest : MonoBehaviour, IInteractable
{
    private SpriteRenderer spriteRenderer;
    public Sprite openSprite;
    public Sprite closeSprite;
    public bool isDone;
    public Character c;
    public GameObject Player;
    private bool b;
    private void Awake()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
        b = false;
    }

    private void Update()
    {
        
        if (b)
        {
            c = GameObject.Find("HeroPlayer")?.GetComponent<Character>();
            if (c != null)
            {
                c.currentHealth += Time.deltaTime * 100;
                if(c.currentHealth >= c.maxHealth)
                {
                    c.currentHealth = c.maxHealth;
                    b = false;
                }
            } 
        }
    }


    private void OnEnable()
    {
        spriteRenderer.sprite = isDone ? openSprite : closeSprite;
    }
    public void TriggerAction()
    {
        Debug.Log("¿ªÆô±¦Ïä");
        if (!isDone)
        {
            OpenChest();
        }
    }
    public void OpenChest()
    {
        
        spriteRenderer.sprite = openSprite;
        isDone = true;
        this.gameObject.tag = "Untagged";
        b = true;
    }
}
