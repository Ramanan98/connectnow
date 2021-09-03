import requests

url = "http://127.0.0.1:8000/signup/"

#Create users

payload={'username': 'Tim',
'password': 'password',
'birthday': '1998-6-10',
'state': 'Tamil Nadu',
'age_min': '18',
'age_max': '25',
'pref_state': 'Uttarakhand',
'interests': '\'technology\',\'programming\',\'nature\',\'food\',\'books\''}

response = requests.request("POST", url, data=payload)
print(response.text)

payload={'username': 'Ana',
'password': 'password',
'birthday': '1999-6-10',
'state': 'Uttarakhand',
'age_min': '19',
'age_max': '24',
'pref_state': 'Tamil Nadu',
'interests': '\'technology\',\'programming\',\'travel\',\'food\',\'books\''}

response = requests.request("POST", url, data=payload)
print(response.text)

payload={'username': 'Rob',
'password': 'password',
'birthday': '1998-1-6',
'state': 'Karnataka',
'age_min': '19',
'age_max': '23',
'pref_state': 'Karnataka',
'interests': '\'luxury\',\'music\',\'nature\',\'food\',\'books\''}

response = requests.request("POST", url, data=payload)
print(response.text)

payload={'username': 'Rebecca',
'password': 'password',
'birthday': '1999-8-3',
'state': 'Delhi',
'age_min': '18',
'age_max': '23',
'pref_state': 'Delhi',
'interests': '\'cinephile\',\'luxury\',\'music\',\'food\',\'books\''}

response = requests.request("POST", url, data=payload)
print(response.text)

payload={'username': 'Dave',
'password': 'password',
'birthday': '1999-12-12',
'state': 'Kerala',
'age_min': '18',
'age_max': '24',
'pref_state': 'Kerala',
'interests': '\'cinephile\',\'luxury\',\'music\',\'blogging\',\'fashion\''}

response = requests.request("POST", url, data=payload)
print(response.text)

payload={'username': 'Tom',
'password': 'password',
'birthday': '2000-12-12',
'state': 'Uttarakhand',
'age_min': '18',
'age_max': '24',
'pref_state': 'Tamil Nadu',
'interests': '\'technology\',\'programming\',\'nature\',\'food\',\'books\''}

response = requests.request("POST", url, data=payload)
print(response.text)

payload={'username': 'ami',
'password': 'password',
'birthday': '2000-2-23',
'state': 'Karnataka',
'age_min': '18',
'age_max': '25',
'pref_state': 'Karnataka',
'interests': '\'luxury\',\'music\',\'nature\',\'food\',\'books\''}

response = requests.request("POST", url, data=payload)
print(response.text)

payload={'username': 'mat',
'password': 'password',
'birthday': '1999-1-11',
'state': 'Delhi',
'age_min': '18',
'age_max': '25',
'pref_state': 'Delhi',
'interests': '\'cinephile\',\'luxury\',\'music\',\'food\',\'books\''}

response = requests.request("POST", url, data=payload)
print(response.text)