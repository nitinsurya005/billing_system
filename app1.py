from flask import Flask,render_template,request,jsonify,send_from_directory,redirect, url_for
import os
from sqlite3 import *
import ast

mode=1

o=os.getcwd() if mode==1 else '/home/nitin/billing_server'

def sno_calc(db,tb):
    con=connect(db)
    cur=con.cursor()
    cur.execute(f"select * from {tb}")
    n=len(cur.fetchall())+1
    con.close()
    return n

def cmp_dtls(cmp):
    con=connect(o+'/cmps1.db')
    cur=con.cursor()
    cur.execute(f'select * from cmps where name="{cmp}"')
    row=cur.fetchall()[0]
    con.close()
    add=row[2].split('\n')
    stn=''
    stc=row[4].split()[-1]
    for i in row[4].split()[:-1]:stn+=f"{i} "
    dtls={'name':row[1],'add1':add[0],'add2':add[1],'add3':add[2],'gstn':row[3],'stnm':stn.strip(),'stcd':stc}
    return dtls

def format_inr(number):
    if len(number)<4:return number
    inr=number[::-1][:3]+','
    j=0
    for i in number[::-1][3:]:
        inr+=i
        j+=1
        if j==2:
            inr+=','
            j=0
    return inr[::-1].strip(',')

app=Flask(__name__,template_folder='templates')

@app.route('/emptypage')
@app.route('/')
@app.route('/home')
def home():return render_template('home.html')

@app.route('/home/favicon.ico')
@app.route('/favicon.ico')
@app.route('/sales/favicon.ico')
@app.route('/purchase/favicon.ico')
@app.route('/manage_address/favicon.ico')
def favicon():return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/sales/<cmp>')
def sales(cmp):return render_template('sales.html',cmpn=cmp_dtls(cmp)['name'],add1=cmp_dtls(cmp)['add1'],add2=cmp_dtls(cmp)['add2'],add3=cmp_dtls(cmp)['add3'],gstin=cmp_dtls(cmp)['gstn'],stn=cmp_dtls(cmp)['stnm'],stc=cmp_dtls(cmp)['stcd'])

@app.route('/purchase/<cmp>')
def purchase(cmp):return render_template('purchase.html',cmpn=cmp_dtls(cmp)['name'],add1=cmp_dtls(cmp)['add1'],add2=cmp_dtls(cmp)['add2'],add3=cmp_dtls(cmp)['add3'],gstin=cmp_dtls(cmp)['gstn'],stn=cmp_dtls(cmp)['stnm'],stc=cmp_dtls(cmp)['stcd'])

@app.route('/sales/get_add')
@app.route('/purchase/get_add')
@app.route('/manage_address/get_add')
def addbook():
    updated_data=[]
    con=connect(o+'/addbook1.db')
    cur=con.cursor()
    cur.execute('select * from addbook')
    l=['sno','comp','add','gst','stnc']
    for i in cur.fetchall():
        d={}
        for j in range(5):d[l[j]]=str(i[j])
        updated_data.append(d)
    con.close()
    return jsonify(updated_data)

@app.route('/manage_address')
def mng_add():return render_template('manage_address.html')

@app.route('/manage_address/add', methods=['POST'])
@app.route('/snew', methods=['POST'])
@app.route('/bnew', methods=['POST'])
def add_addr():
    data = request.json
    name=data['cname']
    addr=data['addrs']
    gstn=data['gstin']
    stnc=data['stnam']+' '+data['stcod']
    con = connect(o+'/addbook1.db')
    cur = con.cursor()
    cur.execute('select * from addbook order by sno')
    rows = cur.fetchall()
    g=[]
    for i in rows:g.append(i[-2])
    for i in g:
        if gstn.lower()==i.lower():return jsonify({"message":'GSTIN Already Exists!'})
    cur.execute(f"insert into addbook values({sno_calc(o+'/addbook1.db','addbook')},'{name}','{addr}','{gstn}','{stnc}')")
    con.commit()
    con.close()
    return jsonify({"message":'Address Added Successfully!'})

@app.route('/manage_address/del', methods=['POST'])
def del_addr():
    data = request.json
    sno=int(data['sno'])
    con = connect(o+'/addbook1.db')
    cur = con.cursor()
    cur.execute('select * from addbook order by sno')
    rows = cur.fetchall()
    rows.pop(sno-1)
    cur.execute(f'delete from addbook where sno={sno}')
    con.commit()
    for i in range(len(rows[sno-1:])):
        cur.execute(f"update addbook set sno={sno} where sno={sno+1}")
        sno+=1
    con.commit()
    con.close()
    return jsonify({"message":'Address Deleted Successfully!'})

@app.route('/manage_address/upd', methods=['POST'])
def upd_addr():
    data = request.json
    sno=int(data['sno'])
    name=data['cname']
    addr=data['addrs']
    gstn=data['gstin']
    stnc=data['stnam']+' '+data['stcod']
    con = connect(o+'/addbook1.db')
    cur = con.cursor()
    cur.execute('select * from addbook order by sno')
    rows = cur.fetchall()
    g=[]
    for i in rows:g.append(i[-2])
    for i in range(len(g)):
        if sno-1!=i and gstn.lower()==g[i].lower():return jsonify({"message":'GSTIN Already Exists!'})
    cur.execute(f"update addbook set sno={sno}, name='{name}', ad='{addr}', gstin='{gstn}', stc='{stnc}' where sno={sno}")
    con.commit()
    con.close()
    return jsonify({"message":'Address Updated Successfully!'})

@app.route('/cmps')
def mng_cmps():return render_template('cmps.html')

@app.route('/cmps/add', methods=['POST'])
def add_cmps():
    data = request.json
    name=data['cname']
    addr=data['addrs']
    gstn=data['gstin']
    stnc=data['stnam']+' '+data['stcod']
    a=open(o+'/nop.txt','r')
    js1=ast.literal_eval(a.read())
    a.close()
    a=open(o+'/nos.txt','r')
    js2=ast.literal_eval(a.read())
    a.close()
    js1[name]=js2[name]=1
    a=open(o+'/nop.txt','w')
    a.write(str(js1))
    a.close()
    a=open(o+'/nos.txt','w')
    a.write(str(js2))
    a.close()
    con = connect(o+'/cmps1.db')
    cur = con.cursor()
    cur.execute('select * from cmps order by sno')
    rows = cur.fetchall()
    g=[]
    for i in rows:g.append(i[-2])
    for i in g:
        if gstn.lower()==i.lower():return jsonify({"message":'GSTIN Already Exists!'})
    cur.execute(f"insert into cmps values({sno_calc(o+'/cmps1.db','cmps')},'{name}','{addr}','{gstn}','{stnc}')")
    con.commit()
    con.close()
    return jsonify({"message":'Company Added Successfully!'})

@app.route('/cmps/del', methods=['POST'])
def del_cmps():
    data = request.json
    sno=int(data['sno'])
    con = connect(o+'/cmps1.db')
    cur = con.cursor()
    cur.execute('select * from cmps order by sno')
    rows = cur.fetchall()
    name=rows[sno-1][1]
    rows.pop(sno-1)
    cur.execute(f'delete from cmps where sno={sno}')
    con.commit()
    a=open(o+'/nop.txt','r')
    js1=ast.literal_eval(a.read())
    a.close()
    a=open(o+'/nos.txt','r')
    js2=ast.literal_eval(a.read())
    a.close()
    js1.pop(name)
    js2.pop(name)
    a=open(o+'/nop.txt','w')
    a.write(str(js1))
    a.close()
    a=open(o+'/nos.txt','w')
    a.write(str(js2))
    a.close()
    for i in range(len(rows[sno-1:])):
        cur.execute(f"update cmps set sno={sno} where sno={sno+1}")
        sno+=1
    con.commit()
    con.close()
    return jsonify({"message":'Company Deleted Successfully!'})

@app.route('/cmps/upd', methods=['POST'])
def upd_cmps():
    data = request.json
    sno=int(data['sno'])
    name=data['cname']
    addr=data['addrs']
    gstn=data['gstin']
    stnc=data['stnam']+' '+data['stcod']
    con = connect(o+'/cmps1.db')
    cur = con.cursor()
    cur.execute('select * from cmps order by sno')
    rows = cur.fetchall()
    onme=rows[sno-1][1]
    g=[]
    a=open(o+'/nop.txt','r')
    js1=ast.literal_eval(a.read())
    a.close()
    a=open(o+'/nos.txt','r')
    js2=ast.literal_eval(a.read())
    a.close()
    js1[name]=js1[onme]
    js2[name]=js2[onme]
    js1.pop(onme)
    js2.pop(onme)
    a=open(o+'/nop.txt','w')
    a.write(str(js1))
    a.close()
    a=open(o+'/nos.txt','w')
    a.write(str(js2))
    a.close()
    for i in rows:g.append(i[-2])
    for i in range(len(g)):
        if sno-1!=i and gstn.lower()==g[i].lower():return jsonify({"message":'GSTIN Already Exists!'})
    cur.execute(f"update cmps set sno={sno}, name='{name}', addr='{addr}', gstin='{gstn}', stc='{stnc}' where sno={sno}")
    con.commit()
    con.close()
    return jsonify({"message":'Company Details Updated Successfully!'})

@app.route('/acs')
def mng_acs():return render_template('acs.html')

@app.route('/acs/add', methods=['POST'])
def add_acs():
    data = request.json
    bnk=data['bnk']
    bnb=data['bnb']
    acn=data['acn']
    ifc=data['ifc']
    con = connect(o+'/acs1.db')
    cur = con.cursor()
    cur.execute('select * from acs order by sno')
    rows = cur.fetchall()
    n=[]
    for i in rows:n.append(i[1])
    for i in range(len(n)):
        if acn.lower()==n[i].lower():return jsonify({"message":'A/C No. Already Exists!'})
    cur.execute(f"insert into acs values({sno_calc(o+'/acs1.db','acs')},'{acn}','{bnk}','{bnb}','{ifc}')")
    con.commit()
    con.close()
    return jsonify({"message":'Account Added Successfully!'})

@app.route('/acs/del', methods=['POST'])
def del_acs():
    data = request.json
    sno=int(data['sno'])
    con = connect(o+'/acs1.db')
    cur = con.cursor()
    cur.execute('select * from acs order by sno')
    rows = cur.fetchall()
    rows.pop(sno-1)
    cur.execute(f'delete from acs where sno={sno}')
    con.commit()
    for i in range(len(rows[sno-1:])):
        cur.execute(f"update acs set sno={sno} where sno={sno+1}")
        sno+=1
    con.commit()
    con.close()
    return jsonify({"message":'Account Deleted Successfully!'})
    
@app.route('/acs/upd', methods=['POST'])
def upd_acs():
    data = request.json
    sno=int(data['sno'])
    bnk=data['bnk']
    bnb=data['bnb']
    acn=data['acn']
    ifc=data['ifc']
    con = connect(o+'/acs1.db')
    cur = con.cursor()
    cur.execute('select * from acs order by sno')
    rows = cur.fetchall()
    g=[]
    for i in rows:g.append(i[1])
    for i in range(len(g)):
        if sno-1!=i and acn.lower()==g[i].lower():return jsonify({"message":'A/C No. Already Exists!'})
    cur.execute(f"update acs set sno={sno}, acno='{acn}', bnk='{bnk}', bnb='{bnb}', ifsc='{ifc}' where sno={sno}")
    con.commit()
    con.close()
    return jsonify({"message":'Account Details Updated Successfully!'})

@app.route('/home/get_cmps/<mode>')
@app.route('/cmps/get_cmps/<mode>')
def cmps(mode):
    updated_data=[]
    con=connect(o+'/cmps1.db')
    cur=con.cursor()
    cur.execute('select * from cmps')
    for i in cur.fetchall():
        if int(mode)==1:updated_data.append({'name':i[1]})
        else:
            d={}
            l=['sno','comp','add','gst','stnc']
            for j in range(len(l)):d[l[j]]=str(i[j])
            updated_data.append(d)
    con.close()
    return jsonify(updated_data)

@app.route('/sales/get_acs')
@app.route('/acs/get_acs')
def acs():
    updated_data=[]
    con=connect(o+'/acs1.db')
    cur=con.cursor()
    cur.execute('select * from acs')
    l=['sno','acn','bnk','bnb','ifc']
    for i in cur.fetchall():
        d={}
        for j in range(5):d[l[j]]=str(i[j]).replace('\n',' ')
        updated_data.append(d)
    con.close()
    return jsonify(updated_data)

@app.route('/sales/get_invno/<cmp>')
def sinvno(cmp):
    a=open(o+'/nos.txt','r')
    js=ast.literal_eval(a.read())
    a.close()
    return jsonify([{'invno':str(js[cmp])}])

@app.route('/purchase/get_invno/<cmp>')
def pinvno(cmp):
    a=open(o+'/nop.txt','r')
    js=ast.literal_eval(a.read())
    a.close()
    return jsonify([{'invno':str(js[cmp])}])

@app.route('/sales/bill',methods=['POST','GET'])
def sales_bill():
    data = request.json

    sadd=f"{data['shipadd']}\nGSTIN/UIN   : {data['sgstin']}\nState Name  : {data['sstnam']}, Code : {data['sstcod']}"
    badd=f"{data['billadd']}\nGSTIN/UIN   : {data['bgstin']}\nState Name  : {data['bstnam']}, Code : {data['bstcod']}"
    cadd=f"{data['caddr']}\nGSTIN/UIN   : {data['cgstn']}\nState Name  : {data['cstnm']}, Code : {data['cstcd']}"
    fadd=f"for {data['compn']}\n \nAuthorized Signatory"

    itd={i:'' for i in ['sno','item','hsn','qty','rte','uom','amt']}
    n=0
    for i in range(1,6):
        f=1
        for j in ['item','hsn','qty','rte','uom','amt']:
            if data[j+str(i)]=='':f=0
        if f:
            n+=1
            for j in ['item','hsn','qty','rte','uom','amt']:
                itd[j]+=f"{data[j+str(i)] if j!='amt' else format_inr(data[j+str(i)])}\n"
    for i in range(1,n+1):itd['sno']+=f"{str(i)}.\n"
    for j in ['sno','item','hsn','qty','rte','uom','amt']:itd[j]=itd[j].strip('\n')
    
    bank=f"Bank : {data['bank']}, {data['branch']} Branch\nA/C. No.{data['a/cno']} IFSC Code: {data['ifscd']}"

    l=['1','invno','date','delnote','mot','bon','bond','8','ddocn','delnd','dispthr','dest','bol','mvno','15','tod',
       '17','18','19','20','21','22','23','amt6','amtw','cgstp','cgst','sgstp','sgst','igstp','igst','invt','33','34','35']
    mdat={1:'Copy',8:sadd,15:badd,17:itd['sno'],18:itd['item'],19:itd['hsn'],20:itd['qty'],21:itd['rte'],22:itd['uom'],23:itd['amt'],
          33:bank,34:cadd,35:fadd}

    bdtl={}
    for i in range(len(l)):
        if l[i][0].isdigit():bdtl[l[i]]=mdat[int(l[i])]
        elif l[i] in['amt6','cgst','sgst','igst']:bdtl[str(i+1)]=format_inr(data[l[i]])
        else:bdtl[str(i+1)]=data[l[i]]

    return jsonify({"message":f"Bill {data['invno']} Created Successfully!"})

@app.route('/purchase/bill',methods=['POST','GET'])
def purchase_bill():
    data = request.json
    
    badd=f"{data['billadd']}\nGSTIN/UIN   : {data['bgstin']}\nState Name  : {data['bstnam']}, Code : {data['bstcod']}"
    cadd=f"{data['caddr']}\nGSTIN/UIN   : {data['cgstn']}\nState Name  : {data['cstnm']}, Code : {data['cstcd']}"
    fadd=f"for {data['compn']}\n \nAuthorized Signatory"
    
    itd={i:'' for i in ['sno','item','hsn','qty','rte','uom','amt']}
    n=0
    for i in range(1,6):
        f=1
        for j in ['item','hsn','qty','rte','uom','amt']:
            if data[j+str(i)]=='':f=0
        if f:
            n+=1
            for j in ['item','hsn','qty','rte','uom','amt']:
                itd[j]+=f"{data[j+str(i)] if j!='amt' else format_inr(data[j+str(i)])}\n"
    for i in range(1,n+1):itd['sno']+=f"{str(i)}.\n"
    for j in ['sno','item','hsn','qty','rte','uom','amt']:itd[j]=itd[j].strip('\n')
    
    l=['1','invno','date','sinvno','otr','6','7','8','9','10','11','12','13','amt6','amtw','cgstin','17','18','19']
    mdat={1:'Copy',6:badd,7:itd['sno'],8:itd['item'],9:itd['hsn'],10:itd['qty'],11:itd['rte'],12:itd['uom'],13:itd['amt'],17:cadd,18:cadd,19:fadd}

    bdtl={}
    for i in range(len(l)):
        if l[i][0].isdigit():bdtl[l[i]]=mdat[int(l[i])]
        elif l[i]=='amt6':bdtl[str(i+1)]=format_inr(data[l[i]])
        else:bdtl[str(i+1)]=data[l[i]]

    return jsonify({"message":f"Bill {data['invno']} Created Successfully!"})

if __name__=='__main__':app.run(debug=1,host='0.0.0.0')