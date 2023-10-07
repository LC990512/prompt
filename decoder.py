import pandas as pd
import numpy as np
import sys
import math
import re
import ast
import os
from lxml import etree

num = 0
step_data = pd.DataFrame()
function_dict = {
    'b11':'access website by URL',
    'b12':'back button of website',
    'b21':'add task',
    'b22':'remove task',
    'b31':'registration',
    'b32':'login',
    'b41':'search email by keywords',
    'b42':'send email with valid data',
    'b51':'calculator total bill with tip',
    'b52':'split tip'
}
category_dict = {
    'a1':'browser',
    'a2':'todo list',
    'a3':'shopping',  
    'a4':'mail client',
    'a5':'tip calculator'
}
#text特殊处理
def convert(idx, identifier):
    #if (idx == "a54"):
    #    print(idx, identifier)
    special_word_dict = {
        'Sign_in':'sign in',
        'sign_up':'sign up',
        'sign_in':'sign in',
        'signin':'sign in',
        'Sign_up':'sign up',
        'signup':'sign up',
        'Log_In':'log in',
        'Log_in':'log in',
        'login':'log in',
        '%':'percent',
        '#':'number',
        'et':'edit text',
        'edittext':'edit text',
        'btn':'button',
        'bt':'button',
        'tv':'text view',
        'textview':'text view',
        'fab':''
    }
    #https://www.google.com/webhp?client=ms-android-google&source=android-home
    identifier = identifier.replace("\"","").replace("ICST","icst") 
    #identifier = identifier.lower()
    #identifier = identifier.replace("_"," ").replace("-", " ").replace("\b", " ").replace("todo", "to do") .strip()
    if (idx == "a34"):
        print(identifier)
    
    for text in identifier.split(" "):
        if text in special_word_dict:
            identifier = identifier.replace(text, special_word_dict[text])
    splitted = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1' , identifier)).split() 
        
    text_feature_without_camel_case = '' 
    for revised_text in splitted:
        revised_text = revised_text.lower()
        if '.com' in revised_text:
            revised_text = revised_text.split(".com")[0] + ".com" 
        if 's.' in revised_text: # for a35
            revised_text = 'Smith'
        if revised_text in special_word_dict:
            revised_text = special_word_dict[revised_text]
        text_feature_without_camel_case += revised_text + " "
    if (idx == "a34"):
        print(text_feature_without_camel_case)
    
    text_feature = text_feature_without_camel_case.replace("_"," ").replace("-", " ").replace("\\b", "").replace("todo", "to do").replace("$", "").replace(".0","").replace("sample.","sample").replace("to,", "to"). replace("do.", "do").strip()
    
    for text in text_feature.split(" "):
        if text in special_word_dict:
            text_feature = text_feature.replace(text, special_word_dict[text])
    if (idx == "a34"):
        print(text_feature)
    
    return text_feature

def get_target(y):
    #1. (Event) Click a view ``sign in, login fragment sign in button''
    num = 0
    y.sort_values(by="tgt_index", inplace=True, ascending=True) 

    for i in y.index:
        step = ""

        if (y.loc[i]['type'] == 'gui'):
            str_type =  "(Event)"
        elif (y.loc[i]['type'] == 'oracle'):
            str_type =  "(Assertion)"
        else:
            num = num + 1
            step = '{}. '.format(num) + "(Event) system back"
            y.loc[i, 'step'] = step
            continue

        #view处理
        str_view = ""
        text = y.loc[i]['text']
        content_desc = y.loc[i]['content_desc']
        id = y.loc[i]['id']

        if (str(y.loc[i]['text']) != 'nan'):
            str_view = text
        if (y.loc[i]['action'] != 'wait_until_text_presence' and y.loc[i]['action'] != 'wait_until_text_invisible'):
            if (str(y.loc[i]['content_desc']) != 'nan'):
                if (str_view != ""):
                    str_view += ", "
                str_view += content_desc
            if (str(y.loc[i]['id']) != 'nan'):
                if (str_view != ""):
                    str_view += ", "
                id = id.split("/")[-1]
                str_view += id
        
        if (str_view == ""):
            #print("str_view为空: ", y.loc[i]['tgt_app'], y.loc[i]['function'], y.loc[i]['tgt_index'])
            xpath = y.loc[i]['xpath']
            xpath = xpath.split(".")[-1]
            if ('[' in xpath):
                xpath = xpath.split("[")[0]
            str_view = "whose type is \"{}\"".format(xpath)
        else:
            # if (y.loc[i]['tgt_app'] == 'a54'):
            #     print("old-----", str_view)
            
            str_view = convert(y.loc[i]['tgt_app'], str_view)
            # if (y.loc[i]['tgt_app'] == 'a54'):
            #     print("new-----", str_view)
            #     print("a54: ", y.loc[i]['function'], y.loc[i]['tgt_index'], str_view)
            str_view = "\"" + str_view + "\""
        
        #input处理   
        str_input = str_view        
        if (str(y.loc[i]['input']) != "nan"):
            str_input = convert(y.loc[i]['tgt_app'], y.loc[i]['input'])
            str_input = str_view + " with " + "\"" + str_input + "\""
       
      
        #action处理
        if (y.loc[i]['action'] == 'click'):
            num = num + 1
            step = '{}. '.format(num) + str_type + " Click a view " + str_view
        elif (y.loc[i]['action'] == 'long_press'):
            num = num + 1
            step = '{}. '.format(num) + str_type + " Long press a view " + str_view
        elif (y.loc[i]['action'] == 'swipe_right'):
            num = num + 1
            step = '{}. '.format(num) + str_type + " Swipe a view " + str_view + " to right"
        elif (y.loc[i]['action'] == 'send_keys' or y.loc[i]['action'] == 'send_keys_and_hide_keyboard'):
            num = num + 1
            step = '{}. '.format(num) + str_type + " Edit a view " + str_input
        elif (y.loc[i]['action'] == 'clear_and_send_keys' or y.loc[i]['action'] == 'clear_and_send_keys_and_hide_keyboard'):
            num = num + 1
            step = '{}. '.format(num) + str_type + " Clear a view " + str_view
            step += "\n"
            num = num + 1
            step += '{}. '.format(num) + str_type + " Edit a view " + str_input    
        elif (y.loc[i]['action'] == 'send_keys_and_enter'):
            num = num + 1
            step = '{}. '.format(num) + str_type + " Edit a view " + str_view
            step += "\n"
            num = num + 1
            step += '{}. '.format(num) + str_type + " system enter"
        elif (y.loc[i]['action'] == 'wait_until_element_presence'): 
            num = num + 1
            step = '{}. '.format(num) + str_type + " Identify a view " + str_view + " in the state"
        elif (y.loc[i]['action'] == 'wait_until_text_presence'):
            num = num + 1
            step = '{}. '.format(num) + str_type + " Identify a text " + str_view + " in the state"
        elif (y.loc[i]['action'] == 'wait_until_text_invisible'):
            num = num + 1
            step = '{}. '.format(num) + str_type + " Identify a text " + str_view + " not in the state"
        
        y.loc[i, 'step'] = step
        #print(y.loc[i]['step'])
        if (step == ""):
            print("step为空: ", y.loc[i]['tgt_app'], y.loc[i]['function'], y.loc[i]['tgt_index'], y.loc[i]['action'])

    #print(y)
    return y   
    #x.sort_values(by=['state_order', 'by', 'bx', 'tgt_index', 'src_app', 'index'], inplace=True, ascending=True) 
   
    #x.to_csv("part.csv", index=False)
    

   

def solve(x):
    #1. (Event) Click a view ``sign in, login fragment sign in button''
    #按照tgtapp划分，处理不同的源app
    #print(x)
    function = x.iloc[0]['function']
    target_group = x.groupby(['tgt_app'], group_keys=True).apply(get_target)
    target_col = x['tgt_app']
    target_col.drop_duplicates(keep='first',inplace=True)
    
    for i in target_col.index:
        app_name = target_col.loc[i]
        #print(app_name[:2])
        str = "You are a designer to summarize the general test step to test the {} functionality for {} apps\n".format(function_dict[function], category_dict[app_name[:2]])
        str += "Below are test steps for different {} apps need to be summarized\n".format(category_dict[app_name[:2]])

        paser = target_group[target_group['tgt_app'] != app_name] 
        #paser.sort_values(by=['tgt_app', 'tgt_index'], inplace=True, ascending=True) 

        #print(app_name)
        #print(paser)
        #print("\n")
        last = ""
        cnt = 0

        for j in paser.index:
            if (paser.loc[j]['tgt_app'] != last):
                cnt = cnt + 1
                last = paser.loc[j]['tgt_app']
                str += "\n"
                str += "Test Steps from {} {} app\n".format(chr(cnt + 64), category_dict[app_name[:2]])
            #print(paser.loc[j])
            #if (str(paser.loc[j]['step']) == 'nan'):
            step = paser.loc[j]['step']
            #print(paser.loc[j]['tgt_app'], paser.loc[j]['function'], paser.loc[j]['tgt_index'])
            #print(step)

            str += step
            str += "\n"                
        str += "\nOutput format:\n"
        str += "General test steps for testing {} functionality in {} apps:\n".format(function_dict[function], category_dict[app_name[:2]])
        str += "Note that, please only output the general test steps without explanation\n"
        #print(str)
        #print("\n")
        #print(function, type(function))
        #file_name = function + ".txt"
        
        file_name = "paser/" + app_name + "_" + function + ".txt"
        file = open(file_name, 'w', encoding='utf-8')
        file.write(str)  

    return x

def main():
    df = pd.read_csv('data.csv')

    #按照function划分
    result_group = df.groupby(['function'], group_keys=True).apply(solve)
    
    #反向填充原始文件
    # for i in range(0, len(result_group)):
    #     index = result_group.iloc[i]['index']
    #     df.loc[df['index']==index, 'step'] = result_group.iloc[i]['step']
    
    result_group.to_csv("result_paser.csv", index=False)
    

if __name__ == "__main__":
    main()
