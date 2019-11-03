# Coloring-Machine-from-SVG_image-using-marlin
this project take any SVG image with size 300x300 mm and convert this image to Gcode. the Gcode then you can take the output file and send it serially to marlin firmware using pronterface.\
as i can't have 16 million color on the machine, i used 1-NN (KNN) to get the closest fit to the color 

### Running the script

1-navigate to the repo folder.\
2-open terminal or cmd and type python svg2gcode.py -i <path_to_file>.\
3-you will find the output Gcode file with name <same_name>.gcode in gcode_output.\

you can try $ python svg2gcode.py -i images/baby.svg

### Changing angles of colors

1-open config.py.\
2-change the angle.

### Adding colors

1-open config.py.\
2-create new list and add color with as many RGB color variance as possible to increase the probability of the 1-NN to chose the right color.\
3-add the angle.\
4-new add list to avilable_colors_RGB list.\
5-add the new color list to color_dict with the new angle as a key.

### Enlarging bed size

to enlarge bed size just open config.py and bed_max_x,bed_max_y.
