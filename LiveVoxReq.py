#!/usr/bin/python3.6
zvHelpInfo = """
This script is for running a REST API connection with LiveVox
        - Andy2 - 5/7/2019 - andrew.mccrevan@eos-usa.com
		
#############################################################################################################

Help
	This script requires 2 arguments to run (python3 LiveVoxReq.py <method> <data>)
		<method> = method inside the script you want to run
		<data> = data you want to pass to the method (just put 'x' if none is necesarry)
			example - "python3 LiveVoxReq.py CreateContact 123
			
		Methods:
						
			CreateContact(data)
				data = "acct#"*-*"lv hist id"
				
			UpdatePhone(data)
				data = "acct#"*-*"phone number"*-*"phone rank"*-*"phone block"*-*"lv hist id"
				
			NewPhone(data)
				data = "acct#"*-*"phone number"*-*"phone rank"*-*"phone block"*-*"cell consent"*-*"lv hist id"
				
			UpdateContact(data)
				data = "acct#"*-*"field name"*-*"field value"*-*"custom?"*-*"lv hist id"

#############################################################################################################

+-----------------------------------------------------------------------------------------------------------+
| REST action | HTTP method | Description                                                                   |
|-----------------------------------------------------------------------------------------------------------|
| Create      | POST        | Creates a new object and returns an ID to identify the object                 |
| Read        | GET         | Provides the requested object. Requires an ID.                                |
| Update      | PUT/POST    | Updates one or more values within the requested object. Requires an ID.       |
| Delete      | DELETE      | Deletes the requested object. Requires and ID. Not all objects can be deleted |
| Find        | POST        | Provides a list of matching objects based on the provided information         |
| List        | GET         | Lists all the existing objects                                                |
| List Info   | GET         | Provides information on how many objects may be returned in a List request.   |
+-----------------------------------------------------------------------------------------------------------+
+-------------------------------------------------------------------------------------------------------------------------------------------------+
| HTTP Response Code | Meaning | Description                                                                                                      |
|-------------------------------------------------------------------------------------------------------------------------------------------------|
| 200 OK             | Success | The request was successful and the response body contains more data                                              |
|                    |         |                                                                                                                  |
| 201 Created        | Success | A Create request was successful. The response body will usually contain an ID for the successfully created item. |     
|                    |         |     Bulk requests may have different response bodies                                                             |
|                    |         |                                                                                                                  |
| 202 Accepted       | Partial | The request wasn’t completely successful. More information is in the response body.                              |
|                    | Success |     Subsequent requests may be needed to resolve any issues.                                                     |
|                    |         |                                                                                                                  |
| 204 No Content     | Success | The request was successful. The response body contains no content.                                               |
|                    |         |     This is usually returned for an Update or Delete request.                                                    |
|                    |         |                                                                                                                  | 
| 400 Bad Request    | Failure | The request was invalid or contained incorrect information.                                                      |
|                    |         |     The body of the response should provide more information on the failure                                      |
|                    |         |                                                                                                                  |
| 401 Unauthorized   | Failure | The session is not valid. It may have expired or the request contained invalid credentials.                      |
|                    |         |     The user must successfully login before making any further request                                           |
|                    |         |                                                                                                                  |
| 403 Permission     | Failure | The user does not have permission to access the requested object                                                 |
|       Denied       |         |     and/or perform the method on the requested object.                                                           |
|                    |         |                                                                                                                  |
| 404 Not Found      | Failure | The requested object does not exist                                                                              |
|                    |         |                                                                                                                  |
| 405 Method         | Failure | The request contains an HTTP method that is invalid for the requested object                                     |
|     Not Supported  |         |                                                                                                                  |
|                    |         |                                                                                                                  |
| 409 Conflict       | Failure | The request cannot be processed as it currently stands. This is commonly the case for attempting to create       |
|                    |         |      duplicate object (i.e. objects with the same name or ID).                                                   |
|                    |         |          The user needs to modify the request to avoid the conflict.                                             |
|                    |         |                                                                                                                  |
| 500 Internal       | Failure | The request causes an unexpected error during processing.                                                        |
|     Server Error   |         |      More information should be provided in the response. This requires help from LiveVox to resolve.            |
|                    |         |                                                                                                                  |
| 502 Bad Gateway    | Failure | This request cannot be handled due to a configuration error. This requires help from LiveVox to resolve.         |
+-------------------------------------------------------------------------------------------------------------------------------------------------+
"""

import sys
import os
import datetime
import subprocess
import requests
import json

zvFunc = sys.argv[1]
zvData = sys.argv[2]

if "_" in zvData:
		zvData2 = zvData.replace("_"," ")
		zvData = zvData2

#==============================================================================================================
#------------------------------------ Login ------------------------------------------------------------
def Login():
	url = 'https://api.livevox.com/session/login'
	payload = {'clientName':'EOSUSA','userName':'Andrew.McCrevan','password':'Livevox10'}
	headers = {'content-type': 'application/json', 'LV-Access': '47bfb7cd-0a0c-469d-9ae2-e2f86e8104d3'}
	# 47bfb7cd-0a0c-469d-9ae2-e2f86e8104d3 or 87c6c071-8d4a-4457-91be-d529e62b876a
	r = requests.post(url, data=json.dumps(payload), headers=headers)
	print(r,r.text)
	if r == '<Response [401]>':
		return '401'
	else:
		zvSessionId = str(r.text)
		zvSessionId = zvSessionId.split(r'{"sessionId":"')[1]
		zvSessionId = zvSessionId.split(r'","')[0]
		return zvSessionId
#-------------- Log Out --------------------------------------------------------------------------------
def Logout(SessID):
	# SessID = LV-Session
	url = 'https://api.livevox.com/session/logout/' + SessID
	r = requests.delete(url)
#==============================================================================================================

# Return Codes:
#		Crt201 = Create Contact - connection complete with no errors
#		Crt202 = Create Contact - account already exists
#		Udt204 = Update Contact - request was successful
#		Udt404 = Update Contact - Contact Doesn't Exist
#		Phn204 = Update Phone   - request was successful
#		Phn404 = Update Phone   - Contact Doesn't Exist
#               Nph204 = New    Phone   - request was successful
#               Nph404 = New    Phone   - Contact Doesn't Exist

#----------------------------------- create contact --------------------------------------------------
def CreateContact(data):
	#         data = "acct#"*-*"lv hist id"
	
	zvSessionId = Login()
	
	if zvSessionId != '401':
	
		zvAcc = data.split("*-*")[0]
		zvLvh = data.split("*-*")[1]
	
		#-------------------------------------------------------------------------
		url = 'https://api.livevox.com/contact/contacts/'
		headers = {'content-type': 'application/json', 'LV-Session': zvSessionId}
	
		payload = {
			"createContactDetails":
				{
					"account": zvAcc,
					"active": "true",
					"country": "UNITED_STATES_OF_AMERICA",
					"accountBlock": "NONE",
				}
			}
	
		r = requests.post(url, data=json.dumps(payload), headers=headers)
		print(r,r.text)
	
		#---- set return data & update lv hisory record ----
		zvRtn = str(r.text)
	
		if zvRtn == r'{"code":202,"message":"Contact already exists!"}':
			zvRtn = "Crt202"
		else:
			zvRtn = "Crt201"
	
		UpdateLvHistory(zvLvh + '*-*' + zvRtn)
	
		Logout(zvSessionId)
		
	else:
		UpdateLvHistory(zvLvh + '*-*' + 'Log401')
#------------------------------------------------------------------------------------------------------

#------------------ UpdatePhone Begin ---------------------------------------------------------------
def UpdatePhone(data):
	#       data = "acct#"*-*"phone number"*-*"phone block"*-*"cell consent"*-*"lv hist id"
	
	zvAcc = data.split("*-*")[0]
	zvPhn = data.split("*-*")[1]
	zvBlk = data.split("*-*")[2]
	zvCns = data.split("*-*")[3]
	zvLvh = data.split("*-*")[4]
	
	zvSessionId = Login()
	
	if zvSessionId != '401':
	
		url = 'https://api.livevox.com/contact/contacts/' + zvAcc
		headers = {'content-type': 'application/json', 'LV-Session': zvAddSessionId}
	
		payload = {
			"updateContactDetails":{
				"phone":[{
				"phone": zvPhn,
				"phoneBlock": zvBlk,
				"cellConsent": zvCns,
					}]
				}
			}
	
		r = requests.put(url, data=json.dumps(payload), headers=headers)
		print(r,r.text)
		
		#---- set return data & update lv hisory record ----
		zvRtn = str(r.text)
	
		if zvRtn == "":
			zvRtn = "Phn204"
		else:
			zvRtn = "Phn404"
	
		UpdateLvHistory(zvLvh + '*-*' + zvRtn)
	
		Logout(zvSessionId)
		
	else:
		UpdateLvHistory(zvLvh + '*-*' + 'Log401')
#-----------------------------------------------------------------------------------------------------

#------------------ NewPhone Begin ---------------------------------------------------------------
def NewPhone(data):
	#    data = "acct#"*-*"phone number"*-*"phone rank"*-*"phone block"*-*"cell consent"*-*"lv hist id"
	
	zvAcc = data.split("*-*")[0]
	zvPhn = data.split("*-*")[1]
	zvRnk = data.split("*-*")[2]
	zvBlk = data.split("*-*")[3]
	zvCns = data.split("*-*")[4]
	zvLvh = data.split("*-*")[5]
	
	zvSessionId = Login()
	
	if zvSessionId != '401':
	
		url = 'https://api.livevox.com/contact/contacts/' + zvAcc
		headers = {'content-type': 'application/json', 'LV-Session': zvSessionId}
	
		payload = {
			"updateContactDetails":{
				"phone":[{
				"phone": zvPhn,
				"ordinal": zvRnk,
				"phoneBlock": zvBlk,
				#"cellConsent": zvCns,
					}]
				}
			}		
		r = requests.put(url, data=json.dumps(payload), headers=headers)
		print(r,r.text)
				
		#---- set return data & update lv hisory record ----
		zvRtn = str(r.text)
	
		if zvRtn == "":
			zvRtn = "Nph204"
		else:
			zvRtn = "Nph404"
	
		UpdateLvHistory(zvLvh + '*-*' + zvRtn)
	
		Logout(zvSessionId)
		
	else:
		UpdateLvHistory(zvLvh + '*-*' + 'Log401')
#-----------------------------------------------------------------------------------------------------

#------------------ Update Contact Begin ---------------------------------------------------------------
def UpdateContact(data):
	#         data = "acct#"*-*"field name"*-*"field value"*-*"custom?"*-*"lv hist id"
	
	zvSessionId = Login()
	
	if zvSessionId != '401':
	
		zvAcc = data.split("*-*")[0]
		zvFld = data.split("*-*")[1]
		zvVal = data.split("*-*")[2]
		zvCst = data.split("*-*")[3]
		zvLvh = data.split("*-*")[4]
	
		url = 'https://api.livevox.com/contact/contacts/' + zvAcc
	
		headers = {'content-type': 'application/json', 'LV-Session': zvSessionId}
	
		#--- if person info ---------------------------------------------------
		if (zvFld == 'firstName') or (zvFld == 'lastName') or (zvFld == 'email') or (zvFld == 'dateOfBirth') or (zvFld == 'ssn') or (zvFld == 'zipCode'):
			payload = {
				   "updateContactDetails": {
				   	"person": {
				   		zvFld: zvVal,
				   		}
				   	}
				   }
		#---------------- if custom field -------------------------------
		elif zvCst == 'Y':
			payload = {
				"updateContactDetails":{
					"customFields":[{
		 				"field": zvFld,
		 				"value": zvVal,
		 					}]
	      					}
				}
		#------------- if not custom field --------------------
		else:
			payload = {
				   "updateContactDetails": {
				   	zvFld: zvVal,
				   	}
				   }
		#-----------------------------------------------------------------------
	
		r = requests.put(url, data=json.dumps(payload), headers=headers)
		print(r,r.text)
		
		#---- set return data & update lv hisory record ----
		zvRtn = str(r.text)
	
		if zvRtn == "":
			zvRtn = "Udt204"
		else:
			zvRtn = "Udt404"
		
		UpdateLvHistory(zvLvh + '*-*' + zvRtn)
	
		Logout(zvSessionId)
		
	else:
		UpdateLvHistory(zvLvh + '*-*' + 'Log401')
#-----------------------------------------------------------------------------------------------------

#--------------------------- Update LV History Begin --------------------------------------------------
def UpdateLvHistory(data):
	#           data = "lv hist id"*-*"return code"
	
	zvLvh = data.split('*-*')[0]
	zvRtn = data.split('*-*')[1]
	zvLvSh = r'/mnt/vmware/rm/rmtest/LvApi/Request/LiveVoxReqSh.sh'
	
	if " " in zvLvh:
		zvLvh = zvLvh.replace(" ","_")
	
	if " " in zvRtn:
		zvRtn = zvRtn.replace(" ","_")
	
	print('*** RETURN --> Lvh:',zvLvh,' | Data:',zvRtn)
	
	subprocess.check_call([zvLvSh,zvLvh,zvRtn])
#-----------------------------------------------------------------------------------------------------

#===============================================================================================================
#--------------------------------- RUN FUNCTIONS BEGIN -----------------------------------------------
if zvFunc == "CreateContact":
	CreateContact(zvData)

if zvFunc == "UpdateContact":
	UpdateContact(zvData)

if zvFunc == "UpdatePhone":
	UpdatePhone(zvData)

if zvFunc == "NewPhone":
	NewPhone(zvData)

if (zvFunc == "Help") or (zvFunc == "help") or (zvFunc == "H") or (zvFunc == "h"):
	print(zvHelpInfo)
#--------------------------------- RUN FUNCTIONS END -------------------------------------------------
#-----------------------------------------------------------------------------------------------------
