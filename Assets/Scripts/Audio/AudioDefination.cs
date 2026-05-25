using System.Collections;
using System.Collections.Generic;
using UnityEngine;
//音频自定义脚本
public class AudioDefination : MonoBehaviour
{
    public PlayAudioEventSO playAudioEvent;
    public AudioClip audioClip;
    public bool playOnEnable;

    private void OnEnable()
    {
        if (playOnEnable)
            PlayAudioClip();
    }

    public void PlayAudioClip()
    {
        playAudioEvent.RaiseEvent(audioClip);
    }
}
