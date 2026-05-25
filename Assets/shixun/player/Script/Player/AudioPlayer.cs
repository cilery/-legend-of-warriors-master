using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AudioPlayer : MonoBehaviour
{
    public AudioClip attack1;
    public AudioClip attack2;
    public AudioClip attack3;
    public AudioClip hurt;
    public AudioClip defence;
    public AudioClip defencePrefect;
    public AudioClip dodge;
    public AudioClip jump;
    public AudioClip run;
    public AudioClip skill01;
    public AudioClip skill02;
    public AudioClip clamber;
    public AudioClip ondie;

    public void PlayAudioAttack1()
    {
        this.GetComponent<AudioSource>().clip = attack1;
        this.GetComponent<AudioSource>().Play();
    }
    public void PlayAudioAttack2()
    {
        this.GetComponent<AudioSource>().clip = attack2;
        this.GetComponent<AudioSource>().Play();
    }
    public void PlayAudioAttack3()
    {
        this.GetComponent<AudioSource>().clip = attack3;
        this.GetComponent<AudioSource>().Play();
    }
    public void PlayAudioHurt(){
        this.GetComponent<AudioSource>().clip = hurt;
        this.GetComponent<AudioSource>().Play();
    }

    public void PlayAudioDefence(){
        this.GetComponent<AudioSource>().clip = defence;
        this.GetComponent<AudioSource>().Play();
    }

    public void PlayAudioDefencePrefect()
    {
        this.GetComponent<AudioSource>().clip = defencePrefect;
        this.GetComponent<AudioSource>().Play();
    }

    public void PlayAudioDdodge(){
        this.GetComponent<AudioSource>().clip = dodge;
        this.GetComponent<AudioSource>().Play();
    }

    public void PlayAudioJump(){
        this.GetComponent<AudioSource>().clip = jump;
        this.GetComponent<AudioSource>().Play();
    }

    public void PlayAudioRun()
    {
        this.GetComponent<AudioSource>().clip = run;
        this.GetComponent<AudioSource>().Play();
    }

    public void PlayAudioSkill01(){
        this.GetComponent<AudioSource>().clip = skill01;
        this.GetComponent<AudioSource>().Play();
    }

    public void PlayAudioSkill02(){
        this.GetComponent<AudioSource>().clip = skill02;
        this.GetComponent<AudioSource>().Play();
    }

    public void PlayAudioClamber()
    {
        this.GetComponent<AudioSource>().clip = clamber;
        this.GetComponent<AudioSource>().Play();
    }

    public void PlayAudioOnDie()
    {
        this.GetComponent<AudioSource>().clip = ondie;
        this.GetComponent<AudioSource>().Play();
    }
}
