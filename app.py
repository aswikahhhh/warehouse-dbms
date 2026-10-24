import os
from functools import wraps
from datetime import date
from decimal import Decimal, InvalidOperation

import click
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY") or "dev-secret-key-change-me"
app.config.update(
    MYSQL_HOST=os.getenv("DB_HOST", "localhost"),
    MYSQL_PORT=int(os.getenv("DB_PORT", "3306")),
    MYSQL_USER=os.getenv("DB_USER", "root"),
    MYSQL_PASSWORD=os.getenv("DB_PASSWORD", ""),
    MYSQL_DB=os.getenv("DB_NAME", "warehouse_management"),
    MYSQL_CURSORCLASS="DictCursor",
)
mysql = MySQL(app)

MODULES = {
    "employees": {"title":"Employees","table":"employee","pk":"emp_id",
        "columns":[("emp_id","Employee ID"),("name","Name"),("email_id","Email"),("phone","Phone"),("designation","Designation"),("warehouse_id","Warehouse ID")],
        "fields":[("name","Name","text",True),("email_id","Email","email",True),("phone","Phone","text",False),("designation","Designation","text",True)],
        "sql":"SELECT emp_id,name,email_id,phone,designation,warehouse_id FROM employee WHERE warehouse_id=%s ORDER BY emp_id DESC",
        "insert":"INSERT INTO employee (name,email_id,phone,designation,warehouse_id) VALUES (%s,%s,%s,%s,%s)"},
    "products": {"title":"Products","table":"product","pk":"product_id",
        "columns":[("product_id","Product ID"),("name","Name"),("category","Category"),("warranty_month","Warranty (months)"),("price","Price")],
        "fields":[("name","Product name","text",True),("category","Category","text",False),("warranty_month","Warranty (months)","number",True),("price","Price","number",True)],
        "sql":"SELECT product_id,name,category,warranty_month,price FROM product WHERE warehouse_id=%s ORDER BY product_id DESC",
        "insert":"INSERT INTO product (name,category,warranty_month,price,warehouse_id) VALUES (%s,%s,%s,%s,%s)"},
    "storage": {"title":"Storage","table":"storage","pk":"storage_id",
        "columns":[("storage_id","Storage ID"),("storage_name","Storage name"),("capacity","Capacity"),("location","Location"),("warehouse_id","Warehouse ID")],
        "fields":[("storage_name","Storage name","text",True),("capacity","Capacity","number",True),("location","Location","text",False)],
        "sql":"SELECT storage_id,storage_name,capacity,location,warehouse_id FROM storage WHERE warehouse_id=%s ORDER BY storage_id DESC",
        "insert":"INSERT INTO storage (storage_name,capacity,location,warehouse_id) VALUES (%s,%s,%s,%s)"},
    "inventory": {"title":"Inventory","table":"inventory","pk":"inventory_id",
        "columns":[("inventory_id","Inventory ID"),("product_id","Product ID"),("reorder_level","Reorder level"),("qty_available","Available quantity"),("last_updated","Last updated")],
        "fields":[("product_id","Product","select_product",True),("reorder_level","Reorder level","number",True),("qty_available","Available quantity","number",True)],
        "sql":"SELECT i.inventory_id,i.product_id,i.reorder_level,i.qty_available,i.last_updated FROM inventory i WHERE i.warehouse_id=%s ORDER BY i.inventory_id DESC",
        "insert":"INSERT INTO inventory (product_id,warehouse_id,reorder_level,qty_available) VALUES (%s,%s,%s,%s)"},
    "stock-requests": {"title":"Stock requests","table":"stock_request","pk":"sr_id",
        "columns":[("sr_id","Request ID"),("req_date","Request date"),("status","Status"),("product_id","Product ID"),("qty","Quantity"),("warehouse_id","Warehouse ID")],
        "fields":[("req_date","Request date","date",True),("status","Status","select_request_status",True),("product_id","Product","select_product",True),("qty","Quantity","number",True)],
        "sql":"SELECT sr_id,req_date,status,product_id,qty,warehouse_id FROM stock_request WHERE warehouse_id=%s ORDER BY sr_id DESC",
        "insert":"INSERT INTO stock_request (req_date,status,product_id,qty,warehouse_id,requested_by) VALUES (%s,%s,%s,%s,%s,%s)"},
    "stock-transfers": {"title":"Stock transfers","table":"stock_transfer","pk":"st_id",
        "columns":[("st_id","Transfer ID"),("name","Transfer / product"),("received_qty","Received quantity"),("received_date","Received date"),("sr_id","Request ID")],
        "fields":[("name","Transfer / product","text",True),("received_qty","Received quantity","number",True),("received_date","Received date","date",False),("sr_id","Stock request","select_request",True)],
        "sql":"SELECT t.st_id,t.name,t.received_qty,t.received_date,t.sr_id FROM stock_transfer t JOIN stock_request r ON r.sr_id=t.sr_id WHERE r.warehouse_id=%s ORDER BY t.st_id DESC",
        "insert":"INSERT INTO stock_transfer (name,received_qty,received_date,sr_id) VALUES (%s,%s,%s,%s)"},
    "units": {"title":"Units / Barcodes","table":"unit","pk":"barcode_id",
        "columns":[("barcode_id","Barcode ID"),("status","Status"),("received_date","Received date"),("product_id","Product ID"),("storage_id","Storage ID")],
        "fields":[("barcode_id","Barcode ID","text",True),("status","Status","select_unit_status",True),("received_date","Received date","date",False),("product_id","Product","select_product",True),("storage_id","Storage","select_storage",True)],
        "sql":"SELECT barcode_id,status,received_date,product_id,storage_id FROM unit WHERE warehouse_id=%s ORDER BY barcode_id DESC",
        "insert":"INSERT INTO unit (barcode_id,status,received_date,product_id,storage_id,warehouse_id) VALUES (%s,%s,%s,%s,%s,%s)"},
    "retail-shops": {"title":"Retail shops","table":"retail_shop","pk":"shop_id",
        "columns":[("shop_id","Shop ID"),("shop_name","Shop name"),("address","Address"),("phone_no","Phone")],
        "fields":[("shop_name","Shop name","text",True),("address","Address","text",False),("phone_no","Phone","text",False)],
        "sql":"SELECT shop_id,shop_name,address,phone_no FROM retail_shop ORDER BY shop_id DESC",
        "insert":"INSERT INTO retail_shop (shop_name,address,phone_no) VALUES (%s,%s,%s)"},
    "sale-orders": {"title":"Sale orders","table":"sale_order","pk":"so_id",
        "columns":[("so_id","Order ID"),("status","Status"),("order_date","Order date"),("product_quantity","Quantity"),("product_name","Product"),("shop_id","Shop ID")],
        "fields":[("status","Status","select_order_status",True),("order_date","Order date","date",True),("product_quantity","Quantity","number",True),("product_name","Product name","text",False),("shop_id","Retail shop","select_shop",True)],
        "sql":"SELECT so_id,status,order_date,product_quantity,product_name,shop_id FROM sale_order WHERE warehouse_id=%s ORDER BY so_id DESC",
        "insert":"INSERT INTO sale_order (status,order_date,product_quantity,product_name,shop_id,warehouse_id) VALUES (%s,%s,%s,%s,%s,%s)"},
    "sale-order-items": {"title":"Sale order items","table":"sale_order_item","pk":"sop_id",
        "columns":[("sop_id","Item ID"),("st_id","Transfer ID"),("name","Item name"),("qty_supplied","Qty supplied"),("supplied_date","Supplied date"),("so_id","Order ID"),("product_id","Product ID")],
        "fields":[("st_id","Transfer ID (optional)","number",False),("name","Item name","text",True),("qty_supplied","Quantity supplied","number",True),("supplied_date","Supplied date","date",False),("so_id","Sale order","select_order",True),("product_id","Product","select_product",True)],
        "sql":"SELECT sop_id,st_id,name,qty_supplied,supplied_date,so_id,product_id FROM sale_order_item WHERE warehouse_id=%s ORDER BY sop_id DESC",
        "insert":"INSERT INTO sale_order_item (st_id,name,qty_supplied,supplied_date,so_id,product_id,warehouse_id) VALUES (%s,%s,%s,%s,%s,%s,%s)"},
}

def get_cursor():
    return mysql.connection.cursor()

def current_user():
    return session.get("user")

def manager_only(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return redirect(url_for("login"))
        if user.get("designation", "").lower() not in ("manager", "warehouse manager", "admin"):
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    return redirect(url_for("dashboard") if current_user() else url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        cur = get_cursor()
        cur.execute("""SELECT e.emp_id,e.name,e.email_id,e.designation,e.warehouse_id,e.password_hash,w.warehouse_name
                       FROM employee e JOIN warehouse w ON w.warehouse_id=e.warehouse_id
                       WHERE LOWER(e.email_id)=%s LIMIT 1""", (email,))
        user = cur.fetchone()
        cur.close()
        if user and user.get("password_hash") and check_password_hash(user["password_hash"], password):
            if user["designation"].lower() not in ("manager", "warehouse manager", "admin"):
                flash("This login is for warehouse managers only.", "error")
            else:
                session.clear()
                session["user"] = {k:user[k] for k in ("emp_id","name","email_id","designation","warehouse_id","warehouse_name")}
                return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password. Check the credentials or run the seed-managers command.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

@app.route("/dashboard")
@manager_only
def dashboard():
    u=current_user(); wid=u["warehouse_id"]; cur=get_cursor()
    cur.execute("SELECT COUNT(*) n FROM employee WHERE warehouse_id=%s",(wid,)); employees=cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) n FROM storage WHERE warehouse_id=%s",(wid,)); storages=cur.fetchone()["n"]
    cur.execute("SELECT COALESCE(SUM(qty_available),0) n FROM inventory WHERE warehouse_id=%s",(wid,)); units=cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) n FROM stock_request WHERE warehouse_id=%s AND status='Pending'",(wid,)); pending=cur.fetchone()["n"]
    cur.execute("""SELECT p.name,i.qty_available,i.reorder_level FROM inventory i
                   JOIN product p ON p.product_id=i.product_id WHERE i.warehouse_id=%s
                   ORDER BY (i.qty_available<=i.reorder_level) DESC,p.name LIMIT 8""",(wid,))
    stock_rows=cur.fetchall(); cur.close()
    return render_template("dashboard.html",employees=employees,storages=storages,units=units,pending=pending,stock_rows=stock_rows,today=date.today().isoformat())

def option_data():
    cur=get_cursor(); wid=current_user()["warehouse_id"]
    cur.execute("SELECT product_id,name FROM product WHERE warehouse_id=%s ORDER BY name",(wid,)); products=cur.fetchall()
    cur.execute("SELECT storage_id,storage_name FROM storage WHERE warehouse_id=%s ORDER BY storage_name",(wid,)); storages=cur.fetchall()
    cur.execute("SELECT sr_id FROM stock_request WHERE warehouse_id=%s ORDER BY sr_id DESC",(wid,)); requests=cur.fetchall()
    cur.execute("SELECT so_id FROM sale_order WHERE warehouse_id=%s ORDER BY so_id DESC",(wid,)); orders=cur.fetchall()
    cur.execute("SELECT shop_id,shop_name FROM retail_shop ORDER BY shop_name"); shops=cur.fetchall()
    cur.close()
    return {"products":products,"storages":storages,"requests":requests,"orders":orders,"shops":shops}

def field_values(field, raw, opts):
    if raw is None:
        raw = ""
    raw = raw.strip()
    if raw == "" and field[3]:
        raise ValueError(f"{field[1]} is required.")
    if raw == "" and not field[3]:
        return None

    typ = field[2]
    if typ == "number":
        try:
            value = Decimal(raw)
            if value < 0:
                raise ValueError(f"{field[1]} cannot be negative.")
            return int(value) if value == value.to_integral_value() else value
        except (InvalidOperation, ValueError):
            raise ValueError(f"{field[1]} must be a valid non-negative number.")
    if typ == "date":
        return raw or None
    option_types = {
        "select_product": ("products", "product_id"),
        "select_storage": ("storages", "storage_id"),
        "select_request": ("requests", "sr_id"),
        "select_order": ("orders", "so_id"),
        "select_shop": ("shops", "shop_id"),
    }
    if typ in option_types:
        key, pk = option_types[typ]
        valid = {str(x[pk]) for x in opts[key]}
        if raw not in valid:
            raise ValueError(f"Choose a valid {field[1].lower()} for your warehouse.")
        return int(raw)
    allowed = {
        "select_request_status": {"Pending", "Approved", "Rejected", "Fulfilled"},
        "select_unit_status": {"Available", "Reserved", "Dispatched", "Damaged"},
        "select_order_status": {"Pending", "Approved", "Dispatched", "Cancelled"},
    }
    if typ in allowed:
        if raw not in allowed[typ]:
            raise ValueError("Choose a valid option.")
        return raw
    return raw

@app.route("/module/<slug>", methods=["GET","POST"])
@manager_only
def module_page(slug):
    if slug not in MODULES: abort(404)
    cfg=MODULES[slug]; u=current_user(); opts=option_data()
    if request.method=="POST":
        cur=None
        try:
            values=[]
            for f in cfg["fields"]:
                raw_value = request.form.get(f[0], "")
                values.append(field_values(f, raw_value, opts))
            if slug in ("employees","storage","products","units","sale-orders","sale-order-items"): values.append(u["warehouse_id"])
            elif slug=="inventory": values=[values[0],u["warehouse_id"],values[1],values[2]]
            elif slug=="stock-requests": values.extend([u["warehouse_id"],u["emp_id"]])
            cur=get_cursor(); cur.execute(cfg["insert"],tuple(values)); mysql.connection.commit(); cur.close()
            flash(f'{cfg["title"]}: record added successfully.',"success")
            return redirect(url_for("module_page",slug=slug))
        except (ValueError, Exception) as exc:
            mysql.connection.rollback()
            if cur: cur.close()
            flash(f"Could not save record: {exc}","error")
    cur=get_cursor(); cur.execute(cfg["sql"],(u["warehouse_id"],) if "%s" in cfg["sql"] else ())
    rows=cur.fetchall(); cur.close()
    return render_template("module.html",cfg=cfg,rows=rows,options=opts,today=date.today().isoformat())

@app.route("/module/<slug>/delete/<record_id>",methods=["POST"])
@manager_only
def delete_record(slug,record_id):
    if slug not in MODULES: abort(404)
    scoped={"employees":("employee","emp_id"),"storage":("storage","storage_id"),"inventory":("inventory","inventory_id"),
            "stock-requests":("stock_request","sr_id"),"units":("unit","barcode_id"),
            "sale-orders":("sale_order","so_id"),"sale-order-items":("sale_order_item","sop_id")}
    if slug not in scoped:
        flash("Delete is disabled for this module to protect linked records.","error")
        return redirect(url_for("module_page",slug=slug))
    table,pk=scoped[slug]; cur=get_cursor()
    cur.execute(f"DELETE FROM {table} WHERE {pk}=%s AND warehouse_id=%s",(record_id,current_user()["warehouse_id"]))
    deleted=cur.rowcount; mysql.connection.commit(); cur.close()
    flash("Record deleted." if deleted else "Record not found in your warehouse.","success" if deleted else "error")
    return redirect(url_for("module_page",slug=slug))

@app.cli.command("create-manager")
@click.option("--name",prompt="Manager name")
@click.option("--email",prompt="Manager email")
@click.option("--warehouse-id",prompt="Warehouse ID",type=int)
@click.option("--password",prompt=True,hide_input=True,confirmation_prompt=True)
def create_manager(name,email,warehouse_id,password):
    cur=get_cursor()
    cur.execute("SELECT warehouse_id FROM warehouse WHERE warehouse_id=%s",(warehouse_id,))
    if not cur.fetchone():
        cur.close(); raise click.ClickException("Warehouse ID does not exist. Import schema.sql first.")
    cur.execute("SELECT emp_id FROM employee WHERE email_id=%s",(email,))
    existing=cur.fetchone(); hashed=generate_password_hash(password)
    if existing:
        cur.execute("UPDATE employee SET name=%s,designation='Warehouse Manager',warehouse_id=%s,password_hash=%s WHERE emp_id=%s",
                    (name,warehouse_id,hashed,existing["emp_id"]))
    else:
        cur.execute("INSERT INTO employee (name,email_id,designation,warehouse_id,password_hash) VALUES (%s,%s,'Warehouse Manager',%s,%s)",
                    (name,email,warehouse_id,hashed))
    mysql.connection.commit(); cur.close(); click.echo("Manager account created/updated.")

@app.cli.command("seed-managers")
def seed_managers():
    """Create three demo manager accounts with hashed passwords."""
    accounts=[
        ("Rahul Kumar","manager1@waresmart.demo",1,"WareSmart@101"),
        ("Meera Nair","manager2@waresmart.demo",2,"WareSmart@202"),
        ("Fathima P","manager3@waresmart.demo",3,"WareSmart@303"),
    ]
    cur=get_cursor()
    for name,email,wid,password in accounts:
        cur.execute("SELECT warehouse_id FROM warehouse WHERE warehouse_id=%s",(wid,))
        if not cur.fetchone():
            cur.close(); raise click.ClickException(f"Warehouse {wid} is missing. Import schema.sql and dummy_data.sql first.")
        cur.execute("SELECT emp_id FROM employee WHERE email_id=%s",(email,))
        existing=cur.fetchone(); hashed=generate_password_hash(password)
        if existing:
            cur.execute("UPDATE employee SET name=%s,designation='Warehouse Manager',warehouse_id=%s,password_hash=%s WHERE emp_id=%s",
                        (name,wid,hashed,existing["emp_id"]))
        else:
            cur.execute("INSERT INTO employee (name,email_id,designation,warehouse_id,password_hash) VALUES (%s,%s,'Warehouse Manager',%s,%s)",
                        (name,email,wid,hashed))
    mysql.connection.commit(); cur.close()
    click.echo("Three demo manager accounts are ready. Change these demo passwords before real use.")

@app.errorhandler(403)
def forbidden(_): return render_template("error.html",code=403,message="Your account is not allowed to access this page."),403
@app.errorhandler(404)
def not_found(_): return render_template("error.html",code=404,message="The page or record was not found."),404

if __name__=="__main__":
    app.run(debug=os.getenv("FLASK_DEBUG","0")=="1")
