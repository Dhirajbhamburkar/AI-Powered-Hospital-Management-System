import pandas as pd
from sklearn.linear_model import LinearRegression

# sample data
data = {
    'day': [1,2,3,4,5,6,7],
    'patients': [50,60,55,70,65,80,90]
}

df = pd.DataFrame(data)

X = df[['day']]
y = df['patients']

model = LinearRegression()
model.fit(X, y)

# prediction
print("Next day patients:", model.predict([[8]]))