using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

public class Character : MonoBehaviour,ISaveable
{
    [Header("事件监听")]
    public VoidEventSO newGameEvent;

    [Header("基本属性")]
    public float maxHealth;
    public float currentHealth;

    [Header("受伤无敌")]

    public bool invulnerable;
    public float invulnerableDuration;
    public float invulnerableCounter;
    [HideInInspector] public Invulner invulner;//��ʱ��

    public UnityEvent<Character> OnHealthChange;
    public UnityEvent<Transform> OnTakeDamage;


    public UnityEvent OnDie;

    private void NewGame()
    {
        currentHealth = maxHealth;
        //currentPower = maxPower;
        OnHealthChange?.Invoke(this);
    }

    //private void Start()
    //{
    //    currentHealth = maxHealth;
    //}

    private void OnEnable()
    {
        newGameEvent.OnEventRaised += NewGame;
        ISaveable saveable = this;
        saveable.RegisterSaveData();
    }

    private void OnDisable()
    {
        newGameEvent.OnEventRaised -= NewGame;
        ISaveable saveable = this;
        saveable.UnRegisterSaveData();
    }

    private void Awake() 
    {
        invulner = new Invulner();
        invulner.invulnerableDuration = invulnerableDuration;
        currentHealth = maxHealth;
    }

    private void Update()
    {
        OnHealthChange?.Invoke(this);
        invulner.updateIn();
        invulnerableCounter = invulner.invulnerableCounter;
        invulnerable = invulner.invulnerable;
        //if (currentHealth > 0 && GameObject.Find("SceneLoad Manager").GetComponent<SceneLoader>().GetGameStart())
        //{
        //    this.GetComponent<PlayControl>()?.PlayBack();
        //}
    }
   
    public void TakeDamage(Attack attack)
    {
        Debug.Log(321);
        if (invulner.invulnerable)
            return;
        if(currentHealth > attack.damage)
        {
            currentHealth = currentHealth - attack.damage;
            invulner.TriggerInvulnerable();
            OnTakeDamage?.Invoke(attack.transform);
        }
        else
        {
            currentHealth = 0;
            OnDie?.Invoke();
        }
    }

    public void TakeDamageWater(AttackWater attack)
    {
        if (invulner.invulnerable)
            return;
        if(currentHealth > attack.damage)
        {
            currentHealth = currentHealth - attack.damage;
            invulner.TriggerInvulnerable();
            OnTakeDamage?.Invoke(attack.transform);
        }
        else
        {
            currentHealth = 0;
            OnDie?.Invoke();
        }
    }

    public DataDefination GetDataID()
    {
        return GetComponent<DataDefination>();
    }

    public void GetSaveData(Data data)
    {
        if (data.characterPosDict.ContainsKey(GetDataID().ID))
        {
            data.characterPosDict[GetDataID().ID] = new SerializeVector3(transform.position);
            data.floatSavedData[GetDataID().ID + "health"] = this.currentHealth;
        }
        else
        {
            data.characterPosDict.Add(GetDataID().ID, new SerializeVector3(transform.position));
            data.floatSavedData.Add(GetDataID().ID + "health", this.currentHealth);
        }
    }

    public void LoadData(Data data)
    {
        if (data.characterPosDict.ContainsKey(GetDataID().ID))
        {
            this.currentHealth = data.floatSavedData[GetDataID().ID + "health"];
            transform.position = data.characterPosDict[GetDataID().ID].ToVector3();
            Debug.Log("角色" + transform.position);
            //通知UI更新
            OnHealthChange?.Invoke(this);
        }
    }
}
