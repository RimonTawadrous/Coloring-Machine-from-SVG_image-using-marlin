#!/usr/bin/env python

# External Imports
import os
import sys,getopt
import xml.etree.ElementTree as ET

# Local Imports
sys.path.insert(0, './lib') # (Import from lib folder)
import shapes as shapes_pkg
from shapes import point_generator
from config import *
import math
DEBUGGING = True
svg_keywords = set(['rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path'])
def distance(c1, c2):
    (r1,g1,b1) = c1
    (r2,g2,b2) = c2
    return math.sqrt((r1 - r2)**2 + (g1 - g2) ** 2 + (b1 - b2) **2)


def generate_gcode(filename):
    ''' The main method that converts svg files into gcode files.
        Still incomplete. See tests/start.svg'''

    # Check File Validity
    if not os.path.isfile(filename):
        raise ValueError("File \""+filename+"\" not found.")

    if not filename.endswith('.svg'):
        raise ValueError("File \""+filename+"\" is not an SVG file.")

    # Define the Output
    # ASSUMING LINUX / OSX FOLDER NAMING STYLE
    log = ""
    log += debug_log("Input File: "+filename)

    file = filename.split('/')[-1]
    dirlist = filename.split('/')[:-1]
    dir_string = ""
    # for folder in dirlist:
    #     dir_string += folder + '/'
        

    # Make Output File
    outdir = dir_string + "gcode_output/"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    outfile = outdir + file.split(".svg")[0] + '.gcode'
    log += debug_log("Output File: "+outfile)

    # Make Debug File
    debugdir = dir_string + "log/"
    if not os.path.exists(debugdir):
        os.makedirs(debugdir)
    debug_file = debugdir + file.split(".svg")[0] + '.log'
    log += debug_log("Log File: "+debug_file+"\n")

    # Get the SVG Input File
    file = open(filename, 'r')
    tree = ET.parse(file)
    root = tree.getroot()
    file.close()
    
    # Get the Height and Width from the parent svg tag
    width = root.get('width')
    height = root.get('height')

    if width == None or height == None:
        viewbox = root.get('viewBox')
        if viewbox:
            _, _, width, height = viewbox.split()                

    if width == None or height == None:
        # raise ValueError("Unable to get width or height for the svg")
        print ("Unable to get width and height for the svg")
        sys.exit(1)

    if "mm" in width:
        width = width[:-2]
    if "mm" in height:
        height = height[:-2]
    
    # Scale the file appropriately
    # (Will never distort image - always scales evenly)
    # ASSUMES: Y ASIX IS LONG AXIS
    #          X AXIS IS SHORT AXIS
    # i.e. laser cutter is in "portrait"
    scale_x = bed_max_x / float(width)
    scale_y = bed_max_y / float(height)
    scale = min(scale_x, scale_y)
    if scale > 1:
        scale = 1


    log += debug_log("wdth: "+str(width))
    log += debug_log("hght: "+str(height))
    log += debug_log("scale: "+str(scale))
    log += debug_log("x%: "+str(scale_x))
    log += debug_log("y%: "+str(scale_y))

    # CREATE OUTPUT VARIABLE
    gcode = ""

    # Write Initial G-Codes
    gcode += preamble + "\n"
    
    # Iterate through svg elements
    prev_tool_num = -1
    for elem in root.iter():
        log += debug_log("--Found Elem: "+str(elem))
        new_shape = True
        try:
            tag_suffix = elem.tag.split("}")[-1]
        except:
            print ("Error reading tag value:", tag_suffix)
            continue
        
        # Checks element is valid SVG shape
        if tag_suffix in svg_keywords:
            #### change tool 
            fill_color = elem.get("fill")
            stroke_color = elem.get("stroke")
            stroke_width = 0
            style = elem.get("style")
            info_dict = {}
       
            if style:
                for info in style.split(';'):
                    splited_data = info.split(":")
                    if splited_data[0]=="fill":
                        fill_color = splited_data[1]
                    elif splited_data[0]=="stroke":
                        stroke_color = splited_data[1]
                    elif splited_data[0]=="stroke-width":
                        stroke_width = splited_data[1]
                        info_dict["stroke-width"] = splited_data[1]

            if fill_color:
                if fill_color[0]=='#':
                    fill_color = fill_color[1:]
                    log += "color in HEX" + str(fill_color)
                    fill_RGB = tuple(int(fill_color[i:i+2], 16) for i in (0, 2, 4))
                    log += "color in RGB" + str(fill_RGB)
                    closest_colors = sorted(avilable_colors_RGB, key=lambda color: distance(color, fill_RGB))
                    info_dict["fill"] = color_dict[closest_colors[0]]
                else:
                    if fill_color in color_dict:
                        info_dict["fill"] = color_dict[fill_color]
                    elif fill_color == "none":
                        pass
                    else:
                        info_dict["fill"] = 4
            
            if stroke_color:
                if stroke_color[0]=='#':
                    stroke_color = stroke_color[1:]
                    stroke_RGB = tuple(int(stroke_color[i:i+2], 16) for i in (0, 2, 4))
                    closest_colors = sorted(avilable_colors_RGB, key=lambda color: distance(color, stroke_RGB))
                    info_dict["stroke"] = color_dict[closest_colors[0]]
                else:
                    if stroke_color in color_dict:
                        info_dict["stroke"] = color_dict[stroke_color]
                    else:
                        info_dict["stroke"] = 4
        
            tool_num = 4
            if "fill" in info_dict:
                tool_num = info_dict["fill"]
            if "stroke" in info_dict:
                tool_num = info_dict["stroke"]
            
            if prev_tool_num != tool_num:
                gcode += shape_postamble + "G4 S0.5\n"
                for i in range(8):
                    gcode += "M280 P0 S"+str(tool_num)+"\n"
                    gcode += "G4 S0.01\n"
                prev_tool_num = tool_num

            ##end of change tool
            log += debug_log("  --Name: "+str(tag_suffix))

            # Get corresponding class object from 'shapes.py'
            shape_class = getattr(shapes_pkg, tag_suffix)
            shape_obj = shape_class(elem)
            log += debug_log("\tClass : "+str(shape_class))
            log += debug_log("\tObject: "+str(shape_obj))
            log += debug_log("\tAttrs : "+str(elem.items()))
            log += debug_log("\tTransform: "+str(elem.get('transform')))


            ############ HERE'S THE MEAT!!! #############
            # Gets the Object path info in one of 2 ways:
            # 1. Reads the <tag>'s 'd' attribute.
            # 2. Reads the SVG and generates the path itself.
            d = shape_obj.d_path()
            log += debug_log("\td: "+str(d))

            # The *Transformation Matrix* #
            # Specifies something about how curves are approximated
            # Non-essential - a default is used if the method below
            #   returns None.
            m = shape_obj.transformation_matrix()
            log += debug_log("\tm: "+str(m))
            if d:
                log += debug_log("\td is GOOD!")
                points = point_generator(d, m, smoothness)
                log += debug_log("\tPoints: "+str(points))
                prev_x = 0
                prev_y = 0
                prev_flag = False
                for x,y in points:
                    log += debug_log("\t  pt: "+str((x,y)))
                    x = scale*x
                    y = bed_max_y - scale*y
                    log += debug_log("\t  pt: "+str((x,y)))
                    if x >= 0 and x <= bed_max_x and y >= 0 and y <= bed_max_y:
                        if new_shape:
                            gcode += ("G0 X%0.1f Y%0.1f\n" % (x, y))
                            gcode += shape_preamble
                            prev_x = x
                            prev_y = y
                            new_shape = False
                        else:
                            if round(prev_x,2) ==  round(x,2) and  round(prev_y,2) ==  round(y,2):
                                prev_x = x
                                prev_y = y 
                                gcode += shape_postamble
                                prev_flag  = True
                            else:
                                gcode += ("G0 X%0.1f Y%0.1f\n" % (x, y))
                                prev_x = x
                                prev_y = y
                               
                                if prev_flag == True:
                                    gcode += shape_preamble
                                    prev_flag  = False
                        log += debug_log("\t    --Point printed")
                    else:
                        log += debug_log("\t    --POINT NOT PRINTED ("+str(bed_max_x)+","+str(bed_max_y)+")")
                        pass
                gcode += shape_postamble + "\n"
            else:
              log += debug_log("\tNO PATH INSTRUCTIONS FOUND!!")
        else:
          log += debug_log("  --No Name: "+tag_suffix)

    gcode += postamble + "\n"

    # Write the Result
    ofile = open(outfile, 'w+')
    ofile.write(gcode)
    ofile.close()

    # Write Debugging
    # if DEBUGGING:
    #     dfile = open(debug_file, 'w+')
    #     # dfile.write(log)
        # dfile.close()



def debug_log(message):
    ''' Simple debugging function. If you don't understand 
        something then chuck this frickin everywhere. '''
    if (DEBUGGING):
        print (message)
    return message+'\n'



def test(filename):
    ''' Simple test function to call to check that this 
        module has been loaded properly'''
    circle_gcode = "G28\nG1 Z5.0\nG4 P200\nG1 X10.0 Y100.0\nG1 X10.0 Y101.8\nG1 X10.6 Y107.0\nG1 X11.8 Y112.1\nG1 X13.7 Y117.0\nG1 X16.2 Y121.5\nG1 X19.3 Y125.7\nG1 X22.9 Y129.5\nG1 X27.0 Y132.8\nG1 X31.5 Y135.5\nG1 X36.4 Y137.7\nG1 X41.4 Y139.1\nG1 X46.5 Y139.9\nG1 X51.7 Y140.0\nG1 X56.9 Y139.4\nG1 X62.0 Y138.2\nG1 X66.9 Y136.3\nG1 X71.5 Y133.7\nG1 X75.8 Y130.6\nG1 X79.6 Y127.0\nG1 X82.8 Y122.9\nG1 X85.5 Y118.5\nG1 X87.6 Y113.8\nG1 X89.1 Y108.8\nG1 X89.9 Y103.6\nG1 X90.0 Y98.2\nG1 X89.4 Y93.0\nG1 X88.2 Y87.9\nG1 X86.3 Y83.0\nG1 X83.8 Y78.5\nG1 X80.7 Y74.3\nG1 X77.1 Y70.5\nG1 X73.0 Y67.2\nG1 X68.5 Y64.5\nG1 X63.6 Y62.3\nG1 X58.6 Y60.9\nG1 X53.5 Y60.1\nG1 X48.3 Y60.0\nG1 X43.1 Y60.6\nG1 X38.0 Y61.8\nG1 X33.1 Y63.7\nG1 X28.5 Y66.3\nG1 X24.2 Y69.4\nG1 X20.4 Y73.0\nG1 X17.2 Y77.1\nG1 X14.5 Y81.5\nG1 X12.4 Y86.2\nG1 X10.9 Y91.2\nG1 X10.1 Y96.4\nG1 X10.0 Y100.0\nG4 P200\nG4 P200\nG1 X110.0 Y100.0\nG1 X110.0 Y101.8\nG1 X110.6 Y107.0\nG1 X111.8 Y112.1\nG1 X113.7 Y117.0\nG1 X116.2 Y121.5\nG1 X119.3 Y125.7\nG1 X122.9 Y129.5\nG1 X127.0 Y132.8\nG1 X131.5 Y135.5\nG1 X136.4 Y137.7\nG1 X141.4 Y139.1\nG1 X146.5 Y139.9\nG1 X151.7 Y140.0\nG1 X156.9 Y139.4\nG1 X162.0 Y138.2\nG1 X166.9 Y136.3\nG1 X171.5 Y133.7\nG1 X175.8 Y130.6\nG1 X179.6 Y127.0\nG1 X182.8 Y122.9\nG1 X185.5 Y118.5\nG1 X187.6 Y113.8\nG1 X189.1 Y108.8\nG1 X189.9 Y103.6\nG1 X190.0 Y98.2\nG1 X189.4 Y93.0\nG1 X188.2 Y87.9\nG1 X186.3 Y83.0\nG1 X183.8 Y78.5\nG1 X180.7 Y74.3\nG1 X177.1 Y70.5\nG1 X173.0 Y67.2\nG1 X168.5 Y64.5\nG1 X163.6 Y62.3\nG1 X158.6 Y60.9\nG1 X153.5 Y60.1\nG1 X148.3 Y60.0\nG1 X143.1 Y60.6\nG1 X138.0 Y61.8\nG1 X133.1 Y63.7\nG1 X128.5 Y66.3\nG1 X124.2 Y69.4\nG1 X120.4 Y73.0\nG1 X117.2 Y77.1\nG1 X114.5 Y81.5\nG1 X112.4 Y86.2\nG1 X110.9 Y91.2\nG1 X110.1 Y96.4\nG1 X110.0 Y100.0\nG4 P200\nG28\n"
    print (circle_gcode[:90], "...")
    return circle_gcode



def main(argv):
    #parse Parameters
    inputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile="])
        if len(opts) == 0:
            print ('you must run "python svg2gcode.py -i <inputfile-name>"')
            sys.exit(2)
    except getopt.GetoptError:
        print ('you must run "python svg2gcode.py -i <inputfile-name>"')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('python svg2gcode.py -i <inputfile-name>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
    print ('Input file is "', inputfile,'"')
    #end of parsing parameters
    #checking file existance    
    if(os.path.isfile(inputfile)):
        generate_gcode(inputfile)
    else:
        print ("file doesn't exist")


if __name__ == "__main__":
    main(sys.argv[1:])