using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using UnityEngine.InputSystem;

public class UIManager : MonoBehaviour
{
    public PlayerStatBar playerStatBar;

    [Header("事件监听")]
    public CharacterEventSO healthEvent;
    public SceneLoadEventSO unloadedSceneEvent;
    public VoidEventSO loadDataEvent;
    public VoidEventSO gameOverEvent;
    public VoidEventSO backToMenuEvent;
    public FloatEventSO syncVolumeEvent;

    [Header("广播")]
    public VoidEventSO pauseEvent;

    [Header("组件")]
    public GameObject gameOverPanel;
    public GameObject restartBin;
    public Button settingsBtn;
    public GameObject pausePanel;
    public Slider volumeSlider;
    public Image Skill01_image;
    public Image Skill02_image;
    private void Awake()
    {
        settingsBtn.onClick.AddListener(TogglePausePanel);
    }

    private void OnEnable()
    {
        healthEvent.OnEventRaised += OnHealthEvent;
        unloadedSceneEvent.LoadRequestEvent += OnUnloadedSceneEvent;
        loadDataEvent.OnEventRaised += OnLoadDataEvent;
        gameOverEvent.OnEventRaised += OnGameOverEvent;

        loadDataEvent.OnEventRaised += TogglePausePanel2;
        backToMenuEvent.OnEventRaised += TogglePausePanel2;

        backToMenuEvent.OnEventRaised += OnLoadDataEvent;
        syncVolumeEvent.OnEventRaised += OnSyncVolumeEvent;
    }

    private void Update()
    {
        if (Keyboard.current.escapeKey.wasPressedThisFrame)
        {
            TogglePausePanel();
        }

        if(GameObject.Find("HeroPlayer")?.GetComponent<PlayControl>() != null)
        {
            Skill01();
            Skill02();
        }
    }

    private void OnDisable()
    {
        healthEvent.OnEventRaised -= OnHealthEvent;
        unloadedSceneEvent.LoadRequestEvent -= OnUnloadedSceneEvent;
        loadDataEvent.OnEventRaised -= OnLoadDataEvent;
        gameOverEvent.OnEventRaised -= OnGameOverEvent;

        loadDataEvent.OnEventRaised -= TogglePausePanel2;
        backToMenuEvent.OnEventRaised -= TogglePausePanel2;


        backToMenuEvent.OnEventRaised -= OnLoadDataEvent;
        syncVolumeEvent.OnEventRaised -= OnSyncVolumeEvent;
    }

    private void OnSyncVolumeEvent(float amount)
    {
        volumeSlider.value = (amount + 80) / 100;
    }

    private void TogglePausePanel()
    {
        
        if (pausePanel.activeInHierarchy)
        {
            pausePanel.SetActive(false);
            Time.timeScale = 1;
        }
        else
        {
            pauseEvent.RaiseEvent();
            pausePanel.SetActive(true);
            Time.timeScale = 0;
        }
    }

    private void TogglePausePanel2()
    {
        //pauseEvent.RaiseEvent();
        pausePanel.SetActive(false);
        Time.timeScale = 1;
    }

    public void OnGameOverEvent()
    {
        gameOverPanel.SetActive(true);
        EventSystem.current.SetSelectedGameObject(restartBin);
    }

    public void OnLoadDataEvent()
    {
        gameOverPanel.SetActive(false);
    }

    private void OnUnloadedSceneEvent(GameSceneSO sceneToLoad, Vector3 arg1, bool arg2)
    {
        var isMenu = sceneToLoad.sceneType == SceneType.Menu;
        playerStatBar.gameObject.SetActive(!isMenu);
    }

    private void OnHealthEvent(Character character)
    {
        var healthpersentage = character.currentHealth / character.maxHealth;
        playerStatBar.OnHealthChange(healthpersentage);
    }

    private void Skill01()
    {
        
        PlayControl gameObject = GameObject.Find("HeroPlayer")?.GetComponent<PlayControl>();
        
        float skill01persentage = gameObject.invulnerableCounterSkill01 / gameObject.invulnerableDurationSkill01;
        Skill01_image.fillAmount = skill01persentage;
    }

    private void Skill02()
    {
        PlayControl gameObject = GameObject.Find("HeroPlayer")?.GetComponent<PlayControl>();
        float skill02persentage = gameObject.invulnerableCounterSkill02 / gameObject.invulnerableDurationSkill02;
        Skill02_image.fillAmount = skill02persentage;
    }
}
