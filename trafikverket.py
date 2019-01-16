#!/usr/bin/env python3

import xml.etree.cElementTree as ET
import urllib
import urllib.request
import argparse
import datetime

def check_trains(args):

    print("Hämtar information om %s" % args.station)
    data1= """
              <REQUEST>
                  <LOGIN authenticationkey="%s"/>
                      <QUERY objecttype="TrainStation">
                          <FILTER>
                              <EQ name="AdvertisedLocationName" value="%s" />
                          </FILTER>
                      </QUERY>
              </REQUEST>
    """ % (args.key, args.station)

    data2 = str.encode(data1)

    req = urllib.request.Request(url='http://api.trafikinfo.trafikverket.se/v1.3/data.xml', data=data2,headers = {'Content-Type':'text/xml'})


    response = urllib.request.urlopen(req)
    the_page = response.read()

    the_page = ET.fromstring(the_page)

    for child in the_page:
        for a in child:
            for b in a:
                if b.tag in ["LocationSignature"]:
                    locSig = (b.text)

    data3= """
               <REQUEST>
                   <LOGIN authenticationkey="%s"/>
                       <QUERY objecttype="TrainAnnouncement" orderby="AdvertisedTimeAtLocation">
                          <FILTER>
                              <EQ name="LocationSignature" value="%s" />
                              <EQ name="ScheduledDepartureDateTime" value="%s" />
                          </FILTER>
                       </QUERY>
               </REQUEST>
    """ % (args.key, locSig, args.date)
    data4 = str.encode(data3)

    req2 = urllib.request.Request(url='http://api.trafikinfo.trafikverket.se/v1.3/data.xml', data=data4,headers = {'Content-Type':'text/xml'})

    response2 = urllib.request.urlopen(req2)
    the_page2 = response2.read()

    the_page2 = ET.fromstring(the_page2)

    list_of_departures = {}
    alltrainnumber = []
    alladvertisedtime = []
    allendstations = []
    for child in the_page2:
        for a in child:
            for b in a:
                if b.tag in ["AdvertisedTrainIdent"]:
                    alltrainnumber.append(str(b.text))
                if b.tag in ["AdvertisedTimeAtLocation"]:
                    #print("Planerad avgångstid:")
                    alladvertisedtime.append(str(b.text))
                if b.tag in ["ToLocation"]:
                    for c in b:
                        if c.tag in ["LocationName"]:
                            locTo = c.text

                            data1= """
                                <REQUEST>
                                    <LOGIN authenticationkey="%s"/>
                                        <QUERY objecttype="TrainStation">
                                            <FILTER>
                                                <EQ name="LocationSignature" value="%s" />
                                            </FILTER>
                                        </QUERY>
                                </REQUEST>
                            """ % (args.key, locTo)

                            data2 = str.encode(data1)

                            req = urllib.request.Request(url='http://api.trafikinfo.trafikverket.se/v1.3/data.xml', data=data2,headers = {'Content-Type':'text/xml'})


                            response = urllib.request.urlopen(req)
                            the_page = response.read()

                            the_page = ET.fromstring(the_page)

                            for child in the_page:
                                for a in child:
                                    for b in a:
                                        if b.tag in ["AdvertisedLocationName"]:
                                            allendstations.append(str(b.text).lower())

    list_of_departures["trainnumber"] = alltrainnumber
    list_of_departures["advertisedtime"] = alladvertisedtime
    list_of_departures["endstations"] = allendstations

    for trainnumber, advertisedtime, endstation in list(zip(list_of_departures["trainnumber"], list_of_departures["advertisedtime"], list_of_departures["endstations"])):
        if args.dest is not None and args.dest not in endstation:
            continue
        print(endstation)
        print(trainnumber)
        print(advertisedtime)
        print("\n")        
if __name__ == "__main__": 
    now = datetime.datetime.now()
    parser = argparse.ArgumentParser(description='Tågstationsavgångar')
    parser.add_argument('--apikey', dest='key', type=str,
                        help='Din API-nyckel', default="openapiconsolekey")
    parser.add_argument('--start', dest='station', type=str,
                        help='Vilken station du vill kolla', default="varberg")
    parser.add_argument('--datum', dest='date', type=str, default=now.strftime("%Y-%m-%d"),
                        help='Vilket datum du vill kolla, skrivs YYYY-MM-DD')
    parser.add_argument('--destionation', dest='dest', type=str, default=None,
			help='Destination att åka till')

    args = parser.parse_args()
    args.station = args.station.lower()
    args.dest = args.dest.lower()
    check_trains(args)
    
