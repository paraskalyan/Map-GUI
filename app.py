import tkinter as tk
from tkinter import *
import tkintermapview
import serial
import threading
import re
from PIL import ImageTk, Image
import os
from datetime import datetime, date
import serial.tools.list_ports

class MapGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x600")
        self.root.title("MAP GUI")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.resizable(False, False)

        font = ('Courier', 10, 'bold')
        self.connect_label = tk.Label(self.root, text="DISCONNECTED", font=font, fg='red')
        self.connect_label.place(x = 980, y = 550)

        com_ports = list(serial.tools.list_ports.comports())
        if len(com_ports) !=0:
            self.port = com_ports[0].device
            self.ser = serial.Serial(self.port, baudrate=115200)
            if(self.ser):
                print("Connected")
                self.connect_label.config(text="CONNECTED", fg='green')
             # Start reading data from the serial port in a separate thread
            self.serial_thread = threading.Thread(target=self.read_serial)
            self.serial_thread.daemon = True
            self.serial_thread.start()
        else:
            self.port = None
            
        self.marker_list = []
        self.marker_data = []
        # self.btn = tk.Button(self.root, text="SEND", command=self.send_data)
        # self.btn.place(x = 20, y = 500)
        self.new_icon = ImageTk.PhotoImage(Image.open("green.png"))
        self.last_label = tk.Label(self.root, text="LAST NODE:- ", font=font, fg='blue')
        self.last_label.place(x = 100, y = 510)
        self.last_node_label = tk.Label(self.root, font=font, justify='left' , fg='blue')
        self.last_node_label.place(x = 200, y = 510)
        self.time_label = tk.Label(self.root, fg='blue', font=font)
        self.time_label.place(x = 980, y = 510)
        self.port_label = tk.Label(self.root, text=f"PORT- {self.port}", fg='blue', font=font)
        self.port_label.place(x = 980, y = 530)

        self.node_label = tk.Label(self.root, font=font ,fg='blue')
        self.node_label.place(x = 500, y = 510)

        self.node_count_label = tk.Label(self.root, font=font, fg='blue', text="Total Nodes: 0")
        self.node_count_label.place(x = 750, y = 510)

        # path for the database to useg                  
        script_directory = os.path.dirname(os.path.abspath(__file__))
        database_path = 'C:/Users/Admin/Desktop/NodeGUI/offline_tiles_RAMGARH_Google.db'
        
        self.map_widget = tkintermapview.TkinterMapView(root, width=1100, height=500, corner_radius=0, database_path=database_path)
        self.map_widget.pack()
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22) 
        self.map_widget.set_position(30.64878716210612, 76.89076668166409)
        self.map_widget.set_zoom(5)
        # self.process_data("NODE0132.43434375.656565 NODE0230.43434375.656565 NODE0330.65827776.732029 NODE0440.65827776.732029")
        self.update_time()
        self.process_data("N42222222#30.65885876.729635 \n N533333333#31.65885876.729635")
        self.node_count = 0
        
        # markers_data = self.load_json_data()
        # for marker in markers_data:
        #     self.node_count += 1
        #     self.node_count_label.config(text=f"Total Nodes: {self.node_count}" )
        #     self.marker = self.map_widget.set_marker(marker['latitude'],marker['longitude'], text=f"{marker['node_id']}", font=('Arial', 9, 'bold'), icon= self.new_icon, text_color = 'blue', command = self.marker_clicked)
    def process_data(self, data):

        # pattern = r"(NODE\d{2})(\d{2}\.\d{6})(\d{2}\.\d{6})"
        pattern = r"(N\d)([^\n]+\#)(\d{2}\.\d{6})(\d{2}\.\d{6})"
        off_pattern = r"(NODE)(\d)(OFF)"
        matches = re.findall(pattern, data)
        off_matches = re.findall(off_pattern, data)
        print(off_matches)
        print(matches)
        if(off_matches):
            for match in off_matches:
                idd = match[1]
                n_id = f'N{idd}'
                print(n_id)
                if len(self.marker_list) != 0:
                    for marker in self.marker_list:
                        if marker['node_id'] == n_id:
                            self.marker_list.remove(marker)
                            self.map_widget.delete(marker['marker'])
                            self.node_count_label.config(text=f"Total Nodes: {len(self.marker_list)}")


        for match in matches:
            node_id = match[0]
            node_data = match[1]
            latitude = float(match[2])
            longitude = float(match[3])
          
            if len(self.marker_list) != 0:
                 for marker in self.marker_list:
                    if marker['node_id'] == node_id:
                        self.marker_list.remove(marker)
                        self.map_widget.delete(marker['marker'])
                
            self.marker = self.map_widget.set_marker(latitude,longitude,text=f"{node_id}", font=('Arial', 9, 'bold'), icon= self.new_icon, text_color = 'blue', command = self.marker_clicked)
            self.marker.text_y_offset = -17
            current_time = datetime.now().time()
            formatted_time = current_time.strftime("%H:%M:%S")
            display_string = f"{node_id}\nLatitude:- {latitude}\nLongitude:- {longitude}\nNode Data:- {node_data}\n{formatted_time}"
            self.last_node_label.config(text=display_string)
            self.write_log(display_string)
            # self.marker_data.append({"node_id": node_id,"latitude": latitude, "longitude": longitude})
            self.marker_list.append({"marker": self.marker, "node_id": node_id,"latitude": latitude, "longitude": longitude, "node_data": node_data})
            self.node_count_label.config(text=f"Total Nodes: {len(self.marker_list)}")
         

        # self.save_to_json(self.marker_data)
            
    # def read_serial(self):
    #     if self.ser.in_waiting > 0:
    #         data = self.ser.read_all().decode().strip()
    #         print(data)
    #         self.process_data(data)

    #     self.root.after(300, self.read_serial)
        
    def marker_clicked(self, marker):
        for node in self.marker_list:
            if marker == node['marker']:   
                n_data = node['node_data']
        self.node_label.config(text=f"{marker.text}\nLatitude:- {marker.position[0]}\nLongitude:- {marker.position[1]}\nNode Data:- {n_data}")


    # def send_data(self):
    #     data = "1NODE01"
    #     # # Convert the data to bytes if necessary
    #     data_bytes = data.encode()
    #     # # Send the data over the serial port
    #     self.ser.write(data_bytes)

    def write_log(self, data):
        dte = date.today()
        dte = dte.strftime("%d-%m-%Y")
        try:
            with open("log.txt", "a") as file:
                file.write(dte + "\n" +data + "\n" + "------------------")
        except Exception as e:
            print(f"Error occurred: {e}") 
    
    # def save_to_json(self, data):
    #     print("JSON DATA:= ", data)
    #     with open('markers.json', 'w') as file:
    #         json.dump(data, file)

    # def load_json_data(self):
    #     with open('markers.json', 'r') as file:
    #         data = json.load(file)
    #     return data
    
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)  # Update every 1 second

    def on_closing(self):
        # Close the Tkinter window
        root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = MapGUI(root)
    root.mainloop()
