# -*- coding: utf-8 -*-
"""
Created on Tue Jun 15 17:12:08 2021

@author: HI
"""



#calender screen
 
@token_required
def calender():
    if request.is_json:
        print("here")
        token = request.headers.get('Authorization')
        if not token:
            return jsonify("Invalid token")
        data = jwt.decode(token, JWT_SECRET)
        print(data['date'])
        # email = request.get_json()['email']
        date = data['date']
        
        #mobile_number = data['mobile_number']
        # print(data)
        date_collection = mongo.db.log
        user = date_collection.find_one({"date":date})
        if(user):
             workouts = date_collection.find_one({"workouts":workouts})
             diet = date_collection.find_one({"diet":diet})
             return workouts
             return diet
            #return make_response(jsonify({"message":to_json(user)}),200)
        else:
            return make_response(jsonify({"message":"user does not exist"}),200)
    else:
        return make_response(jsonify({"message":"bad request"}),401)
        

@user.route("/dietplan",methods=["POST"])
@token_required
def dietplan():
    token = request.form["Authorization"]
    inp = request.form
    data = jwt.decode(token, JWT_SECRET)
    mealplan = data["mealplan"]
    col=mongo.db.test1
    meal=col.find_one({"mealplan":mealplan,"calories":calories,"time":time,"mealdetails":mealdetails})
    if(meal):
            print(meal)
            return make_response(jsonify({"message":to_json(meal)}),200)
    else:
            return make_response(jsonify({"message":"meal chart does not exist"}),200)
#new meal addition form by the user
@user.route("/dietplan",methods=["POST"])
def addmeal():
    db=client.meal_user_added
    print(request.form)
    meal={"Date":request.form.get("date"),
           "Meal type":request.form.get("Meal type"),
           "Meal name":request.form.get("Meal name"),
           "Total servings":request.form.get("Total servings"),
           "Calories":request.form.get("Calories"),
           "Total nutrients":request.form.get("Total nutrients")
         } 

    if db.users.find_one({"Meal type": meal['Meal type']}):
        return jsonify({"error":"Meal type already exists"}),400


    #adding to meal record to the database
    if db.users.insert_one(meal):
        return jsonify(meal),200
    return jsonify({"error":"Adding meal failed"}),400
@user.route("/activity",methods=["POST"])                 
def activity():
    if request.is_json:
        print("here")
        token = request.headers.get('Authorization')
        if not token:
            return jsonify("Invalid token")
        data = jwt.decode(token, JWT_SECRET)
        print(data['date'])
        # email = request.get_json()['email']
        date = data['date']
        # print(data)
        date_collection = mongo.db.activityWorkout
        user = date_collection.find_one({"date":date})
        if(user):
             activites = date_collection.find_one({"activity":activity})
             
             return activites
             
            #return make_response(jsonify({"message":to_json(user)}),200)
        else:
            return make_response(jsonify({"message":"user does not exist"}),200)
    else:
        return make_response(jsonify({"message":"bad request"}),401)
@user.route("/workout",methods=["POST"])                 
def workout():
    if request.is_json:
        print("here")
        token = request.headers.get('Authorization')
        if not token:
            return jsonify("Invalid token")
        data = jwt.decode(token, JWT_SECRET)
        print(data['date'])
        # email = request.get_json()['email']
        date = data['date']
        # print(data)
        date_collection = mongo.db.activityWorkout
        user = date_collection.find_one({"date":date})
        if(user):
             workouts = date_collection.find_one({"workouts":workouts})
             
             return workouts
             
            #return make_response(jsonify({"message":to_json(user)}),200)
        else:
            return make_response(jsonify({"message":"user does not exist"}),200)
    else:
        return make_response(jsonify({"message":"bad request"}),401)
       

#insights screen
#@token_required
#@valid_response
#def insights():
#    token = request.headers.get('Authorization')
#    print(token)
#    tokendata = jwt.decode(token,JWT_SECRET)
#    user_collection = mongo.db.users 
#    req = request.get_json()
#    user = user_collection.find_one({"email":tokendata['email']})
#    if(user):
#        try:
#            user['user_mode']=req['user_mode']
#           user_collection.save(user)
#        except:
#           return make_response(jsonify({"message":"Could not change the status of the user"}),401)
#   else:
#       return make_response(jsonify({"message":"Not found"}),404)
#   return make_response(jsonify({"message":"user mode changed"}),202)
