import sqlite3
from datetime import datetime, timedelta


# ========== TẠO DATABASE ==========
def create_database():
    """Tạo file database.db & các bảng"""

    conn = sqlite3.connect('metro_system.db')
    c = conn.cursor()

    print("🔨 Creating tables...")

    # ========== BẢNG 1: USERS ==========
    c.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            balance REAL DEFAULT 0,
            role TEXT DEFAULT 'CUSTOMER',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Users table created")

    # ========== BẢNG 2: ROUTES ==========
    c.execute('''
        CREATE TABLE IF NOT EXISTS Routes (
            route_id INTEGER PRIMARY KEY,
            route_name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Routes table created")

    # ========== BẢNG 3: STATIONS ==========
    c.execute('''
        CREATE TABLE IF NOT EXISTS Stations (
            station_id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_name TEXT NOT NULL,
            route_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(route_id) REFERENCES Routes(route_id)
        )
    ''')
    print("✅ Stations table created")

    # ========== BẢNG 4: TRAINS ==========
    c.execute('''
        CREATE TABLE IF NOT EXISTS Trains (
            train_id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            status TEXT DEFAULT 'SCHEDULED',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(route_id) REFERENCES Routes(route_id)
        )
    ''')
    print("✅ Trains table created")

    # ========== BẢNG 5: TICKETS ==========
    c.execute('''
        CREATE TABLE IF NOT EXISTS Tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            train_id INTEGER NOT NULL,
            from_station INTEGER NOT NULL,
            to_station INTEGER NOT NULL,
            ticket_type TEXT NOT NULL,
            price REAL NOT NULL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'VALID',
            used_date TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES Users(user_id),
            FOREIGN KEY(train_id) REFERENCES Trains(train_id),
            FOREIGN KEY(from_station) REFERENCES Stations(station_id),
            FOREIGN KEY(to_station) REFERENCES Stations(station_id)
        )
    ''')
    print("✅ Tickets table created")

    # ========== BẢNG 6: TICKET_PRICES ==========
    c.execute('''
        CREATE TABLE IF NOT EXISTS TicketPrices (
            route_id INTEGER NOT NULL,
            ticket_type TEXT NOT NULL,
            price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(route_id, ticket_type),
            FOREIGN KEY(route_id) REFERENCES Routes(route_id)
        )
    ''')
    print("✅ TicketPrices table created")

    # ========== BẢNG 7: TRANSACTIONS ==========
    c.execute('''
        CREATE TABLE IF NOT EXISTS Transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            ticket_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES Users(user_id),
            FOREIGN KEY(ticket_id) REFERENCES Tickets(ticket_id)
        )
    ''')
    print("✅ Transactions table created")

    conn.commit()
    return conn


# ========== INSERT DỮ LIỆU MẪU ==========
def insert_sample_data(conn):
    """Insert dữ liệu mẫu"""

    c = conn.cursor()

    print("\n📝 Inserting sample data...")

    # 1. Insert Users
    users = [
        ('user1', '123456', 'user1@email.com', 1000000, 'CUSTOMER'),
        ('user2', '123456', 'user2@email.com', 500000, 'CUSTOMER'),
        ('admin', 'admin123', 'admin@metro.com', 0, 'ADMIN'),
    ]

    for username, password, email, balance, role in users:
        try:
            c.execute(
                'INSERT INTO Users (username, password, email, balance, role) VALUES (?, ?, ?, ?, ?)',
                (username, password, email, balance, role)
            )
        except sqlite3.IntegrityError:
            print(f"  ⚠️  User {username} already exists")

    print("✅ Users inserted")

    # 2. Insert Routes
    routes = [
        (1, 'Tuyến 1: Ben Thanh - Kiến An'),
        (2, 'Tuyến 2: Sân Bay - Bến Tây'),
        (3, 'Tuyến 3: Bình Triệu - Kiến An'),
    ]

    for route_id, route_name in routes:
        try:
            c.execute(
                'INSERT INTO Routes (route_id, route_name) VALUES (?, ?)',
                (route_id, route_name)
            )
        except sqlite3.IntegrityError:
            print(f"  ⚠️  Route {route_id} already exists")

    print("✅ Routes inserted")

    # 3. Insert Stations for Route 1
    stations_route1 = [
        ('Ben Thanh', 1, 0),
        ('Bến Tây', 1, 1),
        ('Lê Văn Sỹ', 1, 2),
        ('Kiến An', 1, 3),
    ]

    for station_name, route_id, position in stations_route1:
        try:
            c.execute(
                'INSERT INTO Stations (station_name, route_id, position) VALUES (?, ?, ?)',
                (station_name, route_id, position)
            )
        except sqlite3.IntegrityError:
            print(f"  ⚠️  Station {station_name} already exists")

    # 4. Insert Stations for Route 2
    stations_route2 = [
        ('Sân Bay', 2, 0),
        ('Âu Cơ', 2, 1),
        ('Tân Bình', 2, 2),
        ('Bến Tây', 2, 3),
    ]

    for station_name, route_id, position in stations_route2:
        try:
            c.execute(
                'INSERT INTO Stations (station_name, route_id, position) VALUES (?, ?, ?)',
                (station_name, route_id, position)
            )
        except sqlite3.IntegrityError:
            print(f"  ⚠️  Station {station_name} already exists")

    print("✅ Stations inserted")

    # 5. Insert Trains
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    trains = [
        (1, today, '09:00', 100, 'SCHEDULED'),
        (1, today, '10:00', 100, 'SCHEDULED'),
        (1, today, '11:00', 100, 'SCHEDULED'),
        (2, today, '08:30', 150, 'SCHEDULED'),
        (2, today, '14:30', 150, 'SCHEDULED'),
        (1, tomorrow, '09:00', 100, 'SCHEDULED'),
    ]

    for route_id, date, departure_time, capacity, status in trains:
        try:
            c.execute(
                'INSERT INTO Trains (route_id, date, departure_time, capacity, status) VALUES (?, ?, ?, ?, ?)',
                (route_id, date, departure_time, capacity, status)
            )
        except sqlite3.IntegrityError:
            print(f"  ⚠️  Train already exists")

    print("✅ Trains inserted")

    # 6. Insert Ticket Prices
    prices = [
        (1, 'SINGLE', 30000),
        (1, 'MONTHLY', 500000),
        (1, 'CHILD', 15000),
        (2, 'SINGLE', 50000),
        (2, 'MONTHLY', 800000),
        (3, 'SINGLE', 35000),
    ]

    for route_id, ticket_type, price in prices:
        try:
            c.execute(
                'INSERT INTO TicketPrices (route_id, ticket_type, price) VALUES (?, ?, ?)',
                (route_id, ticket_type, price)
            )
        except sqlite3.IntegrityError:
            print(f"  ⚠️  Price for {ticket_type} on route {route_id} already exists")

    print("✅ Ticket prices inserted")

    conn.commit()


# ========== HIỂN THỊ DỮ LIỆU ==========
def display_data(conn):
    """Hiển thị dữ liệu vừa tạo"""

    c = conn.cursor()

    print("\n" + "=" * 50)
    print("📊 DATABASE STRUCTURE")
    print("=" * 50)

    # Users
    print("\n👤 USERS:")
    c.execute('SELECT user_id, username, balance, role FROM Users')
    for row in c.fetchall():
        print(f"  {row[0]}. {row[1]} - Balance: {row[2]:,} VND - Role: {row[3]}")

    # Routes
    print("\n🚇 ROUTES:")
    c.execute('SELECT * FROM Routes')
    for row in c.fetchall():
        print(f"  {row[0]}. {row[1]}")

    # Stations
    print("\n🚉 STATIONS:")
    c.execute(
        'SELECT s.station_name, r.route_name, s.position FROM Stations s JOIN Routes r ON s.route_id = r.route_id ORDER BY s.route_id, s.position')
    for row in c.fetchall():
        print(f"  {row[0]} (Route {row[1]}) - Position: {row[2]}")

    # Trains
    print("\n🚆 TRAINS:")
    c.execute(
        'SELECT t.train_id, r.route_name, t.date, t.departure_time, t.capacity FROM Trains t JOIN Routes r ON t.route_id = r.route_id LIMIT 5')
    for row in c.fetchall():
        print(f"  Train {row[0]}: {row[1]} - {row[2]} {row[3]} - Capacity: {row[4]}")

    # Prices
    print("\n💵 TICKET PRICES:")
    c.execute(
        'SELECT r.route_name, tp.ticket_type, tp.price FROM TicketPrices tp JOIN Routes r ON tp.route_id = r.route_id')
    for row in c.fetchall():
        print(f"  {row[0]} - {row[1]}: {row[2]:,} VND")


# ========== MAIN ==========
if __name__ == '__main__':
    print("🚇 METRO TICKETING SYSTEM - DATABASE SETUP\n")

    # Tạo database
    conn = create_database()

    # Insert dữ liệu mẫu
    insert_sample_data(conn)

    # Hiển thị dữ liệu
    display_data(conn)

    conn.close()

    print("\n" + "=" * 50)
    print("✅ Database 'metro_system.db' created successfully!")
    print("=" * 50)