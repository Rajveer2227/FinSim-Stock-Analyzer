from flask import Flask, request, jsonify, session
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

CORS(app, origins=["http://localhost:3000"], supports_credentials=True)  # Allow requests from React (localhost:3000)

# MySQL Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="stock_db"
)

cursor = db.cursor()

# API to handle feedback submission
@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    feedback = data.get('feedback')
    rating = data.get('rating')

    try:
        insert_query = """
            INSERT INTO feedbacks (name, email, feedback, rating)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (name, email, feedback, rating))
        db.commit()
        return jsonify({"message": "Feedback submitted successfully!"}), 201

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        return jsonify({"error": "Failed to submit feedback"}), 500

# API to handle user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    id_number = data.get('idNumber')

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match!"}), 400

    try:
        insert_query = """
            INSERT INTO users (first_name, last_name, email, phone, password, id_number)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (first_name, last_name, email, phone, password, id_number))
        db.commit()
        return jsonify({"message": "User registered successfully"}), 201
    
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        return jsonify({"error": "Failed to register user"}), 500

@app.route('/api/profile', methods=['GET'])
def get_profile():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401  # User must be logged in

    user_id = session['user_id']
    
    # Fetch user profile data from the database
    cursor = db.cursor()

    try:
        cursor.execute("""
            SELECT first_name, last_name, email, phone, id_number FROM users WHERE user_id=%s
        """, (user_id,))
        
        # Fetch the result
        user = cursor.fetchone()
        
        if user:
            # Return the user's profile data
            return jsonify({
                "first_name": user[0],
                "last_name": user[1],
                "email": user[2],
                "phone": user[3],
                "id_number": user[4]
            }), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except mysql.connector.Error as err:
        return jsonify({"message": f"Database error: {err}"}), 500
    finally:
        cursor.close()  # Close the cursor to avoid memory leaks

@app.route('/api/updateProfile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401  # User must be logged in

    user_id = session['user_id']
    data = request.get_json()

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone = data.get('phone')
    id_number = data.get('id_number')
    password = data.get('password')

    # Update user profile in the database
    cursor = db.cursor()

    try:
        if password:
            hashed_password = password  # For simplicity, not hashing here
            cursor.execute("""
                UPDATE users
                SET first_name=%s, last_name=%s, email=%s, phone=%s, id_number=%s, password=%s
                WHERE user_id=%s
            """, (first_name, last_name, email, phone, id_number, hashed_password, user_id))
        else:
            cursor.execute("""
                UPDATE users
                SET first_name=%s, last_name=%s, email=%s, phone=%s, id_number=%s
                WHERE user_id=%s
            """, (first_name, last_name, email, phone, id_number, user_id))

        db.commit()  # Commit the changes to the database
    except mysql.connector.Error as err:
        db.rollback()  # Rollback if there is any error
        return jsonify({"message": f"Database error: {err}"}), 500
    finally:
        cursor.close()  # Close the cursor to avoid memory leaks

    return jsonify({"message": "Profile updated successfully!"}), 200

# API to handle user login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    # Constructing the SQL query to check the user credentials and role
    select_query = """
        SELECT role, user_id, first_name FROM users WHERE email = %s AND password = %s
    """
    
    cursor.execute(select_query, (email, password))
    result = cursor.fetchone()

    if result:
        role = result[0]  # role will be either 'admin' or 'user'
        user_id = result[1]
        first_name = result[2]

        # Set session variables
        session['user_id'] = user_id
        session['role'] = role
        session['first_name'] = first_name

         # ✅ Print session values to console
        print("Logged in session:")
        print("User ID:", session.get('user_id'))
        print("Role:", session.get('role'))
        print("Name:",session.get('first_name'))

        if role == 'admin':
            return jsonify({"message": "Admin login successful! Redirecting to Admin dashboard."}), 200
        elif role == 'customer':
            return jsonify({"message": "Customer login successful! Redirecting to User dashboard."}), 200
        else:
            return jsonify({"error": "Role is neither 'admin' nor 'user'."}), 400
    else:
        # Sending a structured error response
        return jsonify({"error": "Invalid email or password!"}), 401

@app.route('/api/username', methods=['GET'])
def get_username():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401
    return jsonify({"name": session.get('first_name', '')})


# API to handle adding stock
@app.route('/api/admin/stocks', methods=['POST'])
def add_stock():
    data = request.get_json()
    # turn JS array into comma-string
    sector_str = ",".join(data.get('sector', []))

    try:
        insert_sql = """
            INSERT INTO stocks
               (symbol, company_name, total_stock, price_per_stock, sector, market_cap)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (
            data['symbol'],
            data['company_name'],
            int(data['total_stock']),
            float(data['price_per_stock']),
            sector_str,
            data['market_cap']
        ))
        db.commit()
          # ✅ Return success message properly
        response = jsonify(message="Stock added successfully!")
        response.status_code = 201
        return response

    except Exception as e:
        db.rollback()
        print("Insert error:", e)
        return jsonify({ "error": str(e) }), 500

# Fetch stocks
@app.route('/api/admin/stocks', methods=['GET'])
def get_all_stocks():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="stock_db"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM stocks")
    stocks = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(stocks)


# UPDATE stock by ID
@app.route('/api/admin/stocks/<int:id>', methods=['PUT'])
def update_stock(id):
    data = request.get_json()

    try:
        cursor = db.cursor()
        query = """
            UPDATE stocks SET symbol=%s, company_name=%s, total_stock=%s, 
            price_per_stock=%s, sector=%s, market_cap=%s WHERE id=%s
        """
        values = (
            data['symbol'],
            data['company_name'],
            data['total_stock'],
            data['price_per_stock'],
            ','.join(data['sector']) if isinstance(data['sector'], list) else data['sector'],
            data['market_cap'],
            id
        )
        cursor.execute(query, values)
        db.commit()
        cursor.close()

        return jsonify({'message': 'Stock updated successfully', 'id': id}), 200

    except Exception as e:
        db.rollback()
        print("Update error:", e)
        return jsonify({"error": str(e)}), 500


# DELETE stock by ID
@app.route('/api/admin/stocks/<int:id>', methods=['DELETE'])
def delete_stock(id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="stock_db"
    )
    cursor = conn.cursor()
    cursor.execute("DELETE FROM stocks WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Stock deleted successfully'}), 200
 
 #fetch symbol for user dashboard

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    user_id = session.get('user_id')  # logged-in user ID

    try:
        conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="stock_db"
        )
        cursor = conn.cursor(dictionary=True)

        # Fetch all stocks
        cursor.execute("SELECT * FROM stocks")
        stocks = cursor.fetchall()

        # Fetch user's watchlist (might be empty)
        cursor.execute("SELECT stock_id FROM watchlist WHERE user_id = %s", (user_id,))
        watchlist_rows = cursor.fetchall()
        watchlist = [row['stock_id'] for row in watchlist_rows]  # empty list if nothing

        cursor.close()
        return jsonify({"stocks": stocks, "watchlist": watchlist}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Failed to fetch data"}), 500

# @app.route('/api/stocks', methods=['GET'])
# def get_stocks_for_users():
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="",
#         database="stock_db"
#     )
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT id, symbol, company_name, total_stock, price_per_stock FROM stocks")
#     stocks = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return jsonify(stocks)


#Watch list part


# @app.route('/api/watchlist', methods=['POST'])
# def handle_watchlist():
    data = request.json
    stock_id = data.get('stock_id')
    action = data.get('action')
    user_id = session.get('user_id')  # You must have this set at login

    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    if action == 'add':
         # Insert into DB
        cursor.execute("INSERT  INTO watchlist (user_id, stock_id) VALUES (%s, %s)", (user_id, stock_id))
        db.commit()
        return jsonify({'status': 'added'})
    elif action == 'remove':
        # Remove from DB
        cursor.execute("DELETE FROM watchlist WHERE user_id = %s AND stock_id = %s", (user_id, stock_id))
        db.commit()
        return jsonify({'status': 'removed'})
    else:
        return jsonify({'error': 'Invalid action'}), 400

@app.route('/api/watchlist', methods=['POST'])
def handle_watchlist():
    data = request.json
    stock_id = data.get('stock_id')
    action = data.get('action')
    user_id = session.get('user_id')  # You must have this set at login

    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401

    cursor = db.cursor()  # create cursor locally here

    if action == 'add':
        cursor.execute("INSERT INTO watchlist (user_id, stock_id) VALUES (%s, %s)", (user_id, stock_id))
        db.commit()
        cursor.close()
        return jsonify({'status': 'added'})
    elif action == 'remove':
        cursor.execute("DELETE FROM watchlist WHERE user_id = %s AND stock_id = %s", (user_id, stock_id))
        db.commit()
        cursor.close()
        return jsonify({'status': 'removed'})
    else:
        cursor.close()
        return jsonify({'error': 'Invalid action'}), 400


# @app.route('/api/buy', methods=['POST'])
# def buy_stock():
    data = request.get_json()
    symbol = data.get('symbol')
    company_name = data.get('company_name')
    quantity = int(data.get('quantity'))
    limit_price = float(data.get('limit_price'))  # Limit price can be from the user or current stock price
    user_id = session.get('user_id')  # from logged-in session

    total_price = quantity * limit_price  # Calculate total price

    try:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO portfolio (user_id, symbol, company_name, quantity, limit_price, total_price) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, symbol, company_name, quantity, limit_price, total_price)
        )
        db.commit()
        cursor.close()
        return jsonify({"success": True, "message": "Stock purchased successfully!"}), 201
    except Exception as e:
        db.rollback()
        print(f"Error during stock purchase: {e}")
        return jsonify({"success": False, "error": "Failed to purchase stock"}), 500

@app.route('/api/buy', methods=['POST'])
def buy_stock():
    data = request.get_json()
    symbol = data.get('symbol')
    company_name = data.get('company_name')
    quantity = int(data.get('quantity'))
    limit_price = float(data.get('limit_price'))  # Limit price can be from the user or current stock price
    user_id = session.get('user_id')  # from logged-in session

    total_price = quantity * limit_price  # Calculate total price

    try:
        cursor = db.cursor()

        # Step 1: Insert into portfolio
        cursor.execute(
            "INSERT INTO portfolio (user_id, symbol, company_name, quantity, limit_price, total_price) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, symbol, company_name, quantity, limit_price, total_price)
        )

        # 🔄 Step 2: Update stock table to reduce total_stock
        cursor.execute("""
            UPDATE stocks SET total_stock = total_stock - %s WHERE symbol = %s
        """, (quantity, symbol))

        db.commit()
        cursor.close()
        return jsonify({"success": True, "message": "Stock purchased successfully!"}), 201

    except Exception as e:
        db.rollback()
        print(f"Error during stock purchase: {e}")
        return jsonify({"success": False, "error": "Failed to purchase stock"}), 500


@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    try:
        cursor = db.cursor(dictionary=True)

        query = """
            SELECT 
                p.id AS portfolio_id,
                s.id AS stock_id,
                p.symbol,
                p.company_name,
                p.quantity,
                p.limit_price,
                p.total_price,
                p.created_at,
                s.price_per_stock AS current_price,
                (s.price_per_stock - p.limit_price) * p.quantity AS gain_loss,
                ((s.price_per_stock - p.limit_price) / p.limit_price) * 100 AS gain_loss_percent
            FROM portfolio p
            JOIN stocks s ON p.symbol = s.symbol
            WHERE p.user_id = %s
            ORDER BY p.created_at DESC
        """
        cursor.execute(query, (user_id,))
        portfolio = cursor.fetchall()
        cursor.close()

        return jsonify({"success": True, "data": portfolio}), 200

    except Exception as e:
        print(f"Error fetching portfolio: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve portfolio"}), 500

@app.route('/api/exit', methods=['POST'])
def exit_stock():
    data = request.get_json()
    print("Received data:", data)  # Debug

    stock_id = data.get('stock_id')
    portfolio_id = data.get('portfolio_id')
    quantity = int(data.get('quantity', 0))
    user_id = session.get('user_id')

    print("User ID:", user_id)
    print("Stock ID:", stock_id)
    print("Portfolio ID:", portfolio_id)
    print("Exit Quantity:", quantity)

    if not user_id:
        return jsonify({"success": False, "message": "User not logged in"}), 401

    try:
        cursor = db.cursor(dictionary=True)

        # Fetch portfolio record
        cursor.execute("SELECT quantity FROM portfolio WHERE id = %s AND user_id = %s", (portfolio_id, user_id))
        result = cursor.fetchone()
        print("Portfolio lookup result:", result)

        if not result:
            return jsonify({"success": False, "message": "Portfolio not found"}), 404

        if result['quantity'] < quantity:
            return jsonify({"success": False, "message": "Not enough quantity"}), 400

        remaining_quantity = result['quantity'] - quantity
        if remaining_quantity > 0:
            cursor.execute(""" UPDATE portfolio SET quantity = %s, total_price = limit_price * %s WHERE id = %s """, (remaining_quantity, remaining_quantity, portfolio_id))
            print("Updated portfolio with new quantity and total_price:", remaining_quantity)

        else:
            cursor.execute("DELETE FROM portfolio WHERE id = %s", (portfolio_id,))
            print("Deleted portfolio entry because quantity became zero.")

        # Update stock total
        cursor.execute("UPDATE stocks SET total_stock = total_stock + %s WHERE id = %s", (quantity, stock_id))
        print("Updated stock total_stock")

        db.commit()
        return jsonify({"success": True}), 200

    except Exception as e:
        print("Exit error:", e)
        return jsonify({"success": False, "message": "Exit failed"}), 500

    finally:
        cursor.close()

      


# User Details fetch by admin

# ✅ Get all users with role = 'customer'
@app.route('/api/admin/users', methods=['GET'])
def get_users():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="stock_db"
    )
    cursor = db.cursor(dictionary=True)
    # cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT *
        FROM users 
        WHERE role = 'customer'
    """)
    users = cursor.fetchall()
    return jsonify(users)

# ✅ Delete user by ID
@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    delete_cursor = db.cursor(dictionary=True)
    delete_cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    db.commit()
    return jsonify({'message': 'User deleted successfully'})


# "New Portfolios Created Per Month"
# @app.route('/api/admin/user-activity', methods=['GET'])
# def user_activity():
#     db = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="",
#         database="stock_db"
#     )
#     cursor = db.cursor(dictionary=True)
#     query = """
#         SELECT
#           DATE_FORMAT(created_at, '%Y-%m') AS month,
#           COUNT(*) AS portfolios_created
#         FROM portfolio
#         GROUP BY month
#         ORDER BY month ASC;
#     """
#     cursor.execute(query)
#     result = cursor.fetchall()
#     cursor.close()
#     db.close()

#     return jsonify(result)

#  Overall portfolio quantity trend (total quantity per month across all users):

# # @app.route('/api/admin/portfolio-quantity-trends', methods=['GET'])
# # def portfolio_quantity_trends():
#     db = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="",
#         database="stock_db"
#     )
#     cursor = db.cursor(dictionary=True)
#     query = """
#         SELECT
#             DATE_FORMAT(created_at, '%Y-%m') AS month,
#             SUM(quantity) AS total_quantity
#         FROM portfolio
#         GROUP BY month
#         ORDER BY month ASC;
#     """
#     cursor.execute(query)
#     result = cursor.fetchall()
#     cursor.close()
#     db.close()
#     return jsonify(result)


#  Overall portfolio quantity trend (total quantity per month across selected users):
@app.route('/api/admin/selectUser', methods=['GET'])
def fetch_all_users():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="stock_db"
    )
    cursor = db.cursor(dictionary=True)
    query = "SELECT user_id, CONCAT(first_name, ' ', last_name) AS name FROM users WHERE role = 'customer';"
    cursor.execute(query)
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(users)

@app.route('/api/admin/portfolio-quantity-trends-by-user', methods=['GET'])
def portfolio_quantity_trends_by_user():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id query parameter required"}), 400

    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="stock_db"
    )
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT
            DATE_FORMAT(created_at, '%Y-%m-%D') AS month,
            quantity AS total_quantity
        FROM portfolio
        WHERE user_id = %s
        GROUP BY month
        ORDER BY month ASC;
    """
    cursor.execute(query, (user_id,))
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(result)








# @app.route('/api/portfolio', methods=['GET'])
# def get_portfolio():
    user_id = session.get('user_id')  # Ensure user is authenticated

    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    try:
        cursor = db.cursor(dictionary=True)

        query = """
            SELECT symbol, company_name, quantity, limit_price, total_price, created_at
            FROM portfolio
            WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        portfolio = cursor.fetchall()
        cursor.close()

        return jsonify({"success": True, "data": portfolio}), 200

    except Exception as e:
        print(f"Error fetching portfolio: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve portfolio"}), 500

# @app.route('/api/watchlist', methods=['POST'])
# def add_to_watchlist():
#     if 'user_id' not in session:
#         return jsonify({"error": "Unauthorized"}), 401

#     data = request.json
#     stock_id = data['stockId']
#     user_id = session['user_id']

#     cursor.execute("INSERT INTO watchlist (user_id, stock_id) VALUES (%s, %s)", (user_id, stock_id))
#     db.commit()
#     return jsonify({"message": "Added to watchlist"}), 201

# @app.route('/api/watchlist/<int:stock_id>', methods=['DELETE'])
# def remove_from_watchlist(stock_id):
#     if 'user_id' not in session:
#         return jsonify({"error": "Unauthorized"}), 401

#     user_id = session['user_id']
#     cursor.execute("DELETE FROM watchlist WHERE user_id = %s AND stock_id = %s", (user_id, stock_id))
#     db.commit()
#     return jsonify({"message": "Removed from watchlist"})

# @app.route('/api/watchlist', methods=['GET'])
# def get_watchlist():
#     if 'user_id' not in session:
#         return jsonify({"error": "Unauthorized"}), 401

#     user_id = session['user_id']
#     cursor.execute("""
#         SELECT s.id, s.symbol, s.company_name, s.total_stock, s.change
#         FROM stocks s
#         JOIN watchlist w ON s.id = w.stock_id
#         WHERE w.user_id = %s
#     """, (user_id,))
#     results = cursor.fetchall()
#     return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
