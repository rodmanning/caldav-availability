=====================
 CalDAV Availability
=====================


Overview
========

This program downloads a CalDAV-formatted calendar file and parses it to
produce free/busy information suitable for including in a HTML or other
type of calendar.


Getting and Installing
======================

Checkout and download the file:

   ``git checkout git@github.com:rodmanning/caldav-availability.git <local_path>``

   
Usage
=====

Run the program using the python interpreter:

   ``python caldav_availability.py <options>``

.. note::

   Run ``python caldav_availbility.py --help`` for details on the options
   and settings available.

   
How it Works
============

The program downloads the calendar file over a http Basic Authentication
connection at an url/realm supplied as command line variables. Username and
password details for authentication are also suppled as command line variables.

After downloading the file, the program parses it to compute the amount of
free/busy time in specified blocks on time in a calendar. The size and
start/stop times for the blocks are able to be customized by command line
variables.

The results of the program are written to a text file. Results can be written
in json, XML, or plain text (csv) format.


License
=======

This software is subject to the terms of the Mozilla Public Licence, v. 2.0. If
a copy of the MPL was not distributed with this file, You can obtain one at
http://mozilla.org/MPL/2.0/.

Copyright (c), 2017, Rod Manning <rod.t.manning@gmail.com>
