import customtkinter
import cv2
import supervision as sv
import numpy as np
from ultralytics import YOLO
from tkinter.filedialog import askopenfilename
from tkinter import Entry, END
from PIL import Image

from customtkinter import CTk, CTkRadioButton, CTkScrollableFrame, StringVar, set_appearance_mode


class ScrollableRadiobuttonFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, item_list, command=None, **kwargs):
        super().__init__(master, **kwargs)

        self.command = command
        self.radiobutton_variable = StringVar()
        self.radiobutton_list = []
        for i, item in enumerate(item_list):
            self.add_item(item)

    def add_item(self, item):
        radiobutton = CTkRadioButton(self, text=item, value=item, variable=self.radiobutton_variable)
        if self.command is not None:
            radiobutton.configure(command=self.command)
        radiobutton.grid(row=len(self.radiobutton_list), column=0, pady=(0, 10))
        self.radiobutton_list.append(radiobutton)

    def get_checked_item(self):
        return self.radiobutton_variable.get()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("CrowDET")
        self.geometry("400x300")
        self.grid_rowconfigure(0, weight=1)
        self.columnconfigure(2, weight=2)

        self.model = YOLO('crowddetect.pt')
        self.cam = None

        self.scrollable_radiobutton_frame = ScrollableRadiobuttonFrame(
            master=self, width=200, command=self.radiobutton_frame_event,
            item_list=['Default Camera', "Integrated Camera", "Choose Video(.MP4)", "Connect CCTV"],
            label_text="Choose media"
        )

        self.scrollable_radiobutton_frame.grid(row=0, column=2, padx=15, pady=20, sticky="nsew", columnspan=1)
        self.scrollable_radiobutton_frame.configure(width=200)

    def radiobutton_frame_event(self):
        selected_item = self.scrollable_radiobutton_frame.get_checked_item()
        while self.cam is not None and self.cam.isOpened():
            self.cam.release()
            if cv2.waitKey(10) == ord('q'):
                break
            cv2.destroyAllWindows()

        if selected_item == 'Default Camera':
            self.connect_to_camera(0)
        elif selected_item == 'Integrated Camera':
            self.connect_to_camera(1)
        elif selected_item == 'Choose Video(.MP4)':
            self.choose_video_file()
        elif selected_item == 'Connect CCTV':
            self.connect_to_cctv()

    def connect_to_camera(self, camera_id):
        try:
            self.cam = cv2.VideoCapture(camera_id)
            self.model.predict(source=camera_id, show=True, conf=0.3)
            box_annotator = sv.BoxAnnotator(
                thickness=2,
                text_thickness=2,
                text_scale=1
            )
            print(f"Connecting to camera {camera_id}...")
            while self.cam.isOpened():
                result= self.model(self.cam)
                detections = sv.Detections.from_yolov8(result)
                frame= box_annotator.annotate()
                if cv2.waitKey(10) == ord('q'):
                    break
        except Exception as e:
            print(f"Error while connecting to camera {camera_id}: {str(e)}")

    def choose_video_file(self):
        file_path = askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
        if file_path:
            try:
                self.cam = cv2.VideoCapture(file_path)
                self.model.predict(source=file_path, show=True, conf=0.25)
                detections= sv.Detections.from_yolov8(self.model)
                print("Choosing a video file...")
                while self.cam.isOpened():
                    if cv2.waitKey(10) == ord('q'):
                        break
            except Exception as e:
                print(f"Error while opening video file {file_path}: {str(e)}")


    def connect_to_cctv(self):
        # Add your CCTV connection logic here...

        cctv_url = f"rtsp:{ip}"
        try:
            self.cam = cv2.VideoCapture(cctv_url)
            self.model.predict(source=cctv_url, show=True, conf=0.15)
            print("Connecting to a CCTV device...")

            prop = cv2.cv.CV_CAP_PROP_FRAME_COUNT if imutils.is_cv2() \
                else cv2.CAP_PROP_FRAME_COUNT
            total = int(vs.get(prop))
            print("[INFO] {} total frames in video".format(total))
        except Exception as e:
            print(f"Error while connecting to CCTV: {str(e)}")
            print("[INFO] could not determine # of frames in video")
            print("[INFO] no approx. completion time can be provided")
            total = -1


if __name__ == "__main__":
    customtkinter.set_appearance_mode("white")
    app = App()
    app.mainloop()
