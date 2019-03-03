import sys
import serial

import Leap, sys, thread, time
from Leap import CircleGesture

try:
    # Tkinter for Python 2.xx
    import Tkinter as tk
except ImportError:
    # Tkinter for Python 3.xx
    import tkinter as tk



class Value():
    def __init__(self, name, index, scale):
        self._name = name;
        self._value = tk.IntVar()
        self._value.set(0)
        self._index = index
        self._scale = scale
        
    def set(self, value):
        self._value.set(int(value / self._scale))
        #self._value.set(value)

    def get(self):
        return int(self._value.get())


def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))


get_bin = lambda x, n: format(x, 'b').zfill(n)


class SampleListener(Leap.Listener):
    values = {}
    controller = None
    try:
        port = serial.Serial("/dev/ttyACM0", baudrate=9600, timeout=1.0)
    except:
        port = None
    top = None

    def init_gui(self, controller):
        self.top = tk.Tk()

        for value in [("roll", -1, 1), ("pitch", -1, 5), ("yaw", -1, 5), ("elevation", -1, 1), 
                      ("motor1+", 1, 1), ("motor1-", 0, 1), 
                      ("motor2+", 2, 1), ("motor2-", 3, 1), 
                      ("motor3+", 4, 1), ("motor3-", 5, 1), 
                      ("motor4+", 6, 1), ("motor4-", 7, 1)]:
            self.values[value[0]] = Value(*value)
            label = tk.Label(text=value[0])
            label.pack()
            box = tk.Entry(self.top, textvariable=str(self.values[value[0]]._value), justify="center", width=4)
            box.pack()

        def done():
            self.controller.remove_listener(self)
            self.top.destroy()

        but = tk.Button(text="Exit", command=done)
        but.pack()
        center(self.top)
        self.top.after(1, self.send_serial)
        self.controller = controller
        
    def run_gui(self):
        self.top.mainloop()

    def on_init(self, controller):
        print("Initialized")

    def on_connect(self, controller):
        print("Connected")
        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)

    def on_disconnect(self, controller):
        print("Disconnected")

    def on_exit(self, controller):
        self.port.write(chr(0))
        self.port.close()
        print("Exited")

    def set_motor(self, source, motor):
        ret = False
        if self.values[source].get() > 0:
            self.values["motor"+motor+"+"].set(1)
            ret = True
        else:
            self.values["motor"+motor+"+"].set(0)
        if self.values[source].get() < 0:
            self.values["motor"+motor+"-"].set(1)
            ret = True
        else:
            self.values["motor"+motor+"-"].set(0)
        return ret

    def send_serial(self):
        # clear motor status
        for motor in range(1, 5):
            self.values["motor"+str(motor)+"-"].set(0)
            self.values["motor"+str(motor)+"+"].set(0)
            
        ret = False
        if not ret:
            ret = self.set_motor("elevation", "2")
        if not ret:
            ret = self.set_motor("yaw", "3")
        if not ret:
            ret = self.set_motor("pitch", "1")
        
        keys = [0, 0, 0, 0, 0, 0, 0, 0]
        for val in self.values.itervalues():
            if val._index < 0:
                continue
            keys[val._index] = val.get()
        if self.port:
            data = 0
            for x in range(0, len(keys)):
                data = data | (keys[x] << x)
            self.port.write(chr(data))
            #sys.stdout.write("\r%s"% get_bin(data, 8))
            #sys.stdout.flush()
        self.top.after(1, self.send_serial)

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        
        if not frame.is_valid:
            return
        
        if len(frame.hands) == 0:
            for value in self.values.itervalues():
                value.set(0)
            return
        
        if len(frame.hands) > 1:
            return
        
        previous = controller.frame(10)

        ignore_changes = False
        
        # Get gestures
        for gesture in frame.gestures():
            if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                if gesture.state == Leap.Gesture.STATE_START or gesture.state == Leap.Gesture.STATE_UPDATE:
                    # if we're doing a circle, ignore individual measurements in order to avoid noise
                    ignore_changes = True
                elif gesture.state == Leap.Gesture.STATE_STOP:
                    circle = CircleGesture(gesture)

                    # Determine clock direction using the angle between the pointable and the circle normal
                    if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2:
                        clockwiseness = "clockwise"
                    else:
                        clockwiseness = "counterclockwise"

                    ignore_changes = False
   
        if not ignore_changes:
            # Get hands
            for hand in frame.hands:
                # Get the hand's normal vector and direction
                normal = hand.palm_normal
                direction = hand.direction
    
                # Calculate the hand's pitch, roll, and yaw angles
                pitch = direction.pitch * Leap.RAD_TO_DEG
                roll = normal.roll * Leap.RAD_TO_DEG
                yaw = direction.yaw * Leap.RAD_TO_DEG

                self.values["pitch"].set(pitch)
                self.values["roll"].set(roll)
                self.values["yaw"].set(yaw)

            if previous.is_valid:
                #for hand in frame.hands:
                translation = frame.translation(previous)
                if translation.is_valid:
                    self.values["elevation"].set(translation.y)
                #translation = hand.scale_factor(previous)
                #self.values["elevation"].set(2 if translation < 1.0 else -2)
                # only handle 1st hand
                #break


def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    listener.init_gui(controller)

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)
    
    listener.run_gui()

if __name__ == "__main__":
    main()
