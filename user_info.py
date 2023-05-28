# Function to convert height from feet and inches to centimeters
def convert_height_to_cm(feet, inches):
    total_inches = feet * 12 + inches
    height_cm = total_inches * 2.54
    return height_cm

# Function to convert weight from pounds to kilograms
def convert_weight_to_kg(pounds):
    weight_kg = pounds * 0.45359237
    return weight_kg

# Function to calculate recommended calorie intake based on BMR (Basal Metabolic Rate)
def calculate_calorie_intake(weight, height, age, gender, activity_level):
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    activity_factors = {
        'sedentary': 1.2,
        'lightly active': 1.375,
        'moderately active': 1.55,
        'very active': 1.725,
        'extra active': 1.9
    }
    calorie_intake = bmr * activity_factors[activity_level]
    return calorie_intake

# Function to calculate recommended macronutrient distribution
def calculate_macronutrient_distribution(calorie_intake, goal, weight_kg):
    if goal == 'weight loss':
        protein = 1.2 * weight_kg
        fat = 0.25 * calorie_intake / 9
        carbs = (calorie_intake - ((protein * 4) + (fat * 9))) / 4
    elif goal == 'muscle gain':
        protein = 1.6 * weight_kg
        fat = 0.25 * calorie_intake / 9
        carbs = (calorie_intake - ((protein * 4) + (fat * 9))) / 4
    else:
        protein = 0.8 * weight_kg
        fat = 0.3 * calorie_intake / 9
        carbs = (calorie_intake - ((protein * 4) + (fat * 9))) / 4
    
    return protein, fat, carbs

# Prompt user for information
name = input("Enter your name: ")
age = int(input("Enter your age: "))
gender = input("Enter your gender (male/female): ")
weight_lbs = float(input("Enter your weight in lbs: "))
feet = int(input("Enter your height in feet: "))
inches = int(input("Enter the remaining inches: "))
activity_level = input("Enter your activity level (sedentary/lightly active/moderately active/very active/extra active): ")
goal = input("Enter your goal (weight loss/muscle gain/general health): ")

# Convert height to centimeters
height_cm = convert_height_to_cm(feet, inches)

# Convert weight to kilograms
weight_kg = convert_weight_to_kg(weight_lbs)

# Calculate calorie intake
calorie_intake = calculate_calorie_intake(weight_kg, height_cm, age, gender, activity_level)

# Calculate macronutrient distribution
protein, fat, carbs = calculate_macronutrient_distribution(calorie_intake, goal, weight_kg)

# Print recommended information
print("\nRecommended daily calorie intake:", calorie_intake)
print("Macronutrient distribution:")
print("Protein:", protein, "grams")
print("Fat:", fat, "grams")
print("Carbs:", carbs, "grams")