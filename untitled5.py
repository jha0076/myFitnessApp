# -*- coding: utf-8 -*-
"""
Created on Tue Jun 15 15:47:47 2021

@author: HI
"""


from flask import Blueprint
from flask import Flask, jsonify, request, make_response,send_from_directory , render_template
import os 
import json
#from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt_claims
from bson import json_util, ObjectId
import jwt
from flask_bcrypt import Bcrypt
from datetime import datetime,timedelta
# from dateutil.relativedelta import relativedelta
from dateutil.relativedelta import *

from .utils import *
from .extensions import mongo
from .decoratorss import token_required,valid_response
from .settings import JWT_SECRET
from .helpers import to_json
import forms
import pymongo

client= pymongo.mongoclient('localhost',27017)

UPLOAD_FOLDER = os.path.join(os.getcwd(),'/static/images') 

####    r"C:\Users\CONCERT\Documents\fitness-backend\fitness\static\images"


@user.route('/okay',methods=['POST'])
def abhishttest():
    req = request.get_json()
    print(request.headers.get_all)
    return jsonify(req)



# file serving 
@user.route('/testserver/<image_name>', methods=['POST','GET'])
def get_file(image_name):
    filename = image_name
    if filename=='':
        return make_response(jsonify({"message":"Invalid file name"}),401)
    print(UPLOAD_FOLDER, filename)
    print('Image')
    #print(send_from_directory(UPLOAD_FOLDER,filename)) C:\Users\CONCERT\Documents\fitness-backend\fitness\static\images
    try:
        return send_from_directory('C:\\Users\\CONCERT\\Documents\\fitness-backend\\fitness\\static\\images', filename=image_name, as_attachment=True)
    except FileNotFoundError:
        return (404)
    

@user.route('/initial_user_setup',methods=['POST']) #Checked
def initial_setup(): #TODO validations 
    req = request.get_json()
    user_collection = mongo.db.users
    user = user_collection.find_one({'email':req['email']})
    if user:
         access_token = jwt.encode({'email': req['email']
                               }, JWT_SECRET)
         return make_response(jsonify({"message":"email already exist","data":to_json(user), "token":access_token.decode("UTF-8")}),200)
    try:
        user_collection.insert({
        'name':req['name'], 
        'email':req['email'],
        'username':req['username'],
        'mobile_number':int(req['mobile_number']),
        'firstsignin':True #bool(req['firstsignin'])
        })
        print("I HAPPEN")
        access_token = jwt.encode({"mobile_number": req["mobile_number"],
                               'email': req['email']
                               }, JWT_SECRET)
        return make_response(jsonify({"message":"user added","token":access_token.decode("UTF-8")}),201)
    except:
        return make_response(jsonify({"message":"check details"}),401)


@user.route('/get_user') 
@token_required
def get_user():
    if request.is_json:
        print("here")
        token = request.headers.get('Authorization')
        if not token:
            return jsonify("Invalid token")
        data = jwt.decode(token, JWT_SECRET)
        print(data['email'])
        # email = request.get_json()['email']
        email = data['email']
        #mobile_number = data['mobile_number']
        # print(data)
        user_collection = mongo.db.users
        user = user_collection.find_one({"email":email})
        if(user):
            return make_response(jsonify({"message":to_json(user)}),200)
        else:
            return make_response(jsonify({"message":"user does not exist"}),200)
    else:
        return make_response(jsonify({"message":"bad request"}),401)

## eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImFiaGlzaHQxQHRlc3QuY29tIn0.VndDRGjuz9maw67pR8nNii0U1LOgaN4z69A_8qwGPX8

@user.route('/subscribe',methods=["POST"])
@token_required
@valid_response
def subscribe():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify("Invalid token")
    data = jwt.decode(token,JWT_SECRET)
    req = request.get_json()
    user_collection = mongo.db.users
    user = user_collection.find_one({'email':data['email']})
    tier = req['tier']
    subscription_type = req['subscription_type']
    period = req['period']

    start_date=datetime.datetime.now()


    end_date = start_date+relativedelta(months=+period)#timedelta(days=period*30)


    calculate_amount = get_amount(tier,subscription_type,period)

    if(calculate_amount == -1): return make_response(jsonify({"message":"Invalid"}),403)

    print(start_date)
    print(end_date)
    try:
        subscription = {
            'tier':tier,
            'type':subscription_type,
            'period':period,
            'start_date':start_date,
            'end_date':end_date,
            'amount':calculate_amount,
            'payment_status':"pending",
            'validity':False 
        }
        user['subscription']=subscription
        user_collection.save(user)
        return make_response(jsonify( {"message":"success, details saved"}),201)
    except:
        return make_response(jsonify({"message":"error"}),200)

 
#     # start_date = req['start_date']

###paid 

@user.route('/paid',methods=["POST"])
@token_required
@valid_response
def paid():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify("Invalid token")
    data = jwt.decode(token,JWT_SECRET)
    req = request.get_json()
    user_collection = mongo.db.users
    user = user_collection.find_one({'email':data['email']})
    try:
        user['subscription']['payment_status'] = req['payment_status']
        user['subscription']['validity'] = req['validity']
        user_collection.save(user)
        return make_response(jsonify( {"message":"success, details saved"}),201)
    except:
        return make_response(jsonify({"message":"error"}),200)

##Check validity 



###change_subscription

@user.route('/update_subscription',methods=["POST"])
@token_required
@valid_response
def update_subscription():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify("Invalid token")
    data = jwt.decode(token,JWT_SECRET)
    req = request.get_json()
    user_collection = mongo.db.users
    user = user_collection.find_one({'email':data['email']})

    try:
        for key,value in req.items():
            if(key=='period'):
                # assert(user['subscription']['period']>key)

                # if not req['subscription_type']:
                amount = get_amount(user['subscription']['tier'],user['subscription']['type'],req['period']-user['subscription']['period'])
                # else:
                

                #     amount = get_amount(req['subscription_type'],req['period']-user['subscription']['period']) 
                end_date = user['subscription']['end_date'] + relativedelta(months=+(req['period']-user['subscription']['period']))#timedelta(days=(req['period']-user['subscription']['period'])*30)
                user['subscription']['amount']=amount
                user['subscription']['end_date']=end_date
                print(end_date)

            elif(key=='amount' or key=='payment_status'): continue
            user['subscription'][key]=value
        user_collection.save(user)
        return make_response(jsonify( {"message":"success, details saved"}),201)
    except:
        return make_response(jsonify({"message":"error"}),200)






@user.route('/editProfile',methods=["POST"])  #Checked
@token_required
def editdetails(): 
    token = request.headers.get('Authorization')
    if not token:
        return jsonify("Invalid token")
    data = jwt.decode(token, JWT_SECRET)
    print(request.get_json())
    if request.is_json:
        req = request.get_json()
        user_collection = mongo.db.users
        user = user_collection.find_one({'email':data['email']})
        try:
            for key,value in req.items():
                if key == 'email':
                    continue
                user[key]=value
                
                print(key,value)
            print("Hello")
            user_collection.save(user)
            return make_response(jsonify({"message":"Updated the info"}),202)
        except:
            return make_response(jsonify({"message":"Something is wrong, could not update"}),200)
    else:
        return make_response(jsonify({"message":"bad request"}),400)




@user.route('/get_goal_projections') # TODO @token_required  
def goal_projections():
    if request.is_json:
        req = request.get_json()
        height = float(req['height'])
        weight = float(req['weight'])
        gender=req["gender"]    #FIXME form validations
        dob = req["dob"].split('-')
        username = req['username']
        goal_weight = float(req["desired_goal_weight"])
        age = calc_age(dob)
        BMI = round(bmi_calculation(height, weight), 2)
        BMR = round(bmr_calculation(height, weight, int(age),gender))

        TDEE= tee_dee_calculation(BMR,req["current_fitness_level"])
        TDEE=round(TDEE,2)

        diet = get_diet(weight,goal_weight,TDEE)
        diet=list(diet)
        for i in range(3):
            diet[i]=diet[i]//1


        user_collection = mongo.db.users
        user = user_collection.find_one({"username":username})

        start=""
        end=""
        
        if(user): #FIXME user['startdate']
            start=user["startdate"]
            start=str(start).split("-")
            start=datetime.date(int(start[0]),int(start[1]),int(start[2][:2]))
            if(user["goal_period"]==req["goal_period"]):
                end=user["enddate"]
                end=str(end).split("-")
                end=datetime.date(int(end[0]),int(end[1]),int(end[2][:2]))
            else:            
                end=start+relativedelta(months=+int(req["goal_period"]))
        else:
            start=datetime.datetime.today()
            end=start+ relativedelta(months=+int(req["goal_period"]))

        weeks = (end-start).days//7

        dates=[]

        cur_wt=weight
        des_wt=float(req["desired_goal_weight"])
        for i in range(weeks+2):
            dates.append(str(start+relativedelta(days=+7*i)))
        avg_wt=(cur_wt-des_wt)/weeks
        change_wt=[]
        bmi_change = []
        
        for i in range(weeks+1):
            change_wt.append(round(cur_wt-(avg_wt*i),2)) 
            bmi_change.append(bmi_calculation(height,change_wt[i]))
        
        print(change_wt)
        print(bmi_change)
        return make_response(jsonify(to_json({
            "message":"succes",
            "data":{
                "change_wt":change_wt,"average_Weight":avg_wt,"dates":dates,"diet":diet,
                "TDEE":TDEE,"BMI":BMI,"BMR":BMR,"age":age,"bmi_change":bmi_change
                }
        })))
    else:
        return make_response(jsonify({"message":"bad request"}),400)


# Edit Profile
@user.route("/profile/editprofile", methods=["POST"]) #TODO @token_required
def editprofile():
    token = request.form["Authorization"]
    data = jwt.decode(token, JWT_SECRET)
    username = data["username"]
    col = mongo.db.users # dbo.users
    inp = {} #FIXME
    height = float(inp["height"])
    weight = float(inp["weight"])

    BMI = round(bmi_calculation(height, weight), 2)
    dob = inp["dob"].split('-')
    dob = datetime.date(int(dob[0]), int(dob[1]), int(dob[2]))
    today = datetime.date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    gender='m' if inp["gender"][0] == "M" else "f"
    BMR = round(bmr_calculation(height, weight, int(age),'m' if inp["gender"][0] == "m" else "f"))

    TDEE= tee_dee_calculation(BMR,inp["current_fitness_level"])
    TDEE=round(TDEE,2)

    ideal_weight=(ideal_weight_calculation_devine(height,gender)+ideal_weight_calculation_hamwi(height,gender)+ideal_weight_calculation_miller(height,gender)+ideal_weight_calculation_robinson(height,gender))/4
    ideal_weight=round(ideal_weight,2)

    if(weight-float(inp["desired_goal_weight"])>1):
        diet=macronutrient_calculation_cutting_moderate(TDEE)
    elif(weight-float(inp["desired_goal_weight"])<1):
        diet=macronutrient_calculation_bulking_moderate(TDEE)
    else:
        diet=macronutrient_calculation_maintain_moderate(TDEE)
    diet=list(diet)
    for i in range(3):
        diet[i]=diet[i]//1
    


    start=""
    end=""
    doc = col.find_one({"username": username})
    if(doc.get("startdate")):
        start=(doc["startdate"])
        start=str(start).split("-")
        start=datetime.date(int(start[0]),int(start[1]),int(start[2][:2]))
        if(doc["goal_period"]==inp["goal_period"]):
            end=(doc["enddate"])
            end=str(end).split("-")
            end=datetime.date(int(end[0]),int(end[1]),int(end[2][:2]))
        else:
            
            end=start+ relativedelta(months=+int(inp["goal_period"]))
    else:
        start=datetime.datetime.today()
        end=start+ relativedelta(months=+int(inp["goal_period"]))

    weeks = (end-start).days//7
    dates=[]
    cur_wt=float(inp["weight"])
    des_wt=float(inp["desired_goal_weight"])
    for i in range(weeks+2):
        dates.append(str(start+relativedelta(days=+7*i)))
    avg_wt=(cur_wt-des_wt)/weeks
    change_wt=[]
    for i in range(weeks+1):
        change_wt.append(list([round(cur_wt-(avg_wt*i),2),0,0,0])) 
    
    doc = col.find_one({"username": username})
    if(doc):
        col.update_one({"username": username},
                       {"$set":
                        {
                            "username": inp["username"], "email": inp["email"], "phone": inp["phone"], "dob": inp["dob"],
                            "height": float(inp["height"]), "age": age, "gender": inp["gender"], "weight": float(inp["weight"]),
                            "BMI": BMI, "BMR": BMR, "TDEE":TDEE, "diet":diet, "ideal_weight":ideal_weight,
                            "current_fitness_level": inp["current_fitness_level"], "diet_preference":inp["diet_preference"],
                            "desired_goal_weight": float(inp["desired_goal_weight"]), "goal_period":float(inp["goal_period"]),
                            "change_wt":change_wt, "dates":dates, 
                        }
                        }
                       )

    else:
        col.insert_one({
            "username": inp["username"], "email": inp["email"], "phone": inp["phone"], "dob": inp["dob"], "height": float(inp["height"]),
            "gender": inp["gender"], "BMI": BMI, "BMR": BMR, "TDEE":TDEE, "diet":diet, "ideal_weight":ideal_weight, "age": age,
            "weight": float(inp["weight"]), "current_fitness_level": inp["current_fitness_level"], "diet_preference":inp["diet_preference"],
            "desired_goal_weight": float(inp["desired_goal_weight"]), "goal_period":float(inp["goal_period"]),
            "change_wt":change_wt, "dates":dates,
        })
    # print(request.form["height"])
    access_token = jwt.encode({"username": inp["username"],
                               'email': inp['email']
                               }, JWT_SECRET)
    # print(access_token.decode("UTF-8"))
    return ({"res": "success", "token": access_token.decode("UTF-8")})


@user.route('/usermode',methods=["POST"])
@token_required
@valid_response
def changemode():
    token = request.headers.get('Authorization')
    print(token)
    tokendata = jwt.decode(token,JWT_SECRET)
    user_collection = mongo.db.users 
    req = request.get_json()
    user = user_collection.find_one({"email":tokendata['email']})
    if(user):
        try:
            user['user_mode']=req['user_mode']
            user_collection.save(user)
        except:
            return make_response(jsonify({"message":"Could not change the status of the user"}),401)
    else:
        return make_response(jsonify({"message":"Not found"}),404)
    return make_response(jsonify({"message":"user mode changed"}),202)



@user.route("/profileinfo",methods=["POST"])
@token_required
def profileinfo():
    token = request.form["Authorization"]
    username=jwt.decode(token, JWT_SECRET)["username"]
    col=mongo.db.users           #dbo.users
    doc=col.find_one({"username":username})
    if(doc):
        doc=json.loads(json_util.dumps(doc))
        start=doc["dates"][0]
        start=str(start).split("-")
        start=datetime.date(int(start[0]),int(start[1]),int(start[2][:2]))
        print(start,"date")
        today=datetime.date.today()
        current_week=(today-start).days//7
        print(current_week,"week_no")
        
        return ({"res":"success","data":doc,"week_no":current_week})
    return ({"res":"Cannot find details"})

@user.route("/profile/goal", methods=["POST"])
@token_required
def goal():
    token = request.form["Authorization"]
    inp = request.form
    data = jwt.decode(token, JWT_SECRET)
    username = data["username"]
    col = mongo.db.goals #dbo.goals
    doc = col.find_one({"username": username})
    if(doc):
        col.update({"username": username},
                   {"$set" : {"fat": float(inp["fat"]),
                     "muscle_mass": float(inp["muscle_mass"]), "resting_heart_rate": float(inp["resting_heart_rate"]),
                     "recovery_heart_rate": float(inp["recovery_heart_rate"]), "current_health_condition": list(str(inp["current_health_condition"]).split(",")),
                     "desired_fat":float(inp["desired_fat"]), "desired_muscle_mass":float(inp["desired_muscle_mass"]),
                      "fitness_type":inp["fitness_type"], "carb_level":inp["carb_level"],
                     }
                    }
                   )

    else:
        col.insert_one({
            "username": username, "fat": float(inp["fat"]), "muscle_mass": float(inp["muscle_mass"]), 
            "resting_heart_rate": float(inp["resting_heart_rate"]), "recovery_heart_rate": float(inp["recovery_heart_rate"]),
            "current_health_condition": inp["current_health_condition"], "desired_fat":float(inp["desired_fat"]),
            "desired_muscle_mass":float(inp["desired_muscle_mass"]), "fitness_type":inp["fitness_type"], 
            "carb_level":inp["carb_level"],
        })
    # print(request.form["fat"])
    return ({"res": "success"})



@user.route("/weeklygoal",methods=["POST"])
@token_required
def weeklygoal():
    token = request.form["Authorization"]
    inp = request.form
    data = jwt.decode(token, JWT_SECRET)
    username = data["username"]
    col=mongo.db.users #dbo.users
    doc=col.find_one({"username":username})
    if(doc):
        doc=json.loads(json_util.dumps(doc))
        change_wt=doc["change_wt"]
        start=doc["dates"][0]
        start=str(start).split("-")
        start=datetime.date(int(start[0]),int(start[1]),int(start[2][:2]))
        today=datetime.date.today()
        current_week=(today-start).days//7
        change_wt[current_week][1]=float(inp["weight"])
        change_wt[current_week][2]=float(inp["musclemass"])
        change_wt[current_week][3]=float(inp["fat"])
        print(change_wt[current_week],inp["weight"])
        col.update_one({"username":username},
        {
            "$set": { "change_wt":change_wt }
         })
        doc=col.find_one({"username":username})
        doc=json.loads(json_util.dumps(doc))
        return({"res":"success","data":doc})
    else:
        return({"res":"Didnot update now"})

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
