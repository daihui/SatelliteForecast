# SatelliteForecast
A satellite data crawling from http://www.heavens-above.com/

Base on gived satellite id and rise time crawl other information about the satellite, such as Altitude, Azimuth, Distance (km), Brightness.

##Input File Format
There are two File Format this release 1.0 support:  txt, dat
###For txt
the data format must be:

>satelliteId\t riseTime\t\n

Note: riseTime should be HH:MM ,such as:

11112	08:33

13068	14:26

13154	15:03

14032	14:23

###For Dat
the data format must be:

>satelliteId  YYYYmmdd  HHMMSS000  ...\n

such as:

11112  20160721  184231000  320.914795    0.000000   23.928321    0.000000    1585.339330

11112  20160720  141132000  320.785370    0.000000   24.065700    0.000000    1580.008432

11112  20160720  141133000  320.654764    0.000000   24.203669    0.000000    1574.689324

11112  20160720  141134000  320.522963    0.000000   24.342232    0.000000    1569.382131


The first three columns are needed and others are not neccessary.

More details about this crawling to see the comments in SatForecast.py File.

