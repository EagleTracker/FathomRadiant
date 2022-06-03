import cv2
import PySimpleGUI as sg
import csv

# Window items
layout = [  [sg.Text('Select a file'), sg.FileBrowse()],
            [sg.Text('Output file name'), sg.InputText("Default")],
            [sg.Radio('.CSV', "RADIO1", default=True)],
            [sg.Radio('.TXT', "RADIO1", default=False)],
            [sg.Button('Ok'), sg.Button('Cancel')]]

# Create the window
window = sg.Window('Center Locator', layout)

# Event Loop to process events and get values of inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        window.close()
        break

    # File is valid
    if values["Browse"] != "":
        window.close()

        # Read image through command line
        img = cv2.imread(values['Browse'])

        # Convert to grayscale
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Blur image
        gray_image = cv2.GaussianBlur(gray_image, (7, 7), 0)

        # Convert to binary image
        thresh = cv2.adaptiveThreshold(gray_image, 255,
                                       cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 21, 10)

        # Find contours
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Filter out non-circular and very small contours
        filtered_contours = []
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.12 * cv2.arcLength(contour, True), True)
            area = cv2.contourArea(contour)
            if ((len(approx) > 2) & (area > 15)):
                filtered_contours.append(contour)
        if values[1]:
            # Generate CSV
            with open(values[0]+'.csv', 'w') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
                filewriter.writerow(['X', 'Y'])


                for contour in filtered_contours:
                    # Calculate moments for each contour
                    moment = cv2.moments(contour)

                    # Calculate coordinate of center
                    if moment["m00"] != 0:
                        cX = float(moment["m10"] / moment["m00"])
                        cY = float(moment["m01"] / moment["m00"])
                    else:
                        cX, cY = 0, 0
                    filewriter.writerow([cX, cY])

        if values[2]:
            # Generate TXT
            file = open(values[0]+".txt", "w+")
            for contour in filtered_contours:
                # Calculate moments for each contour
                moment = cv2.moments(contour)

                # Calculate coordinate of center
                if moment["m00"] != 0:
                    cX = float(moment["m10"] / moment["m00"])
                    cY = float(moment["m01"] / moment["m00"])
                else:
                    cX, cY = 0, 0
                file.write(str(cX)+", "+str(cY)+"\n")
            file.close()
