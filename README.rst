Kookaberry Accelerometer Module
======================================

The accelerometer module is a lightweight circuit board, using a subset of **Kookaberry** hardware and **Kookaberry** firmware, 
and is intended to be mounted on a moving vehicle to measure and record its acceleration in high resolution over short periods.

Typical STEM applications include the Reengineering Australia (REA) Formula 1 model race vehicles, ballistic rockets, bouncing balls, pendulums, 
free-fall devices etc.  

In short, on anything that is propelled or moved where it is desirable to record its acceleration.

The mass (weight) of the circuit board has been minimised so that it does not overly reduce  acceleration.

Description
-----------

The Accelerometer Module is shown in :numref:`mfront` below.  Its key properties are:

•	Dimensions: 60mm L x 26mm W x 12mm H (inclusive of jumpers)
•	Weight: 10 grams (inclusive of battery)
•	Power: soldered-in rechargeable 3.6V battery recharged via USB-C connector
•	Power Switch: Jumpers next to battery - On – jumper in lower position; Off – jumper in upper
•	Computing: Raspberry Pi RP2040 microcomputer and LSM303 3-axis accelerometer
•	File Storage: 3.5 Mbytes presented as a USB-C removable memory stick
•	Programmable User Interface: Pushbutton (SW1), Orange LED (LD1), Red LED (LD2)
•	Programming: **KookaSuite** (**KookaBlockly**, **MicroPython**) or **Thonny** (MicroPython) via USB-C.

.. _mfront:
.. figure:: images/module-front.png
    :align: left
    :scale: 30%

    Accelerometer Module front


.. _mrear:
.. figure:: images/module-rear.png
    :align: left
    :scale: 30%

    Accelerometer Module rear
