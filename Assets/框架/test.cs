using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class test : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetMouseButtonDown(0))
        {
            GameObject obj = ResMgr.GetInstance().Load<GameObject>("");
                obj.transform.localScale = Vector3.one * 2;
        }

        if (Input.GetMouseButtonDown(1))
        {
            ResMgr.GetInstance().LoadAsync<GameObject>("", (obj) => { obj.transform.localScale = Vector3.one * 2; });
        }
    }
}
