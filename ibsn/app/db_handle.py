import psycopg2
isError=False
cursor="sfg"

try:
    connection = psycopg2.connect(user = "postgres",
                                  password = "jaxtek",
                                  host = "127.0.0.1",
                                  port = "5433",
                                  database = "postgres")
    cursor = connection.cursor()

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
    isError=True

def username_check(username):
    cursor.execute("select count(username) from auth_user where username=%s",(username,))
    count=cursor.fetchone()
    count=f"{count[0]}"
    if count=="0":
        return 1 #Available
    return 0 #Not available

def get_username(user_id):
    try:
        cursor.execute("select username from auth_user where id = %s;",(user_id,))
        req_username = cursor.fetchone()
        return req_username[0]
    except Exception as e:
        print("Error at get_username ",e)
        return 0

def set_online(user_id):
    user_id = str(user_id)
    try:
        cursor.execute("update user_profiles set isOnline=true where user_id=%s;",(user_id,))
        connection.commit()
    except Exception as e:
        print("Error at set_online ",e)

def set_offline(user_id):
    user_id = str(user_id)
    try:
        cursor.execute("update user_profiles set isOnline=false where user_id=%s;",(user_id,))
        connection.commit()
    except Exception as e:
        print("Error at set_offline ",e)


def add_user(username, birthday,state, age_min, age_max, pref_state, interests):
    print(interests,"...",type(interests))
    interests = interests.split(",")
    y = ""
    for x in interests:
        y=y+ "\'" + x +"\',"
    y=y[:-1]
    interests = y
    print(y)
    try:
        cursor.execute("select id from auth_user where username = %s;",(username,))
        req_id = cursor.fetchone()
        cursor.execute("insert into user_profiles(user_id, username, birthday,state,isOnline) values(%s,%s,%s,%s,false);",(req_id[0],username, birthday,state))
        cursor.execute(f'insert into interests values({req_id[0]},ARRAY[{interests}]);')
        cursor.execute(f"insert into user_preferences values({req_id[0]},{age_min},{age_max},'{pref_state}');")
        connection.commit()
    except Exception as e:
        print("Error at add_user ",e)
        return 0

def set_preferences(id, age_min, age_max, pref_state):
    try:
        cursor.execute(f"update user_preferences set age_min = {age_min}, age_max = {age_max}, state = \'{pref_state}\' where user_id = {id};")
        connection.commit()
    except Exception as e:
        print("Error at set_preferences ",e)
        return 0

def set_interests(id, interests):
    global y
    y=str()
    for x in interests:
        y=y+ "\'" + x +"\',"
    y=y[:-1]
    interests = y
    try:
        cursor.execute(f"update interests set tags = ARRAY[{interests}] where user_id = {id};")
        connection.commit()
    except Exception as e:
        print("Error at set_interests ",e)
        return 0

def get_preferences_and_interests(id):

    try:
        cursor.execute(f"select age_min,age_max,state from user_preferences where user_id = {id};")
        preferences = cursor.fetchall()
        cursor.execute(f"select tags from interests where user_id = {id};")
        tags = cursor.fetchall()
        # print(preferences[0],tags[0][0][0])   
        result=""
        for i in preferences[0]:
            result = result + str(i) +","
        for i in tags[0][0]:
            result = result + str(i) +","
        print(result[:-1])
        return result[:-1]
    except Exception as e:
        print("Error at get_preferences_and_interests ",e)
        return 0

def get_profile(id):
    try:
        cursor.execute(f"select username,extract(year from age(current_date,birthday)),state from user_profiles where user_id = {id};")
        profile = cursor.fetchall()
        data = {
        "name":profile[0][0],
        "age":str(profile[0][1]),
        "state":profile[0][2]
        }
        return data
    except Exception as e:
        print("Error at get_profile ",e)
        return 0