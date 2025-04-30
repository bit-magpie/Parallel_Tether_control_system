import serial
from serial.tools import list_ports
import streamlit as st
import time
import pickle
from os.path import exists
import os

class Reel:
    def __init__(self, serial_port) -> None:
        self.serial = serial.Serial(timeout=3)
        self.serial.port = serial_port
        self.serial.baudrate = 115200
        self.reel_id = 0
        self.last_value = 0
        self.torque_on = True
    
    def getReelId(self):
        self.serial.open()
        self.serial.write("rlid".encode("utf-8"))
        value = self.serial.readline()
        if len(value) > 0:
            self.reel_id = int(value)
        else:
            self.reel_id = -1
        self.serial.close()
        print(self.reel_id)

    def setValue(self, value):
        print(self.serial.port)
        print(value)
        self.serial.open()
        self.serial.write(str(value).encode("utf-8"))
        self.last_value = value
        self.torque_on = True
        self.serial.close()

    def torqueOn(self):
        print(self.serial.port)
        self.serial.open()
        self.serial.write("tqon".encode("utf-8"))
        self.torque_on = True
        self.serial.close()
        print("Torque On")

    def torqueOff(self):
        print(self.serial.port)
        self.serial.open()
        self.serial.write("tqof".encode("utf-8"))
        self.torque_on = False
        self.serial.close()
        print("Torque Off")

    def testReel(self):
        self.serial.open()
        self.serial.write(str(50).encode("utf-8"))
        time.sleep(1)
        self.serial.write(str(-50).encode("utf-8"))
        self.serial.close()

def generateReelList(port_list):
    reel_list = [None]*6

    for i, port in enumerate(port_list):
        reel = Reel(port.device)
        reel.getReelId()
        reel_list[reel.reel_id-1] = reel

    return reel_list

st.title("Parallel Tether Controller Interface")

port_list = list_ports.comports()
file_path = "reel_list.pkl"
two_combs = {'Not selected':[0], 'All':[0,1,2,3,4,5], '1,2':[0,1], '2,3':[1,2], '3,4':[2,3], '4,5':[3,4], '5,6':[4,5], '6,1':[5,0]}
check_array = []
available_reels = []
st.session_state.torque_list = [True]*6

def deselectAll():
    for i in available_reels:
        st.session_state["check"+str(i)] = False

def checkSelected():
    deselectAll()
    to_select = two_combs[st.session_state.sltCombs]
    if len(to_select) > 1:
        for index in to_select:
            if index in available_reels:
                st.session_state["check"+str(index)] = True

def writeToFile(reels):
    with open(file_path, "wb") as file:
        pickle.dump(reels, file)

if len(port_list) > 0:

    if not exists(file_path):
        with st.spinner("Setting up ports..."):
            reel_list = generateReelList(port_list)
            with open(file_path, "wb") as file:
                pickle.dump(reel_list, file)
    else:
        file = open(file_path, "rb")
        reel_list = pickle.load(file)
        file.close()

    cola2, cola3 = st.columns((4,1))
    # all_check = cola1.checkbox("All reels", value=False, key="checkall")
    cola2.selectbox("Combinations", two_combs.keys(), key="sltCombs", on_change=checkSelected,label_visibility="collapsed")
    btn_reassign = cola3.button("Re-assign", key="btnRa")
    st.markdown("""---""")

    for j, reel in enumerate(reel_list):
        if reel is not None:
            col1, col2, col3, col4 = st.columns((1,2,1,1))
            check_array.append(col1.checkbox("Reel " + str(j+1) , value=False, key="check"+str(j)))
            available_reels.append(j)
            col2.markdown("**Port** (" + reel.serial.port + ")")
            
            if reel.torque_on:
                col3.markdown('Torque: **On**')
            else:
                col3.markdown('Torque: **Off**')
            if reel.reel_id > 0:
                col4.markdown('<span style="color:green"><b>Verified</b></span>', unsafe_allow_html=True)
            else:
                col4.markdown('<span style="color:red"><b>Not verified</b></span>', unsafe_allow_html=True)
    
    st.markdown("""---""")
    st.slider("Value", -2000, 2000, 0, key="slider")
    btncol1, btncol2, btncol3 = st.columns((1,3,1))       
    btn_tq_on = btncol1.button("Torque on", key="btnTqOn")
    btn_tq_off = btncol2.button("Release", key="btnTqOf")
    btn_set_length = btncol3.button("Set length", key="btnSet") 
    # st.write(st.session_state)

    if btn_set_length:
        for k in available_reels:
            chk_value = st.session_state["check"+str(k)]
            length = st.session_state["slider"]
            if chk_value:
                reel_list[k].setValue(length)
    
    if btn_reassign:
        os.remove(file_path)
        st.experimental_rerun()

    if btn_tq_on:
        for k in available_reels:
            if st.session_state["check"+str(k)]:
                reel_list[k].torqueOn()
                writeToFile(reel_list)
                st.experimental_rerun()

    if btn_tq_off:
        for k in available_reels:
            if st.session_state["check"+str(k)]:
                reel_list[k].torqueOff()
                writeToFile(reel_list)
                st.experimental_rerun()

else:
    st.warning("No active serial ports found.")

