from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests
from models import Food, UserLog

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lifenutrition.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Function to convert height from feet and inches to centimeters
def convert_height_to_cm(feet, inches):
    total_inches = feet * 12 + inches
    height_cm = total_inches * 2.54
    return height_cm

# Function to convert weight from pounds to kilograms
def convert_weight_to_kg(weight_lbs):
    weight_kg = weight_lbs * 0.453592
    return weight_kg

def calculate_calorie_intake(weight, height, age, gender, activity_level):
    # Calculate basal metabolic rate (BMR)
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # Adjust BMR based on activity level
    if activity_level == 'sedentary':
        calorie_intake = bmr * 1.2
    elif activity_level == 'lightly_active':
        calorie_intake = bmr * 1.375
    elif activity_level == 'moderately_active':
        calorie_intake = bmr * 1.55
    elif activity_level == 'very_active':
        calorie_intake = bmr * 1.725
    else:
        calorie_intake = bmr * 1.9

    return round(calorie_intake)

def calculate_macronutrient_distribution(calorie_intake, goal, weight_kg):
    # Calculate protein and fat based on goal
    if goal == 'maintain':
        protein = weight_kg * 2.2
        fat = weight_kg * 0.9
    elif goal == 'lose':
        protein = weight_kg * 2.5
        fat = weight_kg * 0.8
    elif goal == 'gain':
        protein = weight_kg * 1.8
        fat = weight_kg * 1.1
    else:
        protein = weight_kg * 2.0
        fat = weight_kg * 1.0

    # Calculate remaining calories for carbohydrates
    remaining_calories = calorie_intake - (protein * 4) - (fat * 9)
    carbs = remaining_calories / 4

    # Round the values to the nearest whole numbers
    protein = round(protein)
    fat = round(fat)
    carbs = round(carbs)

    # Round the calories to the nearest whole number
    calories = round(calorie_intake)


    return protein, fat, carbs, calories


# Define the Food model
class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    protein = db.Column(db.Float)
    fat = db.Column(db.Float)
    carbohydrates = db.Column(db.Float)
    calories = db.Column(db.Integer)
    portion_sizes = db.Column(db.String(255))

# Define the UserLog model
class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('food.id'), nullable=False)
    meal_section = db.Column(db.String(50))
    portion_size = db.Column(db.Float)

def recommend_food(user_id):
    user_logs = UserLog.query.filter_by(user_id=user_id).all()
    goal_calories = sum(log.food.calories for log in user_logs)
    goal_protein = sum(log.food.protein for log in user_logs)
    goal_fat = sum(log.food.fat for log in user_logs)
    goal_carbohydrates = sum(log.food.carbohydrates for log in user_logs)

    logged_foods = UserLog.query.filter_by(user_id=user_id).all()
    logged_calories = sum(log.food.calories for log in logged_foods)
    logged_protein = sum(log.food.protein for log in logged_foods)
    logged_fat = sum(log.food.fat for log in logged_foods)
    logged_carbohydrates = sum(log.food.carbohydrates for log in logged_foods)

    remaining_calories = goal_calories - logged_calories
    remaining_protein = goal_protein - logged_protein
    remaining_fat = goal_fat - logged_fat
    remaining_carbohydrates = goal_carbohydrates - logged_carbohydrates

    print("Remaining Calories:", remaining_calories)
    print("Remaining Protein:", remaining_protein)
    print("Remaining Fat:", remaining_fat)
    print("Remaining Carbohydrates:", remaining_carbohydrates)

    recommended_foods = Food.query.filter(
        (Food.calories <= remaining_calories) |
        (Food.protein <= remaining_protein) |
        (Food.fat <= remaining_fat) |
        (Food.carbohydrates <= remaining_carbohydrates)
    ).all()

    recommendation_scores = []
    for food in recommended_foods:
        score = (
            (remaining_calories - food.calories) ** 2 +
            (remaining_protein - food.protein) ** 2 +
            (remaining_fat - food.fat) ** 2 +
            (remaining_carbohydrates - food.carbohydrates) ** 2
        )
        recommendation_scores.append((food, score))

    recommendation_scores.sort(key=lambda x: x[1])  # Sort by score ascending

    sorted_foods = [food for food, _ in recommendation_scores]

    # Normalize the scores
    max_score = recommendation_scores[-1][1]
    recommendation_scores = [(food, score / max_score * 100) for food, score in recommendation_scores]

    return sorted_foods, recommendation_scores


@app.route('/recommendations', methods=['POST'])
def recommend():
    # Get the user ID (replace this with your actual user identification logic)
    user_id = 1  # Replace this with the logic to retrieve or create the user ID

    # Call the recommend_food function to get the recommended foods and scores
    recommended_foods, recommendation_scores = recommend_food(user_id)

    # Render the recommend.html template and pass the recommended foods and scores
    return render_template('recommend.html', recommended_foods=recommended_foods, recommendation_scores=recommendation_scores)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    name = request.form['name']
    age = int(request.form['age'])
    gender = request.form['gender']
    weight_lbs = float(request.form['weight'])
    feet = int(request.form['feet'])
    inches = int(request.form['inches'])
    activity_level = request.form['activity_level']
    goal = request.form['goal']

    # Convert height to centimeters
    height_cm = convert_height_to_cm(feet, inches)

    # Convert weight to kilograms
    weight_kg = convert_weight_to_kg(weight_lbs)

    # Calculate calorie intake
    calorie_intake = calculate_calorie_intake(weight_kg, height_cm, age, gender, activity_level)

    # Calculate macronutrient distribution
    protein, fat, carbs, calories = calculate_macronutrient_distribution(calorie_intake, goal, weight_kg)

    # Get user ID or create a new user
    user_id = 1  # Replace this with actual user ID retrieval or creation logic

    # Get recommended food items
    recommended_foods = recommend_food(user_id)

    return render_template('result.html', name=name, calorie_intake=calorie_intake, protein=protein, fat=fat, carbs=carbs, recommended_foods=recommended_foods)


@app.route('/log_food', methods=['POST'])
def log_food():
    # Retrieve the food log data from the form
    food = request.form['food']
    portion = request.form['portion']

    # Make the API request to the USDA Food Composition Databases
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food}&api_key=pknF7XDZZIaTJhFOVfk9but4xXmViBLagjkIgRuz"
    response = requests.get(url)
    data = response.json()

    # Extract the nutritional information from the API response
    if 'foods' in data and len(data['foods']) > 0:
        food_data = data['foods'][0]
        nutrients = food_data['foodNutrients']

        # Find the specific nutrient values by their nutrient IDs
        protein = next((nutrient['value'] for nutrient in nutrients if nutrient['nutrientId'] == 1003), 0)
        fat = next((nutrient['value'] for nutrient in nutrients if nutrient['nutrientId'] == 1004), 0)
        carbohydrates = next((nutrient['value'] for nutrient in nutrients if nutrient['nutrientId'] == 1005), 0)

        # Calculate the calorie value based on protein, fat, and carbohydrates
        calories = protein * 4 + fat * 9 + carbohydrates * 4

        # Round the calories to the nearest whole number
        calories = int(round(calories))
    else:
        # Handle the case when the food item is not found
        protein = 0
        fat = 0
        carbohydrates = 0
        calories = 0

    # Create a new Food log entry in the database
    food_entry = Food(name=food, protein=protein, fat=fat, carbohydrates=carbohydrates, calories=calories, portion_sizes=portion)
    db.session.add(food_entry)
    db.session.commit()

    return redirect(url_for('foodlog'))

@app.route('/recommendations', methods=['GET'])
def recommendations():
    user_id = 1  # Replace this with actual user ID retrieval or creation logic
    return redirect(url_for('recommend', user_id=user_id))

@app.route('/foodlog')
def foodlog():
    # Retrieve all food entries from the database
    food_entries = Food.query.all()
    return render_template('foodlog.html', food_entries=food_entries)

@app.route('/clear_log', methods=['POST'])
def clear_log():
    # Clear all food entries from the database
    Food.query.delete()
    db.session.commit()

    # Redirect back to the food log page
    return redirect(url_for('foodlog'))

if __name__ == '__main__':
    app.run(debug=True)