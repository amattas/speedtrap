# Speed Trap

This is a simple radar/camera speed trap that can be ran on a RaspberryPI, NVidia Jetson Nano, 
or any other machine with with USB, enough memory, and processing power.

## History 
In my neighborhood I live in a through street, and its an easy way to get two and from two local schools.
Because of the cut through, our neighborhood has a lot of traffic the travels at a high rate of speed.

Our local police department did a speed study and found during bus hours the overwhelming majority of 
traffic was measured to be within 5mph of the posted speed limit, however, they measured a few 
vehicles traveling more than double the speed limit. Although they cannot police the area constantly 
they expressed their willingness to put special patrols in place if I could let them know the time
of the offending vehicles, their license plate number, and estimated speed. Challenge accepted. 

## Hardware
Your hardware list may vary, but this is what I built my device with:
 * [NVidia Jetson Nano](https://developer.nvidia.com/embedded/jetson-nano-developer-kit)
 * [Mini USB Camera Module Board](https://www.amazon.com/gp/product/B07MFTDHLH/ref=ppx_yo_dt_b_asin_title_o08_s00?ie=UTF8&psc=1)
 * [OmniPresense OPS243-A Radar Sensor](https://omnipresense.com/product/ops243-doppler-radar-sensor/)
 * [TP-LINK TL-WN722N WiFi Adapter](https://www.microcenter.com/product/361805/tl-wn722n-150mbps-wireless-n-usb-adapter)
 * [Anker PowerCore+ 26800 PD](https://www.amazon.com/gp/product/B01MZ61PRW/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
 * [BUD Industries NBF-32016 ABS Box](https://www.amazon.com/gp/product/B005UPANU2/ref=ppx_yo_dt_b_asin_title_o04_s01?ie=UTF8&psc=1)
 * [BUD Industries NBX-32916-PL ABS Plastic Internal Panel](https://www.amazon.com/gp/product/B005UPE83U/ref=ppx_yo_dt_b_asin_image_o04_s00?ie=UTF8&psc=1)
 * m2, m2.5, and m3 stand-offs
 * Offset drill bit
 * Plexiglass
 * USB Cables

## Cloud
There is the option to store your data files to cloud storage, right now this only supports Azure
because for my day job I work for Microsoft and it's who I have chosen to support. With that said,
it would be really easy to copy the cloudstorage.py source code file and stub it out for the provider 
of your choice. You can also store to cloud databases, for this I have opted to use generic ODBC as
I developed the software on a Mac, and the out of the box available database drivers are different 
than what is available on arm64.

## Known Issues
There are a couple known issues with the current build:
 * This readme file doesn't have near enough detail yet
 * Like any radar based product this is still affected by doppler shit (cosine effect), while 
   it's easy to calculate the proper speed, I would like for the system to do this automatically. 
   this potentially should be possible either using the video feed and open cv (although I do have
   concern about performance on this small of a device and how that affects accuracy), or potentially
   using an OPS243-C sensor which also measures a few different parameters using its additional 
   FMCW radar.
 * Security: in the type of enclosure I used this unit is fairly easily removed, partially by design. In
   theory though it would be pretty easy to rig up a motion sensor + alarm if the unit is moved, and/or
   use OpenCV with the camera to detect when the image frame has change significantly which would
   indicate some has gotten close to the unit.
