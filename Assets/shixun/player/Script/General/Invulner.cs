using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Invulner 
{//¼ÆÊ±Æ÷

    public bool invulnerable = false;

    public float invulnerableDuration;

    public float invulnerableCounter = 0;

    public Invulner(float f)
    {
        invulnerableDuration = f;
    }

    public Invulner() { }

    public void updateIn()
    {
        if (invulnerable)
        {
            invulnerableCounter -= Time.deltaTime;
            //invulnerable = invulnerableCounter <= 0 ? false : invulnerable;
            if (invulnerableCounter <= 0)
                invulnerable = false;
        }
    }

    public void TriggerInvulnerable()
    {
        if (!invulnerable)
        {
            invulnerable = true;
            invulnerableCounter = invulnerableDuration;
        }
    }
}
