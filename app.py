from flask import Flask, render_template, request, session, redirect
from config import Config
from models.user import db, User
from models.food import Food
from models.order import Order
import os
from werkzeug.utils import secure_filename
from openpyxl import Workbook
from flask import send_file
from twilio.rest import Client
import random
from dotenv import load_dotenv

app = Flask(__name__)

# Secret Key
app.secret_key = "food_order_secret_key"

# Upload Folder
app.config["UPLOAD_FOLDER"] = "static/images"

# Database Configuration
app.config.from_object(Config)

# Initialize Database
db.init_app(app)

# ---------------- TWILIO CONFIG ----------------
load_dotenv()

ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")

client = Client(
    ACCOUNT_SID,
    AUTH_TOKEN
)
# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- MENU ----------------

@app.route("/menu")
def menu():

    foods = Food.query.all()

    return render_template("menu.html", foods=foods)


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        user = User(
            name=request.form["name"],
            email=request.form["email"],
            password=request.form["password"]
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session["user"] = user.name
            return redirect("/menu")

        return "Invalid Email or Password!"

    return render_template("login.html")

# ---------------- ADD TO CART ----------------

@app.route("/add_to_cart/<int:item_id>")
def add_to_cart(item_id):

    if "cart" not in session:
        session["cart"] = []

    cart = session["cart"]

    # If item already exists, increase quantity
    for item in cart:
        if item["id"] == item_id:
            item["quantity"] += 1
            session["cart"] = cart
            return redirect("/cart")

    # Otherwise add new item
    food = db.session.get(Food, item_id)

    if food:
        cart.append({
            "id": food.id,
            "name": food.name,
            "price": food.price,
            "image": food.image,
            "quantity": 1
        })

    session["cart"] = cart

    return redirect("/cart")


# ---------------- INCREASE QUANTITY ----------------

@app.route("/increase_quantity/<int:item_id>")
def increase_quantity(item_id):

    cart = session.get("cart", [])

    for item in cart:
        if item["id"] == item_id:
            item["quantity"] += 1
            break

    session["cart"] = cart

    return redirect("/cart")


# ---------------- DECREASE QUANTITY ----------------

@app.route("/decrease_quantity/<int:item_id>")
def decrease_quantity(item_id):

    cart = session.get("cart", [])

    for item in cart:
        if item["id"] == item_id:

            if item["quantity"] > 1:
                item["quantity"] -= 1
            else:
                cart.remove(item)

            break

    session["cart"] = cart

    return redirect("/cart")


# ---------------- REMOVE FROM CART ----------------

@app.route("/remove_from_cart/<int:index>")
def remove_from_cart(index):

    cart = session.get("cart", [])

    if 0 <= index < len(cart):
        cart.pop(index)

    session["cart"] = cart

    return redirect("/cart")


# ---------------- CART ----------------

@app.route("/cart")
def cart():

    cart = session.get("cart", [])

    total = sum(item["price"] * item["quantity"] for item in cart)

    return render_template(
        "cart.html",
        cart=cart,
        total=total
    )

# ---------------- CHECKOUT ----------------

@app.route("/checkout")
def checkout():

    return render_template("checkout.html")


# ---------------- PLACE ORDER ----------------

@app.route("/place_order", methods=["POST"])
def place_order():

    cart = session.get("cart", [])

    if not cart:
        return redirect("/menu")

    customer = request.form["name"]
    phone = request.form["phone"]
    payment = request.form["payment"]

    # Store customer details in session
    session["customer"] = customer
    session["phone"] = phone
    session["payment"] = payment

    # Generate OTP
    otp = str(random.randint(100000, 999999))
    session["otp"] = otp

    # Send OTP using Twilio
    try:

        client.messages.create(
            body=f"Your Food Order OTP is {otp}",
            from_=TWILIO_NUMBER,
            to="+91" + phone
        )

    except Exception as e:
        return f"SMS Error: {e}"

    return redirect("/verify_otp")


# ---------------- VERIFY OTP ----------------

@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():

    if request.method == "POST":

        entered_otp = request.form["otp"]

        if entered_otp == session.get("otp"):

            cart = session.get("cart", [])

            for item in cart:

                order = Order(
                    customer=session["customer"],
                    phone=session["phone"],
                    food=item["name"],
                    quantity=item["quantity"],
                    total=item["price"] * item["quantity"],
                    payment=session["payment"],
                    status="Pending"
                )

                db.session.add(order)

            db.session.commit()

            # Clear session data
            session.pop("cart", None)
            session.pop("otp", None)
            session.pop("customer", None)
            session.pop("phone", None)
            session.pop("payment", None)

            return render_template(
                "order_success.html",
                name=session.get("user", "Customer")
            )

        return render_template(
            "verify_otp.html",
            error="Invalid OTP!"
        )

    return render_template("verify_otp.html")


# ---------------- ORDERS ----------------
@app.route("/orders")
def orders():

    search = request.args.get("search")

    if search:
        all_orders = Order.query.filter(
            Order.customer.ilike(f"%{search}%")
        ).all()
    else:
        all_orders = Order.query.all()

    total_orders = Order.query.count()

    pending_orders = Order.query.filter_by(
        status="Pending"
    ).count()
    preparing_orders = Order.query.filter_by(
    status="Preparing"
    ).count()
    out_orders = Order.query.filter_by(
    status="Out for Delivery"
    ).count()

    delivered_orders = Order.query.filter_by(
    status="Delivered"
    ).count()


    cancelled_orders = Order.query.filter_by(
        status="Cancelled"
    ).count()

    total_revenue = sum(order.total for order in Order.query.all())

    total_customers = db.session.query(
        Order.customer
    ).distinct().count()

    return render_template(
    "orders.html",
    orders=all_orders,
    total_orders=total_orders,
    pending_orders=pending_orders,
    preparing_orders=preparing_orders,
    out_orders=out_orders,
    delivered_orders=delivered_orders,
    cancelled_orders=cancelled_orders,
    total_revenue=total_revenue,
    total_customers=total_customers
)
# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")

# ---------------- DELETE FOOD ----------------

@app.route("/delete_food/<int:id>")
def delete_food(id):

    food = db.session.get(Food, id)

    if food:
        db.session.delete(food)
        db.session.commit()

    return redirect("/admin")


# ---------------- ADMIN ----------------

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        name = request.form["name"]
        price = request.form["price"]

        image = request.files["image"]

        if image and image.filename != "":

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )

            food = Food(
                name=name,
                price=price,
                image=filename
            )

            db.session.add(food)
            db.session.commit()

        return redirect("/admin")

    foods = Food.query.all()

    total_foods = Food.query.count()
    total_users = User.query.count()

    return render_template(
        "admin.html",
        foods=foods,
        total_foods=total_foods,
        total_users=total_users
    )

# ---------------- UPDATE ORDER STATUS ----------------

@app.route("/update_status/<int:id>/<status>")
def update_status(id, status):

    order = db.session.get(Order, id)

    if order:
        order.status = status
        db.session.commit()

    return redirect("/orders")

# ---------------- EXPORT TO EXCEL ----------------

@app.route("/export_excel")
def export_excel():

    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"

    ws.append([
        "Order ID",
        "Customer",
        "Food",
        "Quantity",
        "Total",
        "Payment",
        "Status",
        "Date"
    ])

    orders = Order.query.all()

    for order in orders:
        ws.append([
            order.id,
            order.customer,
            order.food,
            order.quantity,
            order.total,
            order.payment,
            order.status,
            order.order_date.strftime("%d-%m-%Y %H:%M")
            if order.order_date else ""
        ])

    filename = "orders.xlsx"
    wb.save(filename)

    return send_file(
        filename,
        as_attachment=True
    )

@app.route("/track_order/<int:id>")
def track_order(id):
    order = Order.query.get_or_404(id)
    return render_template("track_order.html", order=order)


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":

    with app.app_context():
        db.create_all()
    print(app.url_map)   # <-- Add this line

    app.run(debug=True)

      