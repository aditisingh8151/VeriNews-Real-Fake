import os
from flask import Flask, render_template, request, redirect, session, jsonify
from pymongo import MongoClient
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import timedelta
from datetime import datetime
import razorpay
from google import genai
LAST_AI_RESULT = {}   #  (imports ke niche)

app = Flask(__name__)
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

app.secret_key = os.environ.get("VERINEWS_SECRET_KEY", "your_secret_key")
app.permanent_session_lifetime = timedelta(days=7)

client = MongoClient("mongodb://localhost:27017/")
db = client["verinews"]
user_collection = db["user"]
notification_collection = db["notifications"]
ai_cache_collection = db["ai_news_cache"]
ai_limit_collection = db["ai_daily_limit"]
check_news_collection = db["check_news"]



razorpay_client=razorpay.Client(auth=(
    "rzp_test_YOUR_KEY_ID",
    "YOUR_KEY_SECRET"
))

# ================= NEWS DATA =================
NEWS = {

    


    "pahalgam": {
        "category": "security",
        "title": "Pahalgam terror attack kills tourists",
        "date": "12 January 2026 | 10:30 AM IST",
        "image": "pahalgamterr.png",
        "content": [
            "A terror attack struck the Pahalgam region of Jammu and Kashmir killing several tourists.",
            "Security forces sealed the area and launched a massive search operation.",
            "Authorities confirmed the situation is under control and investigations are ongoing."
        ],
        "link":"https://www.google.com/search?q=Pahalgam+terror+attack+news",
        "is_premium": True
    },

    "mahakumbh": {
        "category": "religion",
        "title": "Prayag Maha Kumbh draws millions",
        "date": "14 January 2026 | 06:00 AM IST",
        "image": "kumbhreligious.png",
        "content": [
            "Millions of devotees gathered at Prayagraj for the Maha Kumbh festival.",
            "Strict security and medical arrangements were made by local authorities.",
            "The event marks one of the world's largest religious gatherings."
        ],
        "link":"https://www.google.com/search?q=Prayag+Maha+Kumbh+news",
        "is_premium": True
    },

    "flightcrash": {
    "category": "accident",
    "title": "Air India flight crashes shortly after takeoff",
    "date": "16 January 2026 | 09:15 AM IST",
    "image": "flightcrash.png",
    "content": [
        "An Air India passenger aircraft crashed shortly after taking off from a domestic airport on Friday morning.",
        "According to preliminary reports, the aircraft encountered a technical malfunction moments after takeoff.",
        "Emergency services were immediately deployed to the crash site and rescue operations were carried out.",
        "Officials confirmed that an investigation has been launched by aviation authorities to determine the exact cause of the crash."
    ],
    "status": "VERIFIED",
    "link":"https://www.google.com/search?q=Air+India+flight+crash+news",
    

},

"fakearmy": {
    "category": "other",
    "title": "Compulsory army training for all citizens",
    "date": "19 January 2026 | 09:00 AM IST",
    "image": "fake2.png",
    "content": [
        "A viral social media message claimed that the government has made army training mandatory for all citizens above 18 years.",
        "The message spread rapidly across WhatsApp and Telegram without citing any official notification.",
        "No confirmation was found on government portals or official press releases.",
        "Authorities clarified that the claim is false and urged citizens not to forward unverified messages."
    ],
    "status": "FAKE",
    "link":"https://www.google.com/search?q=Government+announces+compulsory+army+training+for+all+citizens+news"
},
"flightjet": {
    "category": "security",
    "title": "IAF fighter jet crashes during routine training sortie",
    "date": "17 January 2026 | 09:40 AM IST",
    "image": "fighterjet.png",
    "content": [
        "An Indian Air Force fighter jet crashed during a routine training sortie in central India on Friday morning.",
        "According to defence officials, the pilot successfully ejected before the aircraft went down.",
        "Emergency response teams were immediately rushed to the crash site and the area was secured.",
        "The Indian Air Force has ordered a court of inquiry to determine the exact cause of the accident."
    ],
    "status": "VERIFIED",
    "link":"https://www.google.com/search?q=IAF+fighter+jet+crash+news",
        "is_premium": True

},
"politicalrally": {
    "category": "politics",
    "title": "Massive political rally held ahead of upcoming elections",
    "date": "16 January 2026 | 04:30 PM IST",
    "image": "polotics1.png",
    "content": [
        "A major political rally was held in the national capital ahead of the upcoming state elections.",
        "Thousands of supporters gathered as senior leaders addressed key issues including employment and inflation.",
        "Security arrangements were tightened to ensure peaceful conduct of the event.",
        "Political analysts believe the rally could significantly influence voter sentiment."
    ],
    "status": "VERIFIED",
    "link":"https://www.google.com/search?q=Massive+political+rally+held+ahead+of+upcoming+elections+news"
},
"isro": {
    "category": "science",
    "title": "ISRO successfully tests system for GANGAYAAN Mission ,Strengthening Indias's Space Exploration Capabilities",
    "date": "18 January 2026 | 08:30 AM IST",
    "image": "isro.png",
    "content": [
        "ISRO successfully tested the crew escape system for the Gaganyaan mission.",
        "The test ensures astronaut safety during launch emergencies.",
        "Scientists termed the test a major milestone.",
        "Gaganyaan is expected to launch in the coming years."
    ],
    "status": "VERIFIED",
    "link":"https://www.google.com/search?q=ISRO+successfully+tests+crew+escape+system+for+Gaganyaan+mission+news",
    "is_premium": True,
    "is_featured": True
},
"kumbhaccident": {
    "category": "accident",
    "title": "During Kumbh Mela,several devotees dead",
    "date": "15 January 2026 | 06:20 AM IST",
    "image": "kumbhacci.png",
    "content": [
        "A tragic stampede occurred during the early morning hours at the Kumbh Mela in Prayagraj.",
        "Several devotees lost their lives while many others sustained injuries amid heavy crowd movement.",
        "Local authorities stated that overcrowding near the bathing ghats led to panic among pilgrims.",
        "An official investigation has been launched and compensation was announced for the victims' families."
    ],
    "status": "VERIFIED",
    "link":"https://www.google.com/search?q=Kumbh+Mela+stampede+news"
},

    "fakeeconomy": {
    "category": "other",
    "title": "India to stop using paper currency from next month",
    "date": "20 January 2026 | 07:45 PM IST",
    "image": "fake1.png",
    "content": [
        "Several social media posts falsely claimed that India will completely stop paper currency from next month.",
        "The rumour suggested that all transactions would shift to digital payments only.",
        "The Reserve Bank of India denied these claims and confirmed that no such decision has been taken.",
        "Experts warned that such misinformation can create unnecessary panic among citizens."
    ],
    "status": "FAKE"
},

    "redfort": {
        "category": "politics",
        "title": "Delhi Red Fort blast investigation continues",
        "date": "15 January 2026 | 02:00 PM IST",
        "image": "redfort.png",
        "content": [
            "Investigation continues after a blast incident near Delhi's Red Fort.",
            "Security agencies are examining CCTV footage and forensic evidence.",
            "Officials stated there is no immediate threat to the public."
        ],
        "link":"https://www.google.com/search?q=Delhi+Red+Fort+blast+news",
            "is_premium": True
    },

    

    "economy": {
        "category": "other",
        "title": "India's economy shows strong growth",
        "date": "19 January 2026 | 08:00 AM IST",
        "image": "economy.png",
        "content": [
            "India's economy recorded strong quarterly growth according to official data.",
            "Experts attribute the rise to industrial output and exports.",
            "Market confidence remains high amid global uncertainty."
        ],
        "link":"https://www.google.com/search?q=India's+economy+shows+strong+growth+news"
    },
   

# ================= EXTRA NEWS =================

"airindia": {
    "category": "accident",
    "title": "Air India flight makes emergency landing",
    "date": "21 January 2026 | 11:20 AM IST",
    "image": "airindia.png",
    "content": [
        "An Air India flight made an emergency landing after a technical fault was detected mid-air.",
        "The pilot alerted air traffic control and followed emergency safety procedures.",
        "All passengers were evacuated safely and no injuries were reported.",
        "Air India confirmed that a detailed technical inspection has been initiated."
    ],
    "status": "VERIFIED",
    "link":"https://www.google.com/search?q=Air+India+flight+emergency+landing+news",
        "is_premium": True
},

"supremecourt": {
    "category": "law",
    "title": "New digital security and surveillance laws",
    "date": "20 January 2026 | 12:00 PM IST",
    "image": "supreme.png",
    "content": [
        "The Supreme Court reviewed newly proposed digital security and surveillance laws.",
        "Petitions raised concerns over privacy and misuse of surveillance powers.",
        "The court sought clarification from the central government.",
        "Final hearings are expected next month."
    ],
    "status": "VERIFIED",
    "link":"https://www.google.com/search?q=Supreme+Court+reviews+new+digital+security+and+surveillance+laws+news"
},

"railways": {
    "category": "security",
    "title": "Indian Railways introduces AI-based system",
    "date": "19 January 2026 | 09:00 AM IST",
    "image": "railway.png",
    "content": [
        "Indian Railways launched an AI-based safety monitoring system across major routes.",
        "The system will detect track faults and signal failures in real time.",
        "Officials say this will significantly reduce accidents.",
        "The project will be expanded nationwide."
    ],
    "status": "VERIFIED",
    "link":"https://www.google.com/search?q=Indian+Railways+introduces+AI-based+safety+monitoring+system+news",
        "is_premium": True

},



"cbse": {
    "category": "education",
    "title": "CBSE announces revised exam pattern for Class 10 and 12",
    "date": "22 January 2026 | 10:00 AM IST",
    "image": "cbse.png",
    "content": [
        "CBSE announced a revised exam pattern for Classes 10 and 12.",
        "The focus will be on conceptual understanding rather than rote learning.",
        "New sample papers will be released soon.",
        "Schools have been advised to inform students accordingly."
    ],
    "status": "VERIFIED",
    "link":"https://www.google.com/search?q=CBSE+announces+revised+exam+pattern+for+Class+10+and+12+news"
},

"ugc": {
    "category": "education",
    "title": "UGC releases new guidelines",
    "date": "23 January 2026 | 01:00 PM IST",
    "image": "ugc.png",
    "content": [
        "UGC released new guidelines for online and hybrid degree programs.",
        "Universities can now offer flexible learning models.",
        "Quality checks and accreditation rules have been strengthened.",
        "Students welcomed the move."
    ],
    "status": "VERIFIED",
    "link":"https://www.google.com/search?q=UGC+releases+new+guidelines+for+online+and+hybrid+degree+programs+news",
    "is_premium": True
},

# ================= FAKE NEWS =================

"fakepetrol": {
    "category": "other",
    "title": "Free petrol for all citizens from next month",
    "date": "24 January 2026 | 06:00 PM IST",
    "image": "fakepetrol.png",
    "content": [
        "A viral post claimed that petrol would be provided free to all citizens.",
        "No official government notification supports this claim.",
        "Fact-checking agencies confirmed the information is false.",
        "Citizens were advised not to share unverified news."
    ],
    "status": "FAKE"
},

"fakeexams": {
    "category": "education",
    "title": "School exams cancelled permanently",
    "date": "25 January 2026 | 07:30 PM IST",
    "image": "fakeexams.png",
    "content": [
        "A WhatsApp message claimed that school exams are cancelled permanently.",
        "Education boards denied issuing any such announcement.",
        "The message was traced back to an unverified source.",
        "Authorities labeled it as fake news."
    ],
    "status": "FAKE"
}


}

# ================= ROUTES =================
@app.route("/search-news", methods=["POST"])
def search_news():
    data = request.get_json()
    query = data.get("query", "").lower().strip()

    if not query:
        return jsonify({
            "message": "No search query provided",
            "results": [],
            "source": "local"
        })

    results = []
    for news in NEWS.values():
        title = news.get("title", "").lower()
        if query in title:
            results.append(news)
    if not results:
        return jsonify({
            "message": "Here's what we found for your search",
            "results": [],
            "source": "local"
        })

    return jsonify({
        "message": "Showing relevant local update",
        "results": results,
        "source": "local"
    })

# AI SEARCH

@app.route("/ai-search", methods=["POST"])
def ai_search():
    data = request.get_json()
    query = data.get("query", "").strip().lower()

    if not query:
        return jsonify({
            "title": "No query",
            "description": "Please enter something.",
            "source": "system"
        })

    today = datetime.utcnow().strftime("%Y-%m-%d")

    # 🔹 STEP-3.1: MongoDB cache check
    cached = ai_cache_collection.find_one({
        "query": query,
        "date": today
    })

    if cached:
        print("✅ FROM MONGODB CACHE")
        return jsonify({
            "title": cached["title"],
            "description": cached["description"],
            "source": "cache"
        })

    # 🔹 STEP-3.2: Daily AI limit check
    MAX_AI_CALLS_PER_DAY = 20

    limit_doc = ai_limit_collection.find_one({"date": today})
    if limit_doc and limit_doc["count"] >= MAX_AI_CALLS_PER_DAY:
        print("⛔ DAILY LIMIT REACHED")
        return jsonify({
            "title": query,
            "description": "AI daily limit reached. Try again tomorrow.",
            "source": "limit"
        })

    # 🔹 STEP-3.3: AI CALL
    try:
        print("🤖 CALLING GEMINI")

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Give short news about {query}"
        )

        title = f"{query.title()} news"
        description = response.text

        # 🔹 STEP-3.4: Save to MongoDB
        ai_cache_collection.insert_one({
            "query": query,
            "title": title,
            "description": description,
            "date": today,
            "created_at": datetime.utcnow()
        })

        ai_limit_collection.update_one(
            {"date": today},
            {"$inc": {"count": 1}},
            upsert=True
        )

        print("💾 SAVED TO DB")

        return jsonify({
            "title": title,
            "description": description,
            "source": "ai"
        })

    except Exception as e:
        print("❌ AI ERROR:", e)
        return jsonify({
            "title": query,
            "description": "AI is temporarily busy. Try again later.",
            "source": "error"
        })




# AI NEWS
@app.route("/ai-news")
def ai_news():
    query = request.args.get("query", "").strip()

    if not query:
        query = "Unknown topic"

    # TEMP AI CONTENT (abhi bina API)
    summary = f"{query} related latest information"

    return render_template(
        "ai_news.html",
        title=query,
        summary=summary
    )

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = user_collection.find_one({
            "email": email,
            
        })

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user"] = user["email"]
            session["user_name"] = user["name"]
            session.permanent = True
            
            return redirect("/dashboard")
        else:
            return "Invalid email or password"

    
    return render_template("login.html")

@app.route("/mark-notification-read", methods=["POST"])
def mark_notification_read():
    if "user" not in session:
        return {"error": "login required"}, 401
    notification_collection.update_many({"seen": False}, {"$set": {"seen": True}})
    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():

    # user login check
    if "user" not in session:
        return redirect("/")

    category = request.args.get("category", "all")

    # default values
    user_is_subscribed = False
    unread_count = 0
    notifications = []

    # get logged in user
    user = user_collection.find_one({"email": session["user"]})

    if user:
        # ==============================
        # 1️⃣ AUTO WELCOME NOTIFICATION
        # ==============================
        existing = notification_collection.find_one({
            "user": session["user"],
            "message": "Welcome to VeriNews Dashboard"
        })

        if not existing:
            notification_collection.insert_one({
                "user": session["user"],
                "message": "Welcome to VeriNews Dashboard",
                "seen": False,
                "created_at": datetime.utcnow()
            })

            # ==============================
# 🔐 SUBSCRIPTION EXPIRY CHECK
# ==============================
        if user and user.get("is_subscribed") and user.get("subscription_expiry"):
            if datetime.utcnow() > user["subscription_expiry"]:
             user_collection.update_one(
            {"email": session["user"]},
            {"$set": {
                "is_subscribed": False,
                "subscription_plan": None,
                "subscription_expiry": None
            }}
             )
             user_is_subscribed=False
            else:
                user_is_subscribed=True
        else:
            user_is_subscribed=False

        
        
    

        unread_count = notification_collection.count_documents({
            "user": session["user"],
            "seen": False
        })

        # ==============================
        # 4️⃣ ALL NOTIFICATIONS (LATEST FIRST)
        # ==============================
        notifications = list(
            notification_collection.find(
                {"user": session["user"]}
            ).sort("_id", -1)
        )

    # ==============================
    # 5️⃣ RENDER DASHBOARD
    # ==============================
    return render_template(
        "dashboard.html",
        news=NEWS,
        selected_category=category,
        username=session.get("user_name", "guest"),
        user_is_subscribed=user_is_subscribed,
        unread_count=unread_count,
        notifications=notifications
    )

   


@app.route("/mark-notifications-seen", methods=["POST"])
def mark_notifications_seen():
    if "user" not in session:
        return {"status": "unauthorized"}, 401

    notification_collection.update_many(
        {
            "user": session["user"],
            "seen": False
        },
        {
            "$set": {"seen": True}
        }
    )

    return {"status": "success"}


@app.route("/account")
def account():
    if "user" not in session:
        return redirect("/")
    user=user_collection.find_one({"email":session["user"]})
    liked_ids=user.get("liked_news",[])
    interested_news=[] 
    for nid in liked_ids:
        nid = str(nid)
        if nid in NEWS:
            item=NEWS[nid]
            interested_news.append({
                "id":nid,
                "title":item.get("title"),
                "category":item.get("category"),
                "image":item.get("image")
            })
    return render_template("account.html", username=user["name"],useremail=user["email"], 
                           interested_news=interested_news,
                             user_is_subscribed=user.get("is_subscribed", False))

@app.route("/sindoor")
def sindoor():
    if "user" not in session:
        return redirect("/")
    return render_template("sindoor.html", username=session.get("user_name", "guest"))


@app.route("/news/<news_id>")
def news_detail(news_id):
    if "user" not in session:
        return redirect("/")
    news = NEWS.get(news_id)
    if news.get("is_premium", False):
        if "user" not in session:
            return redirect("/subscribe")
        user = user_collection.find_one({"email": session["user"]})
        if not user.get("is_subscribed", False):
            return redirect("/subscribe")
        

    if not news:
        return "News not found", 404
    user_intrerest=None
    
    current_category = news.get("category")

    related_news = []
    for nid , item in NEWS.items():
        if item.get("category") == current_category and nid != news_id:
            related_news.append({
                "id": nid,
                "title": item.get("title"),
                "category": item.get("category"),
                "image": item.get("image")
                
            })
            user_intrerest=None
            if "user" in session:
                user=user_collection.find_one({"email": session["user"]})
                if user:
                    if "liked_news" in user and news_id in user.get("liked_news", []):
                        user_intrerest="like"
                    elif "disliked_news" in user and news_id in user.get("disliked_news", []):
                        user_intrerest="dislike"
                    else:
                        user_intrerest="none"
            
    return render_template("news_detail.html", news=news,related_news=related_news,
                           news_id=news_id, username=session.get("user_name" , "guest"), user_intrerest=user_intrerest)





@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if email already exists
        existing_user = user_collection.find_one({"email": email})
        if existing_user:
            return "Email already registered"

        # Hash password
        hashed_password = generate_password_hash(password)

        # Save user
        user_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password,
            
            

        })
        session["user"] = email
        session["user_name"] = name
        session.permanent = True

        return redirect("/dashboard")

    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("user_name", None)
    session.clear()
    return redirect("/")

@app.route("/interest/<news_id>/<action>", methods=["POST"])
def interest_news(news_id, action):
    if "user" not in session:
        return {"error": "login required"}, 401

    user_email = session["user"]

    if action == "like":
        notification_collection.insert_one({
            "user": user_email,
            "message":"you marked a news as intrested",
            "seen": False
        })
        user_collection.update_one(
            {"email": user_email},
            {
                "$addToSet": {"liked_news": news_id},
                "$pull": {"disliked_news": news_id}
            }
        )

    elif action == "dislike":
        notification_collection.insert_one({
            "user": user_email,
            "message":f"you marked a news as not intrested",
            "seen": False

        })
        user_collection.update_one(
            {"email": user_email},
            {
                "$addToSet": {"disliked_news": news_id},
                "$pull": {"liked_news": news_id}
            }
        )

    elif action == "remove":
        user_collection.update_one(
            {"email": user_email},
            {
                "$pull": {
                    "liked_news": news_id,
                    "disliked_news": news_id
                }
            }
        )

    return {"status": "ok"}



@app.route("/subscribe")
def subscribe():
    if "user" not in session:
        return redirect("/")
    return render_template("subscribe.html",razorpay_key="rzp_test_SAN7b93uE9QTKk")

@app.route("/create-order", methods=["POST"])
def create_order():
    try:
        data = request.get_json()
        amount = int(data.get("amount")) * 100  # rupees → paise

        order = razorpay_client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        return {
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"]
        }

    except Exception as e:
        print("❌ Razorpay error:", e)
        return {
            "error": str(e)
        }, 500

@app.route("/payment-success")
def payment_success():

    if "user" not in session:
        return redirect("/")

    user = user_collection.find_one({"email": session["user"]})

    # already subscribed user ko dobara process mat karo
    if user and user.get("is_subscribed") is True:
        return redirect("/account")
    
    plan = request.args.get("plan")

    now = datetime.utcnow()

    if plan == "monthly":
        expiry_date = now + timedelta(days=30)
    elif plan == "half_yearly":
        expiry_date = now + timedelta(days=180)
    elif plan == "yearly":
        expiry_date = now + timedelta(days=365)
    else:
        return redirect("/subscribe")

    user_collection.update_one(
        {"email": session["user"]},
        {"$set": {
            "is_subscribed": True,
            "subscription_plan": plan,
            "subscription_expiry": expiry_date
        }}
    )

    notification_collection.insert_one({
        "user": session["user"],
        "message": "Your subscription is active, you can now access premium news.",
        "seen": False,
        "created_at": datetime.utcnow()
    })

    return render_template("payment_sucess.html",plan=plan,expiry_date=expiry_date)


@app.route("/check-news", methods=["POST"])
def check_news():
    data = request.get_json()
    news_text = data.get("news", "").strip()

    if not news_text:
        return jsonify({
            "result": "Please paste some news text.",
            "label": "error"
        })

    normalized = news_text.lower().strip()

    # 🔹 STEP 1: DB CHECK (AI LIMIT SAVE)
    cached = check_news_collection.find_one({"news": normalized})
    if cached:
        print("✅ CHECK NEWS FROM DB")
        return jsonify({
            "result": cached["result"],
            "label": cached["label"],
            "source": "cache"
        })

    # 🔹 STEP 2: GEMINI CALL
    try:
        print("🤖 CALLING GEMINI FOR CHECK NEWS")

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
Analyze the news and answer ONLY ONE:
- Real News
- Fake News
- Needs More Verification

News:
{news_text}
"""
        )

        verdict = response.text.strip()

        # 🔹 STEP 3: MAP RESULT → LABEL
        if "real" in verdict.lower():
            label = "real"
        elif "fake" in verdict.lower():
            label = "fake"
        else:
            label = "verify"

        # 🔹 STEP 4: SAVE TO DB
        check_news_collection.insert_one({
            "news": normalized,
            "result": verdict,
            "label": label,
            "created_at": datetime.utcnow()
        })

        print("💾 CHECK NEWS SAVED TO DB")

        return jsonify({
            "result": verdict,
            "label": label,
            "source": "ai"
        })

    except Exception as e:
        print("❌ GEMINI ERROR:", e)
        return jsonify({
            "result": "AI is temporarily unavailable. Please try again later.",
            "label": "error"
        })




# ================= RUN =================
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )