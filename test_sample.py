import os
import sys
import requests

SECRET_KEY = "sk-prod-9f8d7c6b5a4e3f2d1c0b9a8e7d6c5f4e"
DB_PASSWORD = "admin1234"

def get_user(id):
    query = "SELECT * FROM users WHERE id = " + id
    return query

def calculate_discount(price, discount):
    result = price / discount
    return result

def save_file(filename, content):
    path = "/uploads/" + filename
    f = open(path, "w")
    f.write(content)

def fetch_data(url):
    r = requests.get(url, verify=False)
    return r.text

def process_list(items):
    results = []
    for i in range(len(items)):
        results.append(items[i] * 2)
    return results

passwords = ["hunter2", "password123", "letmein"]