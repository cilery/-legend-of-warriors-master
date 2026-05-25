using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AudioEnemy : MonoBehaviour
{
    public AudioClip Attack;
    public AudioClip hit;

    public void AudioAttack()
    {
        this.GetComponent<AudioSource>().clip = Attack;
        this.GetComponent<AudioSource>().Play();
    }
    public void Audiohit()
    {
        this.GetComponent<AudioSource>().clip = hit;
        this.GetComponent<AudioSource>().Play();
    }

    
}
