'''
In this annotation tool, the annotator is given the text to label it and then the full meme to label it
'''


import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import json
import cv2
import PIL as pil
import io
import os
import random
import sqlite3
import emoji
import xlsxwriter
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
import socket
import ssl
import requests
import ast
import base64
import datetime
from datetime import date, time , datetime
from datetime import timedelta


def get_graph_knowledge(person):
    
    with open('./celeb_graph_knowledge.json', 'r') as fp:
        data = json.load(fp)
    return data[person]


def get_name(img_id):

    with open('./celeb_boxes_10k.json', 'r') as fp:
        data = json.load(fp)

    celeb_names = []
    for i in data[img_id]['names']:
        celeb_names.append(i)#data[img_id]['names'][0]

    return celeb_names


def download_link(object_to_download, download_filename, download_link_text):

    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

session = st.session_state

annotations = pd.DataFrame(columns = ['ID', 'Notes', 'Hate_level_text_only', 'Hate_level_full_meme'])



sns.set_style('darkgrid')

option1 = ' '
option2 = 'Annotation'
selected_option = st.sidebar.selectbox(
    'Choose a view',
    (option1, option2)
)

img_path = './img/'

# ----- Annotation -----
if selected_option == option2: 
    st.markdown("<h1 style='text-align: center;'>Hello! Please label some of the memes below</h1>", unsafe_allow_html=True)

    results = []

    check = False
    for result in os.listdir(img_path):
        img_name = result
        results.append(os.path.join(img_path, img_name))
    
    with open('./all_text.json', 'r') as fp:
        all_text = json.load(fp)

    if(len(results) == 0):
        st.markdown("<h3 style='text-align: center;'>Congratulations, you have nothing to label!​​​​​​​​​​​​​​​​​​​​​ &#x1F60a;</h3>", unsafe_allow_html=True)


    index = st.number_input(label = 'Index', value = 0 ,min_value = 0, max_value = 146, step = 1)

    plus_sign = '<p style="font-family:sans-serif; color: brown   ; font-size: 15px;"> ' + "+ : move to next meme" + '</p>'
    st.markdown(plus_sign, unsafe_allow_html=True)
    minus_sign = '<p style="font-family:sans-serif; color: brown   ; font-size: 15px;"> ' + "- : move to previous meme" + '</p>'
    st.markdown(minus_sign, unsafe_allow_html=True)

    
    results.sort()
    
    img_id = results[index]
    img_name = results[index]
    img_score = results[index]

    img = cv2.imread(img_name)
 
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    curr_img_id = img_id[6:-4]

    # to delete the zero in the beginning if founf
    curr_img_id = int(curr_img_id)
    
    curr_text = all_text[str(curr_img_id)]

    height, width, channels = img.shape
    
    col1, col3, col2 = st.columns(3)
    
    with col1:
        #st.image(img, width=int(width*0.5))
        
        #text = st.text(curr_text)
        text = '<p style="font-family:sans-serif; color: #273746    ; font-size: 18px;"> ' + curr_text + '</p>'
        st.markdown(text, unsafe_allow_html=True)

                
        if(st.button('Press here after annotating the text', key="{}.1".format(img_id))):# or str(img_id) in session
            if(str(img_id) not in session):
                st.error('Pleas label the text and hit the submit button first')
            else:
                session['button_pressed'] = 1    
                st.info('Please choose the hateful level of the meme below and hit the submit button again')   
                st.image(img, width=int(width*0.5))
                celebs = get_name(img_id[6:])
                for i in celebs:
                    st.text("Celebrity name : {}".format(i))#get_name(img_id[6:])
                    info = get_graph_knowledge(i)#get_name(img_id[6:])
                    new_title = '<p style="font-family:sans-serif; color: #2e4053   ; font-size: 15px;"> ' + info + '</p>'
                    st.markdown(new_title, unsafe_allow_html=True)



    with col3:
        st.write('')

    with col2:
        st.markdown("<h2>What kind of hateful meme is this?</h2>", unsafe_allow_html=True)
        
        hate_level = st.radio('Hateful level',['1', '2', '3'], key = "{}.2".format(img_id))
        st.caption('1 : Not hateful')
        st.caption('2 : Hateful level is intermediate')
        st.caption('3 : Hateful level is very high')



        if(st.button('Submit', key="{}.16".format(img_id))):

            if 'annotations' not in session:
                st.session_state.annotations =  annotations
                

            annotations = session.annotations
            if(img_id[6:] not in annotations['ID'].unique()):
                annotations.loc[len(annotations), 'ID'] = img_id[6:]


            hate_handler_case_text_only = ''
            hate_handler_case_full_meme= ''
            

            if(str(img_id) not in session):
                hate_handler_case_text_only= str(hate_level)
            
            if(str(img_id) in session):
                hate_handler_case_text_only = session['hate_handler_case_text_only']            
                hate_handler_case_full_meme = str(hate_level)
       
            annotations.loc[annotations.ID == img_id[6:], "Hate_level_text_only"] = hate_handler_case_text_only

            if(str(img_id) in session):
                annotations.loc[annotations.ID == img_id[6:], "Hate_level_full_meme"] = hate_handler_case_full_meme


            session.annotations = annotations
            session[str(img_id)] = 1
            session['hate_handler_case_text_only'] = hate_handler_case_text_only
       
        if st.button('Download your annotations as a CSV file'):
            st.markdown('<h5>Please send your annotations to this email address : abdelrahman.eldakrony@stud.uni-due.de</h5>', unsafe_allow_html=True)
            tmp_download_link = download_link(session.annotations, 'annotations_' + str(datetime.now()) + '.csv', 'Click here to download your data!')
            st.markdown(tmp_download_link, unsafe_allow_html=True)


        
