from celery import Celery
from model.models import Session, Company
from config.development import BROKER_URL
import json

app = Celery('tasks', broker=BROKER_URL)

@app.task
def save_chunk(chunk_data, chunk_number, total_chunks):
    global session
    session = Session()

    try:
        reader = json.loads(chunk_data)

        for row in reader:
            sql_data = Company(
                name=row.get('name', ""),  # Use empty string as default
                domain=row.get('domain', ""),
                year_founded=row.get('year founded', ""),
                industry=row.get('industry', ""),
                size_range=row.get('size range', ""),
                locality=row.get('locality', ""),
                country=row.get('country', ""),
                linkedin_url=row.get('linkedin url', ""),
                current_employee_estimate=row.get('current employee estimate', 0),  # Default to 0
                total_employee_estimate=row.get('total employee estimate', 0)  # Default to 0
            )
            
           
            session.add(sql_data)

        session.commit()

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()  
    finally:
        session.close()  

    # Check if this is the last chunk
    if chunk_number == total_chunks:
        print(f"All chunks for received. Processing the file.")

