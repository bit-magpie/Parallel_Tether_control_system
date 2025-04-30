import serial
from serial.tools import list_ports
import streamlit as st
    
port_list = list_ports.comports()
serial_port = serial.Serial()

st.title("Parallel Tether Controller Interface")

# def get_port_info(option):
#     return port_list[option].name

#port = st.selectbox("Available ports", options=range(len(port_list)), format_func=get_port_info)

#col1, col2 = st.columns((4,1))

#length = col1.slider('Reel 1', 0, 2000, 0, key="sldr1")
#col2.write(port_list[0].name)

# if col2.button('Set'):
#     print(length)


slider_array = []
button_array = []

if len(port_list) > 0:
    for i, port in enumerate(port_list):
        slider_array.append(st.slider("Reel " + str(i), -2000, 2000, 0, key="slider" + str(i)))
        col1, col2 = st.columns((5,1))
        col1.markdown("Selected Port: **" + port.device + "**")
        button_array.append(col2.button("Set", key="btn" + str(i)))

    for j, button in enumerate(button_array):
        if button:
            value = st.session_state['slider'+str(j)]
            print("slider: " + str(j))
            print(value)

            serial_port.port = port_list[j].device
            serial_port.baudrate = 115200

            #string += struct.pack('!B',value)
            serial_port.open()
            serial_port.write(str(value).encode("utf-8"))
            serial_port.close()

else:
    st.warning("No active serial ports found.")