using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class controlWater : MonoBehaviour
{
    private AttackWater attack;

    public float timeMax;

    public float time;

    public bool abool;


    private void Awake() {
        abool = true;
        attack = GetComponent<AttackWater>();
        time = timeMax;
    }

    private void Update() {
        if(!abool){
            time -= Time.deltaTime;
        }
        if(time <= 0){
            abool = true;
            time = timeMax;
        }
    }

}
