import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import datetime

# Streamlit page configuration
st.set_page_config(page_title="Webcam Image Capture", layout="centered")

# Custom CSS for styling
st.markdown("""
    <style>
        .stButton>button {
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            margin: 5px;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
        .stButton>button:disabled {
            background-color: #6c757d;
            cursor: not-allowed;
        }
        .error {
            color: red;
            margin: 10px;
            text-align: center;
        }
        .info {
            color: #333;
            margin: 10px;
            text-align: center;
        }
        .download-button {
            background-color: #28a745;
            color: white;
            padding: 10px;
            border-radius: 5px;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
        }
        .download-button:hover {
            background-color: #218838;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'captured_image' not in st.session_state:
    st.session_state.captured_image = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = ""
if 'info_message' not in st.session_state:
    st.session_state.info_message = ""

# Display title
st.title("Webcam Image Capture")

# Placeholder for info and error messages
info_placeholder = st.empty()
error_placeholder = st.empty()

# Display messages
def show_error(message):
    st.session_state.error_message = message
    error_placeholder.markdown(f'<p class="error">{message}</p>', unsafe_allow_html=True)

def show_info(message):
    st.session_state.info_message = message
    info_placeholder.markdown(f'<p class="info">{message}</p>', unsafe_allow_html=True)

def clear_messages():
    st.session_state.error_message = ""
    st.session_state.info_message = ""
    error_placeholder.empty()
    info_placeholder.empty()

# WebRTC configuration for webcam streaming
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# Webcam streamer
class VideoProcessor:
    def __init__(self):
        self.captured_frame = None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr")
        return frame

def capture_image(processor):
    if hasattr(processor, 'frame') and processor.frame is not None:
        img = processor.frame.to_ndarray(format="bgr")
        st.session_state.captured_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        show_info("Image captured successfully!")
    else:
        show_error("No video frame available to capture.")

# Start webcam stream
webrtc_ctx = webrtc_streamer(
    key="webcam",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

# Capture button
capture_button = st.button("Capture Image", disabled=not webrtc_ctx.state.playing)
if capture_button and webrtc_ctx.video_processor:
    capture_image(webrtc_ctx.video_processor)

# Retry button
if st.button("Retry Webcam Access"):
    clear_messages()
    show_info("Attempting to access webcam...")

# Display captured image
if st.session_state.captured_image is not None:
    st.image(st.session_state.captured_image, caption="Captured Image", use_column_width=True)

    # Convert image to bytes for download
    img_pil = Image.fromarray(st.session_state.captured_image)
    img_buffer = io.BytesIO()
    img_pil.save(img_buffer, format="PNG")
    img_bytes = img_buffer.getvalue()

    # Download button
    timestamp = datetime.datetime.now().isoformat().replace(":", "-")
    st.download_button(
        label="Download Captured Image",
        data=img_bytes,
        file_name=f"captured_image_{timestamp}.png",
        mime="image/png",
        key="download",
        help="Click to download the captured image",
    )

# Display initial info
if not webrtc_ctx.state.playing:
    show_info("Please allow webcam access to start capturing images.")
else:
    show_info("Webcam connected successfully.")

# Display diagnostics
diagnostics = {
    "Browser": "Streamlit (Python-based)",
    "Secure Context": "Yes" if st._is_running_with_streamlit else "No",
    "WebRTC Supported": webrtc_ctx is not None
}
show_info(f"Browser: {diagnostics['Browser']} | Secure Context: {diagnostics['Secure Context']} | WebRTC: {diagnostics['WebRTC Supported']}")