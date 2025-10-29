import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

class PostgreSQLConnection:
    def __init__(self):
        self.conn = None
        self.max_retries = 5
        self.retry_delay = 5
        self.connect_with_retry()
    
    def connect_with_retry(self):
        """Create PostgreSQL connection with retry logic"""
        for attempt in range(self.max_retries):
            try:
                self.conn = psycopg2.connect(
                    host=os.getenv('DB_HOST', 'localhost'),
                    database=os.getenv('DB_NAME', 'hospital_db'),
                    user=os.getenv('DB_USER', 'user'),
                    password=os.getenv('DB_PASSWORD', 'password'),
                    port=os.getenv('DB_PORT', '5432'),
                    connect_timeout=10
                )
                # Set to return dictionaries
                self.conn.cursor_factory = RealDictCursor
                print("✅ PostgreSQL connection established successfully")
                return
            except Exception as e:
                print(f"❌ Database connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print("Max retries reached. Could not connect to database.")
                    raise e
    
    def execute(self, query, params=None):
        """Execute query with SQLite to PostgreSQL parameter conversion"""
        # Convert SQLite ? placeholders to PostgreSQL %s
        if '?' in query:
            query = query.replace('?', '%s')
        
        cur = self.conn.cursor()
        try:
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            
            # For SELECT queries, return results
            if query.strip().upper().startswith('SELECT'):
                return cur
            else:
                # For INSERT/UPDATE/DELETE, return self for method chaining
                return self
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def fetchall(self):
        """Fetch all results"""
        return self.conn.cursor().fetchall()
    
    def fetchone(self):
        """Fetch one result"""
        return self.conn.cursor().fetchone()
    
    @property
    def lastrowid(self):
        """Get last inserted row ID"""
        cur = self.conn.cursor()
        cur.execute("SELECT LASTVAL()")
        return cur.fetchone()['lastval']
    
    def commit(self):
        """Commit transaction"""
        self.conn.commit()
    
    def close(self):
        """Close connection"""
        if self.conn:
            self.conn.close()

# Create global connection instance (but don't initialize immediately)
conn = None

def get_db_connection():
    """Get database connection with lazy initialization"""
    global conn
    if conn is None:
        conn = PostgreSQLConnection()
    return conn

def init_database():
    """Initialize database tables"""
    global conn
    try:
        if conn is None:
            conn = PostgreSQLConnection()
        
        # Create tables if they don't exist
        conn.execute('''CREATE TABLE IF NOT EXISTS patient
            (pat_id SERIAL PRIMARY KEY,
            pat_first_name TEXT NOT NULL,
            pat_last_name TEXT NOT NULL,
            pat_insurance_no TEXT NOT NULL,
            pat_ph_no TEXT NOT NULL,
            pat_date DATE DEFAULT CURRENT_DATE,
            pat_address TEXT NOT NULL)''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS doctor
            (doc_id SERIAL PRIMARY KEY,
            doc_first_name TEXT NOT NULL,
            doc_last_name TEXT NOT NULL,
            doc_ph_no TEXT NOT NULL,
            doc_date DATE DEFAULT CURRENT_DATE,
            doc_address TEXT NOT NULL)''')
        
        # ... (rest of your table creation queries remain the same)
        
        conn.commit()
        print("✅ PostgreSQL database initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        if conn:
            conn.conn.rollback()

# Don't auto-initialize database on import anymore
# init_database()