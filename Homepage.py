import streamlit as st
from PIL import Image
import subprocess
import sys
import time
import os
from streamlit_option_menu import option_menu as om
import s3fs
import logging
import boto3
from io import BytesIO
from botocore.exceptions import ClientError

s3_client = boto3.client(
        's3',
        aws_access_key_id=st.secrets["aws_access_key_id"],
        aws_secret_access_key=st.secrets["aws_secret_access_key"],
    )

def upload_file(file_path, bucket):
    file_name = os.path.basename(file_path)
    try:
        with open(file_path, 'rb') as f:
            response = s3_client.upload_fileobj(f, bucket, file_name)
        print(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def load_image(image_file):
    print(type(image_file))
    img = Image.open(image_file)
    return img

# fs = s3fs.S3FileSystem(anon=False) # Connection object for S3

st.set_page_config(
    page_title="Detecting weather fronts",
    page_icon="☁",
    initial_sidebar_state="collapsed",
)

selected = om("Main menu", ['Detect fronts ☁', 'Statistics 📊'], icons=['upload','list-task'], menu_icon='cast', default_index=0, orientation='horizontal')

st.title = "Detect Weather Fronts"

if selected == 'Detect fronts ☁':
    st.header("Detecting weather fronts", anchor="title")
    st.write("Weather has can have loads of indirect effects on us.Some recent studies show that certain changes in the atmospheric fronts, pressure and even temperature can have a major impact on chronic diseases such as Cerebrovascular Attacks. We propose a Computer Vision algorithm that uses RCNN to detect and classify weather fronts on synoptic maps, data which should become useful for later associations with patient fluxes in hospitals and the correlation between the affections and the weather in that period of time.")
    st.subheader("1. First select the synoptic map you want to upload", anchor="step-1")

    st.subheader("Synoptic Map")
    image_file = st.file_uploader("Upload Synoptic Maps", type=["png","jpg","jpeg"])

    uploaded  = False
    if image_file is not None:

        # To See details
        file_details = {"filename":image_file.name, "filetype":image_file.type,
                        "filesize":image_file.size}
        st.write(file_details)

        # To View Uploaded Image
        uploaded_image = load_image(image_file)
        st.image(uploaded_image,width=600)

        uploaded = st.button("Upload maps")

    st.subheader("2. View your resulted detections", anchor="step-2")

    if uploaded:
        with open(os.path.join("imgs", image_file.name), "wb") as f:
            f.write(image_file.getbuffer())
        st.success("Uploaded maps")

        with st.spinner('Detecting fronts...'):
            subprocess.run([f"{sys.executable}" ,"./detect_weather.py", f"./imgs/{image_file.name}"])
            name_size = len(image_file.name)
            if image_file.type == "jpeg":
                name_size -= 5
            else:
                name_size -= 4

            # upload_file(f'../../results/resulted_{image_file.name[:name_size]}.png', "detecting-weather-fronts")
        st.success('Done!')
        # st.snow()

        detected_fronts_img = None # load_image(f'../../results/resulted_{image_file.name[:name_size]}.png')
        st.subheader("Detected fronts", anchor="warm-front")
        if detected_fronts_img:
            st.image(detected_fronts_img,width=750)
else:
    st.header("Statistics", anchor="statistics")
    trai_test_img = load_image('./train_test.png')
    st.image(trai_test_img,width=600)
