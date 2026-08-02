import serpapi
import json

client = serpapi.Client(api_key="ee20eacab05ccd6f05fae6a3cecdc8f0b6a432a7cb164569e73a74b059c90a8e")
results = client.search({
  "engine": "google_trends",
  "q": "AAPL",
  "date": "today 12-m",
  "tz": "420",
  "data_type": "TIMESERIES"
})
interest_over_time = results["interest_over_time"]
print(interest_over_time)

# Save the dictionary to a file
with open("data.json", "w") as file:
    json.dump(interest_over_time, file, indent=4)