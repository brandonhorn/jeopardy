import pandas as pd
import pyodbc
import struct
from azure.identity import DefaultAzureCredential

class sql_client:
    def __init__(self):
        self.server = 'jstore.database.windows.net'
        self.database = 'jstore'
        self.question_table_name = 'questions'
        self.player_table_name = 'players'
        self.player_misses_table_name = 'player_misses'
        self.connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};"
        credential = DefaultAzureCredential()
        self.token = credential.get_token("https://database.windows.net/").token
        exptoken = b""
        for i in bytes(self.token, "UTF-8"):
            exptoken += bytes({i})
            exptoken += bytes(1)
        tokenstruct = struct.pack("=i", len(exptoken)) + exptoken
    
    def _connect(self):
        # Connect to the database
        credential = DefaultAzureCredential()
        self.token = credential.get_token("https://database.windows.net/").token
        exptoken = b""
        for i in bytes(self.token, "UTF-8"):
            exptoken += bytes({i})
            exptoken += bytes(1)
        tokenstruct = struct.pack("=i", len(exptoken)) + exptoken
        conn = pyodbc.connect(self.connection_string, attrs_before={1256: tokenstruct})
        return conn

    def upload(self, df):
        # Upload the DataFrame to the 'questions' table
        conn = self._connect()
        cursor = conn.cursor()

        # Create table if it doesn't exist
        self.cursor = cursor.execute(f"""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{self.question_table_name}' AND xtype='U')
        CREATE TABLE {self.question_table_name} (
            Id INT PRIMARY KEY,
            Category NVARCHAR(MAX),
            Question NVARCHAR(MAX),
            Value INT,
            Answer NVARCHAR(MAX)
        )
        """)

        # Insert data into the table
        for _, row in df.iterrows():
            cursor.execute(f"""
            INSERT INTO {self.question_table_name} (Id, Category, Question, Value, Answer)
            VALUES (?, ?, ?, ?, ?)
            """, row['Index'], row['Category'], row['Question'], row['Value'], row['Answer'])

        # Commit the transaction
        conn.commit()
        conn.close()

    def get_question(self, id):
        # Connect to the database
        conn = self._connect()
        cursor = conn.cursor()

        # Fetch a random question
        cursor = cursor.execute(f"SELECT TOP 1 * FROM {self.question_table_name} WHERE Id = ?", id)
        row = cursor.fetchone()

        # Close the connection
        conn.close()

        return {
            'Id': row.Id,
            'Category': row.Category,
            'Question': row.Question,
            'Value': row.Value,
            'Answer': row.Answer
        }
    
    def create_player(self, user_id):
        # Connect to the database
        conn = self._connect()
        cursor = conn.cursor()

        # Create Player table if it doesn't exist
        cursor.execute(f"""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{self.player_table_name}' AND xtype='U')
        CREATE TABLE {self.player_table_name} (
            User_ID INT PRIMARY KEY,
            a200_score INT,
            a400_score INT,
            a600_score INT,
            a800_score INT,
            a1000_score INT,
            a1200_score INT,
            a1600_score INT,
            a2000_score INT,
            a200_count INT,
            a400_count INT,
            a600_count INT,
            a800_count INT,
            a1000_count INT,
            a1200_count INT,
            a1600_count INT,
            a2000_count INT
        )
        """)

        # Create a new player
        cursor.execute(f"INSERT INTO {self.player_table_name} (User_ID, a200_score, a400_score, a600_score, a800_score, a1000_score, a1200_score, a1600_score, a2000_score, a200_count, a400_count, a600_count, a800_count, a1000_count, a1200_count, a1600_count, a2000_count) VALUES (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)")
        cursor.commit
        cursor.close()
        conn.close()

    def create_player_misses(self):
        # Connect to the database
        conn = self._connect()
        cursor = conn.cursor()

        # Create Player table if it doesn't exist
        cursor.execute(f"""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{self.player_misses_table_name}' AND xtype='U')
        CREATE TABLE {self.player_misses_table_name} (
            User_ID INT,
            Clue_ID INT,
            FOREIGN KEY (User_ID) REFERENCES {self.player_table_name}(User_ID),
            FOREIGN KEY (Clue_ID) REFERENCES {self.question_table_name}(Id)
        )
        """)
        cursor.commit()
        conn.close()

    
    def update_player(self, user_id, clue_id, value, correct):
        # Connect to the database
        conn = self._connect()
        cursor = conn.cursor()

        points = correct * value
        score_column_name = f"a{value}_score"
        count_column_name = f"a{value}_count"
        # Update the player's score
        cursor = cursor.execute(f"""UPDATE {self.player_table_name}
                            SET {score_column_name} = {score_column_name} + ?,
                                {count_column_name} = {count_column_name} + 1
                              WHERE User_ID = ?
                       """, (points, user_id))
        conn.commit()
        if correct != 1:
            # Insert the player's miss
            cursor = cursor.execute(f"INSERT INTO {self.player_misses_table_name} (User_ID, Clue_ID) VALUES (?, ?)", (user_id, clue_id))
            conn.commit()
        # Close the connection
        cursor.close()
        conn.close()

    def get_player_coryat_score(self, user_id):
        # Connect to the database
        conn = self._connect()
        cursor = conn.cursor()

        # Fetch all the player's scores and counts
        cursor.execute(f"SELECT * FROM {self.player_table_name} WHERE User_ID = ?", user_id)
        row = cursor.fetchone()
        # normalize the score by dividing by the count, where the count is 8 columns greater than the score index
        score = 0
        for i in range(1, 9):
            int_score = row[i] / row[i + 8]
            if i in [2,4]:
                int_score *= 2
            score += (int_score* 6)


        # Close the connection
        conn.close()

        print(score)
        return score