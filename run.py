#!/usr/bin/env python3

import argparse
import json
import os
import re
import requests
import smtplib

def sendEmail(*, email, password, receiver_email, data):
    # https://myaccount.google.com/u/4/lesssecureapps?pageId=none
    if email and password and receiver_email:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        sender_email = email
        server.login(email, password)
        server.sendmail(sender_email, receiver_email, data['status'])
        server.quit()

def CheckCase(credentials, args):
    caseID = credentials.get("caseID", None)
    assert caseID, "caseID is specified!"
    email = credentials.get("email", None)
    password = credentials.get("password", None)
    receiver_email = credentials.get("receiver_email", None)
    payload = {'appReceiptNum': caseID}
    r = requests.post('https://egov.uscis.gov/casestatus/mycasestatus.do', data=payload)
    time = re.search(r'(?<=On ).+(?=\, 2020,)', r.text)
    case = re.search(r'(?<=<h1>).+(?=\</h1>)', r.text)
    if(r.status_code != requests.codes.ok or case == None):
        print("Warning: Case number might be wrong")
        return
    print('Status: ' + case.group())
    timeStr = time.group(0).split(',')
    print(timeStr[0] + ', 2020')
    data = {'status' : case.group()}
    if os.path.exists(args.status):
        with open(args.status) as f:
            old_data = json.load(f)
            if old_data['status'] != data['status']:
                print("Status change!")
                try:
                    sendEmail(email=email, password=password,
                              receiver_email=receiver_email, data=data)
                except:
                    print("Warning: Unable to send email!")
    else:
        try:
            sendEmail(email=email, password=password,
                      receiver_email=receiver_email, data=data)
        except:
            print("Warning: Unable to send email!")
    with open(args.status, 'w') as f:
        json.dump(data, f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--credentials',
                        type=str, default="credentials.json")
    parser.add_argument('--status',
                        type=str, default="status.json")
    args = parser.parse_args()
    assert os.path.exists(args.credentials), "Need credentials.json!"
    with open(args.credentials) as f:
        credentials = json.load(f)
        CheckCase(credentials, args)

if __name__ == "__main__":
    main()
