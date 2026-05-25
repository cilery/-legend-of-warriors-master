using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// 三消元素
/// </summary>
public class ColorBuffer : MonoBehaviour
{
   

    [System.Serializable]
    public struct ColorSprite
    {
        public ColorType color;
        public Sprite sprite;
        public GameObject explosionEffect;
    }

    public ColorSprite[] ColorSprites;

    private Dictionary<ColorType, Sprite> colorSpriteDict;
    private Dictionary<ColorType, GameObject> colorEffectDict;

    private SpriteRenderer sprite;
    public int NumColors
    {
        get
        {
            return ColorSprites.Length;

        }
    }

    public ColorType Color { get => color; set => SetColor(value); }

    private ColorType color;
    private void Awake()
    {
        sprite = transform.Find("color").GetComponent<SpriteRenderer>();
        colorSpriteDict = new Dictionary<ColorType, Sprite>();
        colorEffectDict = new Dictionary<ColorType, GameObject>();
        for (int i = 0; i < ColorSprites.Length; i++)
        {
            if (!colorSpriteDict.ContainsKey(ColorSprites[i].color))//containsKey方法用来判断Map集合对象中是否包含指定的键名。
            {
                colorSpriteDict.Add(ColorSprites[i].color, ColorSprites[i].sprite);
               
            }

          
        }

        for (int i = 0; i < ColorSprites.Length; i++)
        {
            if (!colorEffectDict.ContainsKey(ColorSprites[i].color))//containsKey方法用来判断Map集合对象中是否包含指定的键名。
            {
                colorEffectDict.Add(ColorSprites[i].color, ColorSprites[i].explosionEffect);

            }

           
        }
    }


    public void SetColor(ColorType newColor)
    {
       
        if (colorSpriteDict.ContainsKey(newColor))
        {
            sprite.sprite = colorSpriteDict[newColor];
        }
      
    }

    public void playEffect(ColorType newColor)
    {
        if (colorEffectDict.ContainsKey(newColor))
        {
            colorEffectDict[newColor].GetComponent<ParticleSystem>().Play();
        }

    }

}
