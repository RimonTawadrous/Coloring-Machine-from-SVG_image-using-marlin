''' Configuration file for SVG to GCODE converter
    Date: 26 Oct 2016
    Author: Peter Scriven
'''

z_leveling = 5

avilable_colores = ["red","green","blue","black","orange","yellow","brown",""]
blue = [(102, 186, 234),(107, 27, 181),(108, 0, 250),(90, 2, 232),(44, 2, 232),(16, 117, 194),(25, 16, 194),(16, 18, 194),(33, 83, 191),(176,224,230),(173,216,230),(135,206,250),(135,206,235),
(0,191,255),(176,196,222),(30,144,255),(100,149,237),(70,130,180),(123,104,238),(106,90,205),(72,61,139),(65,105,225),(0,0,255),(0,0,205),(0,0,139)]
black = [(0,0,0),(10,10,10),(30,30,30),(64, 38, 43),(128, 105, 73),(135, 83, 7),(140, 119, 87),(192,192,192),(169,169,169),(128,128,128),(105,105,105)]
yellow = [(240, 240, 2),(235, 232, 52),(194, 194, 25),(243, 241, 208),(255,255,153),(255,255,102),(255,255,51),(255,255,0),(204,204,0),(214, 168, 108)]
red = [(194, 90, 25),(237, 75, 0),(255, 43, 5),(255, 30, 5),(255, 5, 5),(255, 5, 55),(250,128,114),(233,150,122),(240,128,128),(205,92,92),(220,20,60),(178,34,34),(255,0,0),(255,99,71),(255,69,0),
(219,112,147),(255,160,122),(232, 202, 160),(223, 171, 162)]

blue_angle = 6
black_angle = 58
yellow_angle = 110
red_angle = 168

avilable_colors_RGB = blue+black+yellow+red

color_dict = dict.fromkeys(blue , blue_angle)
color_dict.update(dict.fromkeys(black , black_angle))
color_dict.update(dict.fromkeys(yellow , yellow_angle))
color_dict.update(dict.fromkeys(red , red_angle))

'''G-code emitted at the start of processing the SVG file'''
preamble = "G0 X0 Y0\n"
for i in range(8):
    preamble +=  "M280 P1 S6\n"
    preamble += "G4 S0.01\n"
preamble += "G1 Z0.0\n"

'''G-code emitted at the end of processing the SVG file'''
postamble = "G0 X0 Y0\n"

'''G-code emitted before processing a SVG shape'''
shape_preamble = "G1 Z"+ str(z_leveling) + "\n"

'''G-code emitted after processing a SVG shape'''
shape_postamble = "G1 Z0.0\n"

# A4 area:               210mm x 297mm
# Printer Cutting Area: ~178mm x ~344mm
# Testing Area:          150mm x 150mm  (for now)
'''Print bed width in mm'''
bed_max_x = 300

'''Print bed height in mm'''
bed_max_y = 300
''' Used to control the smoothness/sharpness of the curves.
    Smaller the value greater the sharpness. Make sure the
    value is greater than 0.1'''
smoothness = 0.2
