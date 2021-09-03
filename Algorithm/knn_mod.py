from nltk.stem import SnowballStemmer
import psycopg2
import redis
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

r = redis.Redis(host=u'localhost', port=6379)

#User requesting matches is in group 1. Users passed from the filter function are in group 2
#Only one user in group 1, others in group 2
example_input = {
    "group1": [
        {
          "user_id": "",
          "interests": [   
          ]
      }
    ],
    "group2": [
        {
          "user_id": "",
          "interests": [
          ]
        },
        {
          "user_id": "",
          "interests": [
          ]
        },
    ]
}

def scoring_function(person1, person2):
    # returns a score that gives the similarity between 2 people
    # scoring function:
    #   +add for each interest * weight
    ss = SnowballStemmer("english")
    score = 0.0

    interest_list1 = person1["interests"]
    interest_list2 = person2["interests"]

    # compare similar interests
    for interest1 in interest_list1:
        for interest2 in interest_list2:
            stem1 = ss.stem(interest1.lower())
            stem2 = ss.stem(interest2.lower())

            #Increase the score for every interest that matches
            if stem1 == stem2:
                score += 1

    return score

# Locate the most similar neighbors

def get_neighbors(users_list, user, num_neighbors):
    distances = list()

    #Calculate the similarity between every user in group 2 with the current user and add them to a list
    for user_d in example_input["group2"]:
        dist = scoring_function(user, user_d)
        distances.append((user_d, dist))
    
    #Sort the distances list in reverse order, since similarity should be maximum
    distances.sort(key=lambda tup: tup[1], reverse=True)

    #Return the list of users in order of decreasing similarity
    neighbors = list()
    for i in range(num_neighbors):
        neighbors.append(distances[i][0])
    return neighbors


def get_a_match(given_id):
    result = list()

    #Put the requesting user's user_id and interests in group 1
    example_input["group1"][0]["user_id"] = given_id
    cursor.execute(f'select tags from interests where user_id = {given_id};')
    try:
        requesting_users_interests = cursor.fetchall()[0][0]
    except Exception as e:
        print(f"User {given_id} not found :{e}")
        return None
    example_input["group1"][0]["interests"] = requesting_users_interests
    #Call filter postgres function to get the users that match the requesting user's preferences
    i = 0
    query = f'select get_matching_users({given_id});'
    cursor.execute(query)
    #Store them in a list. If nobody is matched in filtering, return None
    filters = cursor.fetchall()
    if not filters:
        # print("No match")
        return None
    
    #Put every filtered user's id in group 2
    for x in filters:
        #if r.sismember('online',x[0]):      #Check if they're online by checking redis set. Comment this line while testing
            example_input["group2"][i]["user_id"] = x[0]
            i += 1

    #Put every filtered user's interests in group 2
    i = 0
    for filter in filters:
        cursor.execute(f'select tags from interests where user_id = {filter[0]};')
        filter_interests = cursor.fetchall()
        example_input["group2"][i]["interests"] = filter_interests[0][0]
        i += 1

    #Add all the matched users' ids to the result
    for person in example_input["group1"]:
        neighbors = get_neighbors(example_input, person, 1)     #Get one matched user (highest similarity)
        match = neighbors[0].get('user_id')
        print(f"returning match for {given_id}-->:{match}")
        return match