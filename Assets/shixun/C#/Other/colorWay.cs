using System.Collections;
using System.Collections.Generic;
using UnityEngine;
/// <summary>
/// 三消机制的实现
/// </summary>
public class colorWay : MonoBehaviour
{

    public List<ColorType> list = new List<ColorType>();

    public GameObject allEnemy;
   

    public ColorList colorList;//机制表达层列表


 
    int same;

   
    public void Put(ColorType color) //压入元素
    {
        


        if (list.Count != 0)         ///当列表不为空时
        {
            if (color == list[list.Count - 1])   ///如果要放进来的元素与表头元素相同时，same值加加
            {
                same++;
                list.Add(color);///加入元素
            }
            else
            {
                same = 1;             ///如果不同 置same为1，代表当前与之相同的元素只有它自己本身。
                list.Add(color);
            }

        }
        else
        {
            same++;  ///当列表为空时，直接插入表头
            list.Add(color);
        }

        Rmove();
      
        for (int i = 0; i < list.Count; i++)
        {

            colorList.colorList[i].SetColor(list[i]);
            colorList.colorList[i].GetComponent<Animator>().Play("bufferIN");

        }
        //if (colorList.colorList.Length >list.Count)
        //{
        //    for (int j =list.Count; j < colorList.colorList.Length; j++)
        //    {
              
        //    }
        //}

    }

    void Rmove() //删除元素
    {
        if (list.Count > 4)          ///限制列表存储元素个数
        {

            list.RemoveAt(0);
        }

        if (same == 3)            /// 当达到3个连续相同的元素时消除
        {
            ColorType color = list[list.Count - 1];
            int count = list.Count;
            same = list.Count - 3;
       
            for (int i = count - 1; i > count - 4; i--)
            {
               list.Remove(list[i]);
                  colorList.colorList[i].SetColor(ColorType.EMPTY);
                colorList.colorList[i].GetComponent<Animator>().Play("bufferDestroy"); 
                colorList.colorList[i].playEffect(color);
            }
            effect(color);

        }
    }

    void effect(ColorType color)     ///不同颜色不同效果
    {
        if (color == ColorType.RED)
        {
            if (allEnemy.CompareTag("enemy"))
            {
                allEnemy.GetComponent<EnemyFSM>().TransitionState(EnemyStateType.Red);
            }
            else if (allEnemy.CompareTag("Boss"))
            {

                allEnemy.GetComponent<BossFSM>().TransitionState(StateID.red);
            }
        }
        else if (color == ColorType.BLUE)
        {
            if (allEnemy.CompareTag("enemy"))
            {
                allEnemy.GetComponent<EnemyFSM>().TransitionState(EnemyStateType.Blue);
            }
            else if (allEnemy.CompareTag("Boss"))
            {

                allEnemy.GetComponent<BossFSM>().TransitionState(StateID.bule);
            }
        }
        else if (color == ColorType.GREEN)
        {
            
            GameObject traget = GameObject.FindWithTag("Player");
            Debug.Log(traget.name);
           traget.GetComponent<Character>().currentHealth += 50;
            if (traget.GetComponent<Character>().currentHealth > 100)
            {
               traget.GetComponent<Character>().currentHealth = 100;
            }
         
        }
    }
}
