using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// 控制技能释放出的预制体
/// </summary>
public class cotrolPrefabs : MonoBehaviour
{
    // Start is called before the first frame update

    public float time =1;
    void Start()
    {
       
    }

    // Update is called once per frame
    void Update()
    {
        time -= Time.deltaTime;

        if (time <= 0)
        {
           
            Destroy(this.gameObject);
        }
    }
}
