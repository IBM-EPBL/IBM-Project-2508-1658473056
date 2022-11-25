# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 18:55:33 2022

@author: Rohith
"""
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from collections import UserDict
from threading import activeCount
from turtle import st
import ibm_db
import ibm_db_dbi
import re
import io
from flask import Flask, redirect, session,url_for, request,render_template
COS_ENDPOINT="https://s3.jp-tok.cloud-object-storage.appdomain.cloud"
COS_API_KEY_ID="jTuq9SgGUGZ7PB3kbz8PO34PIjfnvbC_w03eD0_MyzU4"
COS_INSTANCE_CRN="crn:v1:bluemix:public:cloud-object-storage:global:a/76d200e982db41eabf28071cb42c5c4e:7de5a48d-85a5-4730-aeb0-b8571a96124c::"


cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

app=Flask(__name__)

app.secret_key='a'
#print('hi')
conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=125f9f61-9715-46f9-9399-c8177b21803b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30426;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=glv80047;PWD=VDWHzoVzcvVLbUVx;",'','')
@app.route('/')

def homer():
    return render_template('signuplogin.html')
@app.route('/login',methods=["GET",'POST'])
def login():
    global userid
    msg=' '
    
    if request.method == 'POST':
        username=request.form['nm']
        password=request.form['passi']
        if(username=="123456" and password=="123456"):
            return render_template('admin.html',msg=msg)
        else:
            sql= "SELECT * FROM user where username=? AND password=?"
            stmt=ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,username)
            ibm_db.bind_param(stmt,2,password)
            ibm_db.execute(stmt)
            account=ibm_db.fetch_assoc(stmt)
            print(account)
            if account:
                session['Loggedin']=True
                session['id']=account['USERNAME']
                userid=account['USERNAME']
                
                session['username']=account['USERNAME']
                msg='logged in successfully'
                
                
                query="select * from product"
                stmt=ibm_db.prepare(conn,query)
                ibm_db.execute(stmt)
                products=[]
                while True:
                    obj=ibm_db.fetch_tuple(stmt)
                    if(obj):
                        products.append(obj)
                    else:
                        break
                print(products)
                return render_template('dashboard.html',products=products)
            else:
                msg='Incorrect user credentials'
                return render_template('signuplogin.html',msg=msg)
    else:
        return render_template('signuplogin.html')
@app.route('/register',methods=['GET','POST'])
def register():
    msg=' '
    if request.method=='POST':
        username=request.form['nm']
        password=request.form['passi']
        repeatpass=request.form['repassi']
        email=request.form['email']
       
        sql="SELECT * FROM user WHERE username=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg='Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            msg='Invalid email address and enter all details!'
            
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg= 'name must contain only characters and numbers !'
        else:
            
            insert_sql="INSERT INTO user VALUES(?,?,?,?)"
            prep_stmt=ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(prep_stmt,1,username)
            ibm_db.bind_param(prep_stmt,2,password)
            ibm_db.bind_param(prep_stmt,3,repeatpass)
            ibm_db.bind_param(prep_stmt,4,email)
            ibm_db.execute(prep_stmt)
           
            msg='You have successfully registered !'
    elif request.method == 'POST':
        msg='Please fill out the form !'
    return render_template('signuplogin.html',msg=msg)
@app.route('/insert',methods=['GET','POST'])
def insert():
    msg=' '
    print("working1")
    if request.method=='POST':
        pname=request.form['b1']
        pid=request.form['pid']
        ptype=request.form['pptype']
        offer=request.form['o1']
        price=request.form['price']
        sql="SELECT * FROM PRODUCT WHERE BRAND=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,pname)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg='Product already exists !'
       
        else: 
            f = request.files['imgup']
            prod_img_name=f"img_{pid}"
            print(prod_img_name)
            try:
                part_size = 1024 * 1024 * 5
             
                file_threshold = 1024 * 1024 * 15
             
                transfer_config = ibm_boto3.s3.transfer.TransferConfig(
                        multipart_threshold=file_threshold,
                        multipart_chunksize=part_size
                    )
             
                content = f.read()
                cos.Object('prieeass1', prod_img_name).upload_fileobj(
                            Fileobj=io.BytesIO(content),
                            Config=transfer_config
                        )
             
            except ClientError as be:
                    # print("CLIENT ERROR: {0}\n".format(be))
                    return redirect(url_for('login'))
             
            except Exception as e:
                    # print("Unable to complete multi-part upload: {0}".format(e))
                    return redirect(url_for('login'))
             

            insert_sql="INSERT INTO product VALUES(?,?,?,?,?,?)"
            prep_stmt=ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(prep_stmt,1,prod_img_name)
            ibm_db.bind_param(prep_stmt,2,pname)
            ibm_db.bind_param(prep_stmt,3,ptype)
            ibm_db.bind_param(prep_stmt,4,offer)
            ibm_db.bind_param(prep_stmt,5,pid)
            ibm_db.bind_param(prep_stmt,6,price)
            
            ibm_db.execute(prep_stmt)
           
            msg='Product details successfully registered !'
    elif request.method == 'POST':
        msg='Please fill out the form !'
    return render_template('signuplogin.html',msg=msg)
if __name__=='__main__':
    app.run()
        
        