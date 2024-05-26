from flask import Flask,render_template,request,jsonify,send_from_directory,redirect, url_for
import os
from sqlite3 import *
import ast

class server:
    def __init__(self,app,mode=1):
        self.o=os.getcwd() if mode==1 else '/home/nitin/billing_server'
        self.app=app

        @self.app.route('/emptypage')
        @self.app.route('/')
        @self.app.route('/home')
        def home():return self.home()

        @self.app.route('/home/favicon.ico')
        @self.app.route('/favicon.ico')
        @self.app.route('/sales/favicon.ico')
        @self.app.route('/purchase/favicon.ico')
        @self.app.route('/manage_address/favicon.ico')
        def favicon():return self.favicon()

        @self.app.route('/sales/<cmp>')
        def sales(cmp):return self.sales(cmp)

        @self.app.route('/purchase/<cmp>')
        def purchase(cmp):return self.purchase(cmp)

        @self.app.route('/sales/get_add')
        @self.app.route('/purchase/get_add')
        @self.app.route('/manage_address/get_add')
        def addbook():return self.addbook()

        @self.app.route('/manage_address')
        def mng_add():return self.mng_add()

        @self.app.route('/manage_address/add', methods=['POST'])
        @self.app.route('/snew', methods=['POST'])
        @self.app.route('/bnew', methods=['POST'])
        def add_addr():return self.add_addr()

        @self.app.route('/manage_address/del', methods=['POST'])
        def del_addr():return self.del_addr()

        @self.app.route('/manage_address/upd', methods=['POST'])
        def upd_addr():return self.upd_addr()

        @self.app.route('/cmps')
        def mng_cmps():return self.mng_cmps()

        @self.app.route('/cmps/add', methods=['POST'])
        def add_cmps():return self.add_cmps()

        @self.app.route('/cmps/del', methods=['POST'])
        def del_cmps():return self.del_cmps()

        @self.app.route('/cmps/upd', methods=['POST'])
        def upd_cmps():return self.upd_cmps()

        @self.app.route('/acs')
        def mng_acs():return self.mng_acs()

        @self.app.route('/acs/add', methods=['POST'])
        def add_acs():return self.add_acs()

        @self.app.route('/acs/del', methods=['POST'])
        def del_acs():return self.del_acs()

        @self.app.route('/acs/upd', methods=['POST'])
        def upd_acs():return self.upd_acs()

        @self.app.route('/home/get_cmps/<mode>')
        @self.app.route('/cmps/get_cmps/<mode>')
        def cmps(mode):return self.cmps(mode)

        @self.app.route('/sales/get_acs')
        @self.app.route('/acs/get_acs')
        def acs():return self.acs()

        @self.app.route('/sales/get_invno/<cmp>')
        def sinvno(cmp):return self.sinvno(cmp)

        @self.app.route('/purchase/get_invno/<cmp>')
        def pinvno(cmp):return self.pinvno(cmp)

        @self.app.route('/sales/bill',methods=['POST','GET'])
        def sales_bill():return self.sales_bill()

        @self.app.route('/purchase/bill',methods=['POST','GET'])
        def purchase_bill():return self.purchase_bill()

    def home(self):return render_template('home.html')

    def favicon(self):return send_from_directory(os.path.join(self.app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

    def sales(self,cmp):return render_template('sales.html',cmpn=self.cmp_dtls(cmp)['name'],add1=self.cmp_dtls(cmp)['add1'],add2=self.cmp_dtls(cmp)['add2'],add3=self.cmp_dtls(cmp)['add3'],gstin=self.cmp_dtls(cmp)['gstn'],stn=self.cmp_dtls(cmp)['stnm'],stc=self.cmp_dtls(cmp)['stcd'])

    def purchase(self,cmp):return render_template('purchase.html',cmpn=self.cmp_dtls(cmp)['name'],add1=self.cmp_dtls(cmp)['add1'],add2=self.cmp_dtls(cmp)['add2'],add3=self.cmp_dtls(cmp)['add3'],gstin=self.cmp_dtls(cmp)['gstn'],stn=self.cmp_dtls(cmp)['stnm'],stc=self.cmp_dtls(cmp)['stcd'])

    def addbook(self):
        updated_data=[]
        con=connect(self.o+'/addbook1.db')
        cur=con.cursor()
        cur.execute('select * from addbook')
        l=['sno','comp','add','gst','stnc']
        for i in cur.fetchall():
            d={}
            for j in range(5):d[l[j]]=str(i[j])
            updated_data.append(d)
        con.close()
        return jsonify(updated_data)

    def mng_add(self):return render_template('manage_address.html')

    def add_addr(self):
        data = request.json
        name=data['cname']
        addr=data['addrs']
        gstn=data['gstin']
        stnc=data['stnam']+' '+data['stcod']
        con = connect(self.o+'/addbook1.db')
        cur = con.cursor()
        cur.execute('select * from addbook order by sno')
        rows = cur.fetchall()
        g=[]
        for i in rows:g.append(i[-2])
        for i in g:
            if gstn.lower()==i.lower():return jsonify({"message":'GSTIN Already Exists!'})
        cur.execute(f"insert into addbook values({self.sno_calc(self.o+'/addbook1.db','addbook')},'{name}','{addr}','{gstn}','{stnc}')")
        con.commit()
        con.close()
        return jsonify({"message":'Address Added Successfully!'})

    def del_addr(self):
        data = request.json
        sno=int(data['sno'])
        con = connect(self.o+'/addbook1.db')
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

    def upd_addr(self):
        data = request.json
        sno=int(data['sno'])
        name=data['cname']
        addr=data['addrs']
        gstn=data['gstin']
        stnc=data['stnam']+' '+data['stcod']
        con = connect(self.o+'/addbook1.db')
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

    def mng_cmps(self):return render_template('cmps.html')

    def add_cmps(self):
        data = request.json
        name=data['cname']
        addr=data['addrs']
        gstn=data['gstin']
        stnc=data['stnam']+' '+data['stcod']
        a=open(self.o+'/nop.txt','r')
        js1=ast.literal_eval(a.read())
        a.close()
        a=open(self.o+'/nos.txt','r')
        js2=ast.literal_eval(a.read())
        a.close()
        js1[name]=js2[name]=1
        a=open(self.o+'/nop.txt','w')
        a.write(str(js1))
        a.close()
        a=open(self.o+'/nos.txt','w')
        a.write(str(js2))
        a.close()
        con = connect(self.o+'/cmps1.db')
        cur = con.cursor()
        cur.execute('select * from cmps order by sno')
        rows = cur.fetchall()
        g=[]
        for i in rows:g.append(i[-2])
        for i in g:
            if gstn.lower()==i.lower():return jsonify({"message":'GSTIN Already Exists!'})
        cur.execute(f"insert into cmps values({self.sno_calc(self.o+'/cmps1.db','cmps')},'{name}','{addr}','{gstn}','{stnc}')")
        con.commit()
        con.close()
        return jsonify({"message":'Company Added Successfully!'})

    def del_cmps(self):
        data = request.json
        sno=int(data['sno'])
        con = connect(self.o+'/cmps1.db')
        cur = con.cursor()
        cur.execute('select * from cmps order by sno')
        rows = cur.fetchall()
        name=rows[sno-1][1]
        rows.pop(sno-1)
        cur.execute(f'delete from cmps where sno={sno}')
        con.commit()
        a=open(self.o+'/nop.txt','r')
        js1=ast.literal_eval(a.read())
        a.close()
        a=open(self.o+'/nos.txt','r')
        js2=ast.literal_eval(a.read())
        a.close()
        js1.pop(name)
        js2.pop(name)
        a=open(self.o+'/nop.txt','w')
        a.write(str(js1))
        a.close()
        a=open(self.o+'/nos.txt','w')
        a.write(str(js2))
        a.close()
        for i in range(len(rows[sno-1:])):
            cur.execute(f"update cmps set sno={sno} where sno={sno+1}")
            sno+=1
        con.commit()
        con.close()
        return jsonify({"message":'Company Deleted Successfully!'})

    def upd_cmps(self):
        data = request.json
        sno=int(data['sno'])
        name=data['cname']
        addr=data['addrs']
        gstn=data['gstin']
        stnc=data['stnam']+' '+data['stcod']
        con = connect(self.o+'/cmps1.db')
        cur = con.cursor()
        cur.execute('select * from cmps order by sno')
        rows = cur.fetchall()
        onme=rows[sno-1][1]
        g=[]
        a=open(self.o+'/nop.txt','r')
        js1=ast.literal_eval(a.read())
        a.close()
        a=open(self.o+'/nos.txt','r')
        js2=ast.literal_eval(a.read())
        a.close()
        js1[name]=js1[onme]
        js2[name]=js2[onme]
        js1.pop(onme)
        js2.pop(onme)
        a=open(self.o+'/nop.txt','w')
        a.write(str(js1))
        a.close()
        a=open(self.o+'/nos.txt','w')
        a.write(str(js2))
        a.close()
        for i in rows:g.append(i[-2])
        for i in range(len(g)):
            if sno-1!=i and gstn.lower()==g[i].lower():return jsonify({"message":'GSTIN Already Exists!'})
        cur.execute(f"update cmps set sno={sno}, name='{name}', addr='{addr}', gstin='{gstn}', stc='{stnc}' where sno={sno}")
        con.commit()
        con.close()
        return jsonify({"message":'Company Details Updated Successfully!'})

    def mng_acs(self):return render_template('acs.html')

    def add_acs(self):
        data = request.json
        bnk=data['bnk']
        bnb=data['bnb']
        acn=data['acn']
        ifc=data['ifc']
        con = connect(self.o+'/acs1.db')
        cur = con.cursor()
        cur.execute('select * from acs order by sno')
        rows = cur.fetchall()
        n=[]
        for i in rows:n.append(i[1])
        for i in range(len(n)):
            if acn.lower()==n[i].lower():return jsonify({"message":'A/C No. Already Exists!'})
        cur.execute(f"insert into acs values({self.sno_calc(self.o+'/acs1.db','acs')},'{acn}','{bnk}','{bnb}','{ifc}')")
        con.commit()
        con.close()
        return jsonify({"message":'Account Added Successfully!'})

    def del_acs(self):
        data = request.json
        sno=int(data['sno'])
        con = connect(self.o+'/acs1.db')
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
    
    def upd_acs(self):
        data = request.json
        sno=int(data['sno'])
        bnk=data['bnk']
        bnb=data['bnb']
        acn=data['acn']
        ifc=data['ifc']
        con = connect(self.o+'/acs1.db')
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

    def cmps(self,mode):
        updated_data=[]
        con=connect(self.o+'/cmps1.db')
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

    def acs(self):
        updated_data=[]
        con=connect(self.o+'/acs1.db')
        cur=con.cursor()
        cur.execute('select * from acs')
        l=['sno','acn','bnk','bnb','ifc']
        for i in cur.fetchall():
            d={}
            for j in range(5):d[l[j]]=str(i[j]).replace('\n',' ')
            updated_data.append(d)
        con.close()
        return jsonify(updated_data)

    def sinvno(self,cmp):
        a=open(self.o+'/nos.txt','r')
        js=ast.literal_eval(a.read())
        a.close()
        return jsonify([{'invno':str(js[cmp])}])

    def pinvno(self,cmp):
        a=open(self.o+'/nop.txt','r')
        js=ast.literal_eval(a.read())
        a.close()
        return jsonify([{'invno':str(js[cmp])}])

    def sno_calc(self,db,tb):
        con=connect(db)
        cur=con.cursor()
        cur.execute(f"select * from {tb}")
        n=len(cur.fetchall())+1
        con.close()
        return n

    def cmp_dtls(self,cmp):
        con=connect(self.o+'/cmps1.db')
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

    def sales_bill(self):
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
                    itd[j]+=f"{data[j+str(i)] if j!='amt' else self.format_inr(data[j+str(i)])}\n"
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
            elif l[i] in['amt6','cgst','sgst','igst']:bdtl[str(i+1)]=self.format_inr(data[l[i]])
            else:bdtl[str(i+1)]=data[l[i]]

        return jsonify({"message":f"Bill {data['invno']} Created Successfully!"})

    def purchase_bill(self):
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
                    itd[j]+=f"{data[j+str(i)] if j!='amt' else self.format_inr(data[j+str(i)])}\n"
        for i in range(1,n+1):itd['sno']+=f"{str(i)}.\n"
        for j in ['sno','item','hsn','qty','rte','uom','amt']:itd[j]=itd[j].strip('\n')
        
        l=['1','invno','date','sinvno','otr','6','7','8','9','10','11','12','13','amt6','amtw','cgstin','17','18','19']
        mdat={1:'Copy',6:badd,7:itd['sno'],8:itd['item'],9:itd['hsn'],10:itd['qty'],11:itd['rte'],12:itd['uom'],13:itd['amt'],17:cadd,18:cadd,19:fadd}

        bdtl={}
        for i in range(len(l)):
            if l[i][0].isdigit():bdtl[l[i]]=mdat[int(l[i])]
            elif l[i]=='amt6':bdtl[str(i+1)]=self.format_inr(data[l[i]])
            else:bdtl[str(i+1)]=data[l[i]]

        return jsonify({"message":f"Bill {data['invno']} Created Successfully!"})
    
    def format_inr(self,number):
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

if __name__=='__main__':
    app=Flask(__name__,template_folder='templates')
    a=server(app,1)
    app.run(debug=1,host='0.0.0.0')
    