using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// 三消UI
/// </summary>
public class ColorList : MonoBehaviour
{
    public ColorBuffer[] colorList;

    private SpriteRenderer[] spritColor;

    public float addY;///与三消显示UI的跟随对象保持的高度

    public GameObject manage;  ///三消显示UI的跟随对象

    private void Awake()
    {
        spritColor = GetComponentsInChildren<SpriteRenderer>();
        colorList = new ColorBuffer[transform.childCount];
       for (int i=0;i< colorList.Length; i++)
        {
            colorList[i] = transform.GetChild(i).GetComponentInChildren<ColorBuffer>(); //获取子组件的ColorBuffer内容，加入到列表

            colorList[i].SetColor(ColorType.EMPTY);      //设置ColorBuffer的初始状态


        }
    }

    private void Update()
    {
        if (manage == null)
        {
            Destroy(this.gameObject);
        }
        else
        {
            transform.position = new Vector2(manage.transform.position.x, manage.transform.position.y+ addY);
            for (int i = 0; i < spritColor.Length; i++)
            {
                spritColor[i].color = new Color(spritColor[i].color.r, spritColor[i].color.g, spritColor[i].color.b, manage.GetComponent<SpriteRenderer>().color.a);//使三消UI的透明度与对象保持一致
            }

        }
    }
}
