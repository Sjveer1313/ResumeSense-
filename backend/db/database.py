"""
Database connection and setup for ResumeSense.
Uses MySQL with pymysql connector.
"""
import pymysql
from pymysql.cursors import DictCursor
from backend.config import Config
import json


class Database:
    """Database connection and operations"""
    
    def __init__(self):
        """Initialize database connection"""
        self.connection = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.connection = pymysql.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                cursorclass=DictCursor,
                charset='utf8mb4'
            )
            print("Database connection established")
        except pymysql.Error as e:
            print(f"Error connecting to database: {e}")
            # Try to create database if it doesn't exist
            try:
                temp_conn = pymysql.connect(
                    host=Config.MYSQL_HOST,
                    port=Config.MYSQL_PORT,
                    user=Config.MYSQL_USER,
                    password=Config.MYSQL_PASSWORD,
                    cursorclass=DictCursor
                )
                with temp_conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE}")
                temp_conn.close()
                # Retry connection
                self.connection = pymysql.connect(
                    host=Config.MYSQL_HOST,
                    port=Config.MYSQL_PORT,
                    user=Config.MYSQL_USER,
                    password=Config.MYSQL_PASSWORD,
                    database=Config.MYSQL_DATABASE,
                    cursorclass=DictCursor,
                    charset='utf8mb4'
                )
                print("Database created and connection established")
            except Exception as e2:
                print(f"Error creating database: {e2}")
                raise
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            with self.connection.cursor() as cursor:
                # Create resumes table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS resumes (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        resume_text TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """)
                
                # Create jobs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        job_description TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create analysis_results table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        resume_id INT NOT NULL,
                        job_id INT,
                        match_score DECIMAL(5,2),
                        ats_score DECIMAL(5,2),
                        quality_score DECIMAL(5,2),
                        ats_flags JSON,
                        power_verb_suggestions JSON,
                        match_details JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE,
                        FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE SET NULL
                    )
                """)
                
                self.connection.commit()
                print("Database tables created/verified")
        except Exception as e:
            print(f"Error creating tables: {e}")
            self.connection.rollback()
    
    def insert_resume(self, resume_text: str) -> int:
        """
        Insert a new resume into the database.
        
        Args:
            resume_text: Resume text content
            
        Returns:
            ID of inserted resume
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO resumes (resume_text) VALUES (%s)",
                    (resume_text,)
                )
                self.connection.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error inserting resume: {e}")
            self.connection.rollback()
            raise
    
    def insert_job(self, job_description: str) -> int:
        """
        Insert a new job description into the database.
        
        Args:
            job_description: Job description text
            
        Returns:
            ID of inserted job
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO jobs (job_description) VALUES (%s)",
                    (job_description,)
                )
                self.connection.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error inserting job: {e}")
            self.connection.rollback()
            raise
    
    def insert_analysis_result(self, resume_id: int, job_id: int = None,
                              match_score: float = None, ats_score: float = None,
                              quality_score: float = None, ats_flags: dict = None,
                              power_verb_suggestions: list = None,
                              match_details: dict = None) -> int:
        """
        Insert analysis result into the database.
        
        Args:
            resume_id: ID of the resume
            job_id: ID of the job (optional)
            match_score: JD-Resume match score
            ats_score: ATS compliance score
            quality_score: ML quality score
            ats_flags: ATS compliance flags
            power_verb_suggestions: Power verb suggestions
            match_details: JD match details
            
        Returns:
            ID of inserted analysis result
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO analysis_results 
                    (resume_id, job_id, match_score, ats_score, quality_score,
                     ats_flags, power_verb_suggestions, match_details)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    resume_id,
                    job_id,
                    match_score,
                    ats_score,
                    quality_score,
                    json.dumps(ats_flags) if ats_flags else None,
                    json.dumps(power_verb_suggestions) if power_verb_suggestions else None,
                    json.dumps(match_details) if match_details else None
                ))
                self.connection.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error inserting analysis result: {e}")
            self.connection.rollback()
            raise
    
    def get_resume(self, resume_id: int) -> dict:
        """
        Get resume by ID.
        
        Args:
            resume_id: Resume ID
            
        Returns:
            Resume dictionary or None
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM resumes WHERE id = %s",
                    (resume_id,)
                )
                return cursor.fetchone()
        except Exception as e:
            print(f"Error getting resume: {e}")
            return None
    
    def get_analysis_history(self, limit: int = 20) -> list:
        """
        Get analysis history.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of analysis results
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ar.id,
                        ar.resume_id,
                        ar.job_id,
                        ar.match_score,
                        ar.ats_score,
                        ar.quality_score,
                        ar.ats_flags,
                        ar.power_verb_suggestions,
                        ar.match_details,
                        ar.created_at,
                        r.resume_text,
                        j.job_description
                    FROM analysis_results ar
                    LEFT JOIN resumes r ON ar.resume_id = r.id
                    LEFT JOIN jobs j ON ar.job_id = j.id
                    ORDER BY ar.created_at DESC
                    LIMIT %s
                """, (limit,))
                results = cursor.fetchall()
                
                # Parse JSON fields
                for result in results:
                    if result.get('ats_flags'):
                        result['ats_flags'] = json.loads(result['ats_flags'])
                    if result.get('power_verb_suggestions'):
                        result['power_verb_suggestions'] = json.loads(result['power_verb_suggestions'])
                    if result.get('match_details'):
                        result['match_details'] = json.loads(result['match_details'])
                
                return results
        except Exception as e:
            print(f"Error getting analysis history: {e}")
            return []
    
    def get_analysis_result(self, result_id: int) -> dict:
        """
        Get analysis result by ID.
        
        Args:
            result_id: Analysis result ID
            
        Returns:
            Analysis result dictionary or None
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ar.*,
                        r.resume_text,
                        j.job_description
                    FROM analysis_results ar
                    LEFT JOIN resumes r ON ar.resume_id = r.id
                    LEFT JOIN jobs j ON ar.job_id = j.id
                    WHERE ar.id = %s
                """, (result_id,))
                result = cursor.fetchone()
                
                if result:
                    # Parse JSON fields
                    if result.get('ats_flags'):
                        result['ats_flags'] = json.loads(result['ats_flags'])
                    if result.get('power_verb_suggestions'):
                        result['power_verb_suggestions'] = json.loads(result['power_verb_suggestions'])
                    if result.get('match_details'):
                        result['match_details'] = json.loads(result['match_details'])
                
                return result
        except Exception as e:
            print(f"Error getting analysis result: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")


