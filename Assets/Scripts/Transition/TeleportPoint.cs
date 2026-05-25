using System.Collections;
using System.Collections.Generic;
using UnityEngine;
//勧僕重云 
public class TeleportPoint : MonoBehaviour, IInteractable
{
    public SceneLoadEventSO loadEventSO;
    public GameSceneSO sceneToGo; 
    public Vector3 positionToGo;
    public void TriggerAction()
    {
        Debug.Log("勧僕");
        loadEventSO.RaiseLoadRequestEvent(sceneToGo, positionToGo, true);
    }
}
