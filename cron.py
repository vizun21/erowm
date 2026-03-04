from .models import Setting, Business, TBLBANK
from django.db import connections
from django.utils import timezone

def cron_database_syn():
    try:
        tr_num = Setting.objects.get(name="transaction_num")

        query = """SELECT * FROM TBLBANK WHERE Bkid > """+str(tr_num.value)

        with connections['default'].cursor() as cursor:
            cursor.execute(query)
            columns = [ col[0] for col in cursor.description ]
            data_list = [ dict(zip(columns,row)) for row in cursor.fetchall() ]

        try:
            num = TBLBANK.objects.all().order_by('-Bkid').first().Bkid + 1
        except Exception:
            num = 1

        for data in data_list:
            try:
                business = Business.objects.get(account__account_number=data['Bkacctno'])

                # Bkdate: 뱅크다는 'YYYYMMDD' 또는 'YYYYMMDDHHMMSS' 형식으로 전달
                raw_date = str(data['Bkdate']).replace('-', '').replace(' ', '').replace(':', '')
                try:
                    if len(raw_date) >= 14:
                        bkdate_str = raw_date[:4]+'-'+raw_date[4:6]+'-'+raw_date[6:8]+' '+raw_date[8:10]+':'+raw_date[10:12]+':'+raw_date[12:14]
                    else:
                        bkdate_str = raw_date[:4]+'-'+raw_date[4:6]+'-'+raw_date[6:8]
                except Exception:
                    bkdate_str = str(data['Bkdate'])[:10]

                TBLBANK.objects.create(
                    Bkid=num,
                    Bkdivision=1,
                    direct=False,
                    Mid=data['Mid'],
                    Bkacctno=data['Bkacctno'],
                    Bkname=data['Bkname'],
                    Bkdate=bkdate_str,
                    Bkjukyo=data['Bkjukyo'],
                    Bkinput=data['Bkinput'],
                    Bkoutput=data['Bkoutput'],
                    Bkjango=data['Bkjango'],
                    business=business
                )
                tr_num.value = data['Bkid']
                tr_num.save()
                num += 1
            except Business.DoesNotExist:
                print(str(timezone.now())+" [cron] 계좌번호 매칭 사업장 없음: "+str(data.get('Bkacctno')))
            except Exception as inner_ex:
                print(str(timezone.now())+" [cron] 거래 저장 오류: "+str(inner_ex))

        print(str(timezone.now())+" cron complete")
    except Exception as ex:
        print("--"+str(timezone.now())+" "+str(ex))
