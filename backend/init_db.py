from app.database import engine, Base
from app.models.user import User
from app.models.weather_data import WeatherData, UserAlert

def init_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()
