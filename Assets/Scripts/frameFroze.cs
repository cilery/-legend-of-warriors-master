using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class frameFroze : MonoBehaviour
{
    private static frameFroze instance;
    public Cinemachine.CinemachineImpulseSource impulseSource;
    public static frameFroze Instance
    {
        get
        {
            if (instance == null)
            {
                instance = Transform.FindAnyObjectByType<frameFroze>();
            }
            return instance;


        }

    }
    private bool isShake;

    public void HitPause(int duration)
    {
        StartCoroutine(Pause(duration));

    }
    IEnumerator Pause(int duration)
    {
        float pauseTime = duration / 60f;
        Time.timeScale = 0;
        yield return new WaitForSecondsRealtime(pauseTime);
        Time.timeScale = 1;
    }
   
    public void shakeCamera()
    {
        impulseSource.GenerateImpulse();
    }
   
}
