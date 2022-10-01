import requests
import json
import pandas as pd
import numpy as np
import asyncio
from aiohttp import ClientSession

from datetime import datetime
from datetime import timezone
import openpyxl



df=pd.DataFrame()
#dataframe to work with. 


def filter(srcd):
	if (",") in srcd:
		sc=srcd.split(",")
	else:
		sc=srcd.split(" ")
	try:
		while True:
			sc.remove("")
	except: pass
	return sc

sc=input("""Enter Source station codes
plz seperate them by either , or space ;) :-  """)
dc=input("""Enter Destination station codes ^_° :-  """)
doj=input(""" Enter expected dates to travel in the format 'dd-mm-yyyy' and use seprators as above ->> """)
sc=filter(sc)
dc=filter(dc)
doj=filter(doj)
#testdata
#sc=["delhi","ambala","chandigarh","karnal"]
#dc=["mumbai","pune","chennai","banglore"]
#doj=["27-10-2022","28-10-2022"]
def get_codes(name):
	uri=("https://ground-auto-suggest.makemytrip.com/rails/autosuggest/stations?search_query="+name+"&limit=10&version=v1&input_language=en&rails-lang-code=en")
	heads={"Host":"ground-auto-suggest.makemytrip.com" , "rails-lang-code":"en" , "profile-type":"null" , "user-agent":"Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36" , "uuid":"null" , "os":"web" , "mmt-os":"web" , "accept":"*/*" , "sec-gpc":"1" , "accept-language":"en-US,en;q=0.9" , "origin":"https://www.makemytrip.com" , "sec-fetch-site":"same-site" , "sec-fetch-mode":"cors" , "sec-fetch-dest":"empty" , "referer":"https://www.makemytrip.com/" , "accept-encoding":"gzip, deflate, br" }
	try:
		r=requests.get(uri,headers=heads)
		sed=json.loads(r.text)
		sedx=sed["data"]["r"]
		sedy=sedx[0]["irctc_code"]
		return sedy
	except:
		return None
	
src_codes=[]
dest_codes=[]
for i in sc:
	why=get_codes(i)
	if why != None:
		src_codes.append(why)
	else: pass
	
for i in dc:
	bulli=get_codes(i)
	if bulli != None:
		dest_codes.append(bulli)
	else: pass

print(src_codes,dest_codes,sep="\n")



async def test_new(a , session: ClientSession):
	global df
	a=list(a)
	omfoo =[]
	doj=str(a[0])
	dest=str(a[1])
	src=str(a[2])
	uri="https://securedapi.confirmtkt.com/api/platform/trainbooking/tatwnstns?fromStnCode="+src+"&destStnCode="+dest+"&doj="+doj+"&token=&quota=GN&appVersion=290&androidid=mweb_android"
	r=await session.request(method="GET",url=uri)
	r.raise_for_status()
	g=await r.text()
	sed=json.loads(g)
	try:
		for i in sed["trainBtwnStnsList"]:
			for j in (i["avaiblitycache"]).values():
				if j["Prediction"] == "Available":
					uwu="True"
				else: 
					uwu="False"
				if "Date" in j:
					date=j["Date"]
					d=datetime.fromisoformat(date).astimezone(timezone.utc)
					date=d.strftime('%d-%m-%Y')
				else: 
					date='00-00-0000'
				bulli={"TrainNumber":i["trainNumber"],"Distance":i["distance"],"TrainName":i["trainName"],"Duration":i["duration"],"Pantry":i["HasPantry"],"From":i["fromStnCode"],"Starts At":i["departureTime"],"To":i["toStnCode"],"Arrives At":i["arrivalTime"],"TravelClass":j["TravelClass"],"Quota":j["Quota"],"Seat Info":j["Availability"],"Prediction":j["Prediction"],"Date":date,"Fare(1P)":j["Fare"],"Available":uwu}
				omfoo.append(bulli)
				
		dfx=pd.DataFrame(data=omfoo)
		#df=df.append(dfx,ignore_index=True)
		return dfx
	except: 
		return None
			
	

async def uew(i,session:ClientSession):
	global df 
	data =await(test_new(i,session))
	if type(data) ==None: pass
	else:
		df=df.append(data,ignore_index=True)
		

s1=np.array(src_codes)
s2=np.array(dest_codes)
s3=np.array(doj)
l1=np.array(np.meshgrid(s3,s2,s1)).T.reshape(-1,3)



async def main(y:set ):
	async with ClientSession() as session:
		tasks=[]
		for i in y:
			tasks.append(uew(i,session))
		await asyncio.gather(*tasks)




asyncio.run(main(l1))


df=df.sort_values(by="Available",ascending=False,kind="mergesort")

print(df,df.shape,df[["From","To"]],sep="\n")

df.to_excel("output.xlsx", sheet_name='Sheet_name_1')
