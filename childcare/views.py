# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from http.client import HTTPConnection as _HTTPConnection, HTTPException
import urllib

# Create your views here.

import xml.etree.ElementTree as ET
def xmlTest(request):
    doc = ET.parse("childcare/xmlTest.xml")
    root = doc.getroot()
    #print(doc)
    doc = '<?xml version="1.0" encoding="UTF-8"?>\n<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xxx="https://api.childcare.go.kr/mediate/soap/acntRpt/acRptStacnt.ws/acRptStacnt.ws">\n<soap:Header></soap:Header>\n<soap:Body>\n<xxx:acRptStacnt>\n<Request>\n<S_AUTH_KEY>C81AECA1AE8342A394039DF8E1596508</S_AUTH_KEY>\n<C_AUTH_KEY></C_AUTH_KEY>\n<ACYEAR>2019</ACYEAR>\n<STR>\n<GB>1</GB>\n<CD>111</CD>\n<CSCNN>100000</CSCNN>\n<RMK><![CDATA[\n비고1\n]]></RMK>\n</STR>\n<STR>\n<GB>2</GB>\n<CD>212</CD>\n<CSCNN>300000</CSCNN>\n<RMK><![CDATA[\n비고2\n]]></RMK>\n</STR>\n</Request>\n</xxx:acRptStacnt>\n</soap:Body>\n</soap:Envelope>'
    
    #try:
    #conn = _HTTPConnection("api.childcare.go.kr")
    #params = urllib.parse.urlencode({'request': doc})
    #print(params)
    #print("============before=============")
    #conn.request("POST", "/mediate/soap/acntRpt/acRptStacnt.ws/acRptStacnt.ws", params)
    #print("============after=============")
    #content = conn.getresponse().read()
    #conn.close()
    import requests
    url = "https://api.childcare.go.kr/mediate/soap/acntRpt/acRptStacnt.ws/acRptStacnt.ws"
    headers = {'content-type': 'text/xml'}
    body = """<?xml version="1.0" encoding="UTF-8"?>
            <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xxx="https://api.childcare.go.kr/mediate/soap/acntRpt/acRptStacnt.ws/acRptStacnt.ws">
                <soap:Header></soap:Header>
                <soap:Body>
                    <xxx:acRptStacnt>
                        <Request>
                            <S_AUTH_KEY>C81AECA1AE8342A394039DF8E1596508</S_AUTH_KEY>
                            <C_AUTH_KEY></C_AUTH_KEY>
                            <ACYEAR>2019</ACYEAR>
                            <STR>
                                <GB>1</GB>
                                <CD>111</CD>
                                <CSCNN>100000</CSCNN>
                                <RMK><![CDATA[\n비고1\n]]></RMK>
                            </STR>
                            <STR>
                                <GB>2</GB>
                                <CD>212</CD>
                                <CSCNN>300000</CSCNN>
                                <RMK><![CDATA[\n비고2\n]]></RMK>
                            </STR>
                        </Request>
                    </xxx:acRptStacnt>
                </soap:Body>
            </soap:Envelope>"""
    content = requests.post(url, data=body, headers=headers)
    return render(request, 'childcare/xmlTest.html', {'root': root, 'content': content})
    #except:
        #import sys
        #print(sys.exc_info()[:2])
        
    #return render(request, 'childcare/xmlTest.html', {'root': root})
