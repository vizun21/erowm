# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Case, When, Count, Q
from django.db.models.functions import Coalesce
from http.client import HTTPConnection as _HTTPConnection, HTTPException
#import urllib
from accounting.models import Business, Item, Transaction, Budget
from .models import Record
from dateutil.relativedelta import relativedelta
import datetime
import requests

@login_required(login_url='/')
def monthly_report(request):
    business = get_object_or_404(Business, pk=request.session['business'])
    today = datetime.datetime.now()
    date = today - relativedelta(months=1)
    selected_year = request.GET.get('year', date.strftime("%Y"))
    this_y = date.strftime("%Y")
    this_m = date.strftime("%m")
    operation = "acRptMonthSum"

    if request.method == "GET":
        ym_range = []
        start_date = datetime.datetime.strptime(selected_year+"-03-01", "%Y-%m-%d")
        for months in range(12):
            temp_date = start_date + relativedelta(months=months)
            y = temp_date.strftime("%Y")
            m = temp_date.strftime("%m")
            try:
                recorded = Record.objects.get(business=business, operation=operation, year=y, gubun=m).regdatetime
            except:
                recorded = 0
            ym_range.append({'year': y, 'month': m, 'recorded': recorded})

    elif request.method == "POST":
        #--SR
        item_list = Item.objects.filter(
            paragraph__subsection__institution = business.type3,
        ).annotate(
            total_sum=Coalesce(
                Sum(Case(
                    When(transaction__business = business, then=Case(
                        When(transaction__Bkdate__year = selected_year, then=Case(
                            When(transaction__Bkdate__month = this_m, then=Case(
                                When(
                                    transaction__Bkoutput=0,
                                    then='transaction__Bkinput'
                                ),
                                default='transaction__Bkoutput')))))))),0),
            count=Count(Case(
                When(transaction__business = business, then=Case(
                    When(transaction__Bkdate__year = selected_year, then=Case(
                        When(transaction__Bkdate__month = this_m, then='id')))))))
        ).exclude(code=0).exclude(total_sum=0).exclude(count=0).order_by(
            'paragraph__subsection__type',
            'paragraph__subsection__code',
            'paragraph__code',
            'code'
        )
        #--END SR

        body =  "<S_AUTH_KEY>"+business.s_auth_key+"</S_AUTH_KEY>\n" + \
                "<MON>"+date.strftime("%Y")+this_m+"</MON>\n"
        for item in item_list:
            GB = "1" if item.paragraph.subsection.type=="수입" else "2"
            CD = str(item.paragraph.subsection.code)+str(item.paragraph.code)+str(item.code)
            body += "<SR>\n"
            body += "   <GB>"+GB+"</GB>\n"
            body += "   <CD>"+CD+"</CD>\n"
            body += "   <AMT>"+str(item.total_sum)+"</AMT>\n"
            body += "   <CNT>"+str(item.count)+"</CNT>\n"
            body += "</SR>\n"
        response = request_childcare(business, operation, selected_year, this_m, body)
        return response

    return render(request, 'childcare/monthly_report.html', {
        'accounting_report': 'active', 'monthly_report': 'active','business': business,
        'ym_range': ym_range, 'y_range': range(int(this_y), 1999, -1),
        'this_y': this_y, 'this_m': this_m, 'selected_year': int(selected_year) })

@login_required(login_url='/')
def budget_report(request):
    business = get_object_or_404(Business, pk=request.session['business'])
    today = datetime.datetime.now()
    #회기년도 설정 - 1,2월일 경우 이전년도까지, 3월 이후면 올해년도까지
    if int(today.strftime("%m")) < 3:
        ac_year = (today - relativedelta(years=1)).strftime("%Y")
    else:
        ac_year = today.strftime("%Y")
    selected_year = request.GET.get('year', ac_year)
    operation = "acRptBudget"

    if request.method == "GET":
        n_range = []
        for n in range(0, 4):
            try:
                recorded = Record.objects.get(business=business, operation=operation, year=selected_year, gubun=n).regdatetime
            except:
                recorded = 0
            n_range.append({'n': n, 'recorded': recorded})
        
    elif request.method == "POST":
        gubun = request.POST.get('gubun', 0)
        #--BGTR
        if int(gubun) == 0:
            budget_list = Budget.objects.filter(business=business, year=selected_year
            ).filter(Q(type='revenue')|Q(type='expenditure')
            ).exclude(item__code=0).order_by(
                'item__paragraph__subsection__type',
                'item__paragraph__subsection__code',
                'item__paragraph__code',
                'item__code'
            )
        else:
            budget_list = Budget.objects.filter(business=business, year=selected_year
            ).filter(Q(type__startswith='supplementary')&Q(type__endswith=gubun)
            ).exclude(item__code=0).order_by(
                'item__paragraph__subsection__type',
                'item__paragraph__subsection__code',
                'item__paragraph__code',
                'item__code'
            )
        #--END BGTR

        body =  "<S_AUTH_KEY>"+business.s_auth_key+"</S_AUTH_KEY>\n" + \
                "<ACYEAR>"+str(selected_year)+"</ACYEAR>\n" + \
                "<BGTGB>"+gubun+"</BGTGB>\n"
        for budget in budget_list:
            GB = "1" if budget.item.paragraph.subsection.type=="수입" else "2"
            CD = str(budget.item.paragraph.subsection.code)+str(budget.item.paragraph.code)+str(budget.item.code)
            COMPUTBSIS = ""

            if budget.price != 0:
                context_list = budget.context.split("|")
                unit_price_list = budget.unit_price.split("|")
                cnt_list = budget.cnt.split("|")
                months_list = budget.months.split("|")
                percent_list = budget.percent.split("|")
                sub_price_list = budget.sub_price.split("|")
                for idx in range(0, len(context_list)):
                    if percent_list[idx] == '':
                        COMPUTBSIS += context_list[idx] + " " + unit_price_list[idx] + " * " + cnt_list[idx] + " * " + months_list[idx] + " = " + sub_price_list[idx] + "\n"
                    else:
                        COMPUTBSIS += context_list[idx] + " " + unit_price_list[idx] + " * " + cnt_list[idx] + " * " + months_list[idx] + " * " + percent_list[idx] +"% = " + sub_price_list[idx] + "\n"

            body += "<BGTR>\n"
            body += "   <GB>"+GB+"</GB>\n"
            body += "   <CD>"+CD+"</CD>\n"
            body += "   <BGTAMT>"+str(budget.price)+"</BGTAMT>\n"
            body += "   <COMPUTBSIS>"+COMPUTBSIS+"</COMPUTBSIS>\n"
            body += "</BGTR>\n"
        response = request_childcare(business, operation, selected_year, gubun, body)
        return response

    return render(request, 'childcare/budget_report.html', {
        'accounting_report': 'active', 'budget_report': 'active', 'business': business,
        'n_range': n_range, 'y_range': range(int(ac_year), 1999, -1),
        'selected_year': int(selected_year) })

@login_required(login_url='/')
def settlement_report(request):
    business = get_object_or_404(Business, pk=request.session['business'])
    today = datetime.datetime.now()
    #회기년도 설정 - 1,2월일 경우 이전년도까지, 3월 이후면 올해년도까지
    if int(today.strftime("%m")) < 3:
        ac_year = (today - relativedelta(years=1)).strftime("%Y")
    else:
        ac_year = today.strftime("%Y")
    selected_year = request.GET.get('year', ac_year)
    start_date = datetime.datetime.strptime(selected_year+"-03-01", "%Y-%m-%d")
    end_date = start_date + relativedelta(years=1)
    operation = "acRptStacnt"
    
    if request.method == "GET":
        try:
            recorded = Record.objects.get(business=business, operation=operation, year=selected_year, gubun='').regdatetime
        except:
            recorded = 0

    if request.method == "POST":
        #--STR
        item_list = Item.objects.filter(
            paragraph__subsection__institution = business.type3,
        ).annotate(
            total_sum=Coalesce(
                Sum(Case(
                    When(transaction__business = business, then=Case(
                        When(transaction__Bkdate__gte = start_date, then=Case(
                            When(transaction__Bkdate__lt = end_date, then=Case(
                                When(
                                    transaction__Bkoutput=0,
                                    then='transaction__Bkinput'
                                ),
                                default='transaction__Bkoutput')))))))),0)
        ).exclude(code=0).order_by(
            'paragraph__subsection__type',
            'paragraph__subsection__code',
            'paragraph__code',
            'code'
        )
        #--END STR
        body =  "<S_AUTH_KEY>"+business.s_auth_key+"</S_AUTH_KEY>\n" + \
                "<ACYEAR>"+str(selected_year)+"</ACYEAR>\n"
        for item in item_list:
            GB = "1" if item.paragraph.subsection.type=="수입" else "2"
            CD = str(item.paragraph.subsection.code)+str(item.paragraph.code)+str(item.code)
            body += "<STR>\n"
            body += "   <GB>"+GB+"</GB>\n"
            body += "   <CD>"+CD+"</CD>\n"
            body += "   <CSCNN>"+str(item.total_sum)+"</CSCNN>\n"
            body += "   <RMK></RMK>\n"
            body += "</STR>\n"
        response = request_childcare(business, operation, selected_year, "", body)
        return response
    return render(request, 'childcare/settlement_report.html', {
        'accounting_report': 'active', 'settlement_report': 'active', 'business': business,
        'y_range': range(int(ac_year), 1999, -1), 'recorded': recorded,
        'selected_year': int(selected_year)})


def request_childcare(business, operation, year, gubun, body):
    #url = "https://api.childcare.go.kr/route/soap/acntRpt/"+operation+".ws/"+operation+".ws?wsdl"
    url = "https://stgapi.childcare.go.kr/route/soap/acntRpt/"+operation+".ws/"+operation+".ws?wsdl"
    headers = {'content-type': 'application/soap+xml'}
    preXml = \
        '<?xml version="1.0"?>\n' + \
        '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xxx="'+url+'">\n' + \
        '   <soap:Header></soap:Header>\n' + \
        '   <soap:Body>\n' + \
        '       <xxx:'+operation+'>\n' + \
        '           <Request>\n' + \
        '               <C_AUTH_KEY>A56AE60160DB4FE98E8B445F18558AD2</C_AUTH_KEY>\n'
    tailXml = \
        '           </Request>\n' + \
        '       </xxx:'+operation+'>\n' + \
        '   </soap:Body>\n' + \
        '</soap:Envelope>\n'

    reqMsg = preXml+body+tailXml
    print(reqMsg)
    print("============post===========")
    resMsg = requests.post(url, data=reqMsg.encode('utf-8'), headers=headers, verify=False)
    print("============end==========")
    print(resMsg.content)
    content = makeSimpleXml(resMsg.content.decode('utf-8'))

    record, created = Record.objects.get_or_create(business=business, operation=operation, year=year, gubun=gubun, defaults={'data': "", 'result_code': -1, 'result_msg': ""})
    record.data = reqMsg
    print(resMsg.status_code)
    record.result_code = content[0]
    record.result_msg = content[1]
    record.regdatetime = datetime.datetime.now()
    record.save()

    redirect_url = redirect('show_record')
    redirect_url['Location'] += '?operation='+operation+'&year='+year+'&gubun='+gubun
    return redirect_url;

def show_record(request):
    business = get_object_or_404(Business, pk=request.session['business'])
    operation = request.GET.get("operation")
    year = request.GET.get('year')
    gubun = request.GET.get('gubun')

    if operation == "acRptMonthSum":
        roofName = "SR"
        column_list = ["구분", "계정코드", "합계금액", "전표개수"]
    elif operation == "acRptBudget":
        roofName = "BGTR"
        column_list = ["구분", "계정코드", "예산금액", "산출기초"]
    elif operation == "acRptStacnt":
        roofName = "STR"
        column_list = ["구분", "계정코드", "결산금액", "비고"]
    else:
        return render(request, 'childcare/result.html', {'msg': "오퍼레이션오류"})
    
    record = get_object_or_404(Record, business=business, operation=operation, year=year, gubun=gubun)
    root = ET.fromstring(record.data)
    Body = root.find("{http://schemas.xmlsoap.org/soap/envelope/}Body")
    Operation = Body.find("{https://stgapi.childcare.go.kr/route/soap/acntRpt/"+operation+".ws/"+operation+".ws?wsdl}"+operation)
    Request = Operation.find("Request")
    r_list = Request.findall(roofName)

    record_list = []
    for r in r_list:
        row = []
        for child in r.getchildren():
            row.append(child.text)
        record_list.append(row)
    return render(request, 'childcare/result.html', {'column_list': column_list, 'record_list': record_list, 'status_code': record.result_code, 'content': record.result_msg})


import xml.etree.ElementTree as ET
def makeSimpleXml(xml):
    content = []
    root = ET.fromstring(xml)
    for code in root.iter("RESULTCODE"):
        content.append(code.text)
    for code in root.iter("RESULTMSG"):
        content.append(code.text)
    return content



def xmlTest(request):
    f = open("childcare/xmlTest2.xml", 'r')
    body = f.read()
    #url = "https://api.childcare.go.kr/route/soap/acntRpt/acRptMonthSum.ws/acRptMonthSum.ws"
    #headers = {'content-type': 'application/soap+xml'}
    #content = requests.post(url, data=body.encode('utf-8'), headers=headers, verify=False)
    #a = content.content
    #result = a.decode('utf-8')
    #content.close
    root = ET.fromstring(body)
    Body = root.find("{http://schemas.xmlsoap.org/soap/envelope/}Body")
    operation = Body.find("{https://api.childcare.go.kr/route/soap/acntRpt/acRptMonthSum.ws/acRptMonthSum.ws}acRptMonthSum")
    Request = operation.find("Request")
    SR = Request.findall("SR")

    sr_list = []
    for sr in SR:
        row = {}
        for child in sr.getchildren():
            row[child.tag] = child.text
        sr_list.append(row)
    return render(request, 'childcare/xmlTest.html', {'sr_list': sr_list})


def non_request_childcare(business, operation, year, gubun, body):
    url = "https://api.childcare.go.kr/route/soap/acntRpt/"+operation+".ws/"+operation+".ws?wsdl"
    headers = {'content-type': 'application/soap+xml'}
    preXml = \
        '<?xml version="1.0"?>\n' + \
        '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xxx="'+url+'">\n' + \
        '   <soap:Header></soap:Header>\n' + \
        '   <soap:Body>\n' + \
        '       <xxx:'+operation+'>\n' + \
        '           <Request>\n' + \
        '               <C_AUTH_KEY>A56AE60160DB4FE98E8B445F18558AD2</C_AUTH_KEY>\n'
    tailXml = \
        '           </Request>\n' + \
        '       </xxx:'+operation+'>\n' + \
        '   </soap:Body>\n' + \
        '</soap:Envelope>\n'

    reqMsg = preXml+body+tailXml
    print(reqMsg)
    return None
