import device
import cv2
import io
import time


def main():
    # print OpenCV version
    print("OpenCV version: " + cv2.__version__)

    # Get camera list
    device_list = device.getDeviceList()
    index = 0

    #Identify Read camera
    read_camera_index = -1
    for name in device_list:
        print(str(index) + ': ' + name)
        if 'Logitech' in name:
            read_camera_index = index
        index += 1

    last_index = index - 1

    if last_index < 0:
        print("No device is connected")
        return

    if read_camera_index < 0:
        print("Read camera not connected")

    file = open("read_camera.txt","w")
    file.write(str(read_camera_index))
    file.close()

    #Get read camera index from text file
    read_file = open("C:\\Users\\IMI-User\\Downloads\\python-capture-device-list-master\\read_camera.txt", "r")
    camera_index = read_file.read()
    read_file.close()
    camera_index = int(camera_index)

    print(camera_index)

main()