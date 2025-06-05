import sys
import random
import json
from uuid import uuid4

# Data Models

CITY_FEATURES = ["port", "university", "factory", "park", "museum", "power plant"]

class Law:
    def __init__(self, title, description, impact):
        self.id = str(uuid4())
        self.title = title
        self.description = description
        self.impact = impact  # e.g. {'crime': -2, 'happiness': +1}

class City:
    def __init__(self, name, population=1000, features=None, economy=50, crime=10, happiness=50):
        self.id = str(uuid4())
        self.name = name
        self.population = population
        self.economy = economy  # 0-100
        self.crime = crime      # 0-100
        self.happiness = happiness  # 0-100
        self.features = features if features else []

    def yearly_update(self, law_effects):
        # Apply law effects
        for k, v in law_effects.items():
            if hasattr(self, k):
                setattr(self, k, max(0, min(100, getattr(self, k) + v)))

        # Economic growth
        econ_growth = random.randint(0, 2)
        self.economy = min(100, self.economy + econ_growth)

        # Happiness and crime random drift
        self.happiness = max(0, min(100, self.happiness + random.randint(-1, 2)))
        self.crime = max(0, min(100, self.crime + random.randint(-1, 1)))

        # Population growth
        growth = int(self.population * (0.01 + self.economy/1000 - self.crime/2000))
        self.population = max(0, self.population + growth)

class Event:
    def __init__(self, description, effect, year):
        self.id = str(uuid4())
        self.description = description
        self.effect = effect  # e.g. {'food': +100, 'money': -200}
        self.year = year

class Country:
    def __init__(self, name="Civica"):
        self.name = name
        self.description = "A personal, evolving fictional nation."
        self.population = 10000
        self.cities = []
        self.laws = []
        self.events = []
        self.year = 1 # <- Start at year 1!
        self.resources = {"food": 5000, "money": 10000, "tech": 500, "reputation": 50}

    def status(self):
        print(f"\n==== {self.name} - Year {self.year} ====")
        print(f"Description: {self.description}")
        print(f"Total Population: {self.population}")
        print(f"Resources: {self.resources}")
        print(f"Cities:")
        for city in self.cities:
            print(f" - {city.name} | Pop: {city.population} | Econ: {city.economy} | Crime: {city.crime} | Happy: {city.happiness} | Features: {', '.join(city.features)}")
        print(f"Laws: {[law.title for law in self.laws]}")
        print(f"Recent Events: {[event.description for event in self.events[-3:]]}")
        print("="*34 + "\n")

    def add_city(self, name, population=1000, features=None):
        if features is None:
            features = []
        city = City(name, population, features)
        self.cities.append(city)
        self.population += population
        print(f"Added city: {city.name} (Population: {city.population})")

    def add_law(self, title, description, impact):
        law = Law(title, description, impact)
        self.laws.append(law)
        print(f"Enacted law: {law.title}")

    def add_event(self, description, effect):
        event = Event(description, effect, self.year)
        self.events.append(event)
        # Apply effect
        for k, v in effect.items():
            if k in self.resources:
                self.resources[k] += v
        print(f"Event occurred: {event.description}")

    def simulate_tick(self):
        print(f"\nSimulating year {self.year}...")

        # Calculate cumulative law effects
        law_effects = {"crime": 0, "happiness": 0}
        for law in self.laws:
            for k, v in law.impact.items():
                if k in law_effects:
                    law_effects[k] += v

        # Update cities
        total_population = 0
        for city in self.cities:
            city.yearly_update(law_effects)
            total_population += city.population

        self.population = total_population if self.cities else self.population

        # National resources change
        food_produced = sum([city.economy for city in self.cities]) * 5
        food_consumed = self.population // 2
        self.resources["food"] += food_produced - food_consumed
        self.resources["money"] += random.randint(-500, 900)
        self.resources["tech"] += random.randint(0, 30)
        self.resources["reputation"] = max(0, min(100, self.resources["reputation"] + random.randint(-2, 3)))

        # Random event
        if random.random() < 0.3:
            event_type = random.choice(["good", "bad"])
            if event_type == "good":
                evt = Event(
                    "A scientific breakthrough boosts tech!",
                    {"tech": 100, "reputation": 5},
                    self.year
                )
                self.resources["tech"] += 100
                self.resources["reputation"] += 5
                self.events.append(evt)
                print(f"Event: {evt.description}")
            else:
                evt = Event(
                    "A crop blight reduces food stores!",
                    {"food": -300},
                    self.year
                )
                self.resources["food"] -= 300
                self.events.append(evt)
                print(f"Event: {evt.description}")

        # Check for starvation
        if self.resources["food"] < 0:
            lost = min(self.population // 10, self.population)
            self.population -= lost
            print("Starvation! Population decreased by", lost)
            self.resources["food"] = 0
            evt = Event(
                "Starvation strikes the nation!",
                {},
                self.year
            )
            self.events.append(evt)

        # Year advance
        self.year += 1
        print(f"Year {self.year - 1} complete.")
        self.status()

    def save(self, filename):
        data = {
            "name": self.name,
            "description": self.description,
            "population": self.population,
            "year": self.year,
            "resources": self.resources,
            "cities": [
                {
                    "id": c.id, "name": c.name, "population": c.population,
                    "economy": c.economy, "crime": c.crime,
                    "happiness": c.happiness, "features": c.features
                }
                for c in self.cities
            ],
            "laws": [
                {"id": l.id, "title": l.title, "description": l.description, "impact": l.impact}
                for l in self.laws
            ],
            "events": [
                {"id": e.id, "description": e.description, "effect": e.effect, "year": e.year}
                for e in self.events
            ]
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved nation to {filename}")

    def load(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)
        self.name = data["name"]
        self.description = data["description"]
        self.population = data["population"]
        self.year = data["year"]
        self.resources = data["resources"]
        self.cities = [
            City(
                name=c["name"], population=c["population"],
                features=c["features"], economy=c["economy"],
                crime=c["crime"], happiness=c["happiness"]
            )
            for c in data["cities"]
        ]
        self.laws = [
            Law(title=l["title"], description=l["description"], impact=l["impact"])
            for l in data["laws"]
        ]
        self.events = [
            Event(description=e["description"], effect=e["effect"], year=e["year"])
            for e in data["events"]
        ]
        print(f"Loaded nation from {filename}")

def menu():
    print("Choose an action:")
    print("1. View country status")
    print("2. Add city")
    print("3. Add law")
    print("4. Add event")
    print("5. Simulate one year")
    print("6. Save nation")
    print("7. Load nation")
    print("8. Quit")

def main():
    country = Country()

    while True:
        menu()
        choice = input("Enter choice (1-8): ").strip()
        if choice == "1":
            country.status()
        elif choice == "2":
            name = input("City name: ")
            population = input("Population (default 1000): ")
            population = int(population) if population.strip() else 1000
            feats = input("Features (comma separated, or leave blank for random): ").strip()
            if not feats:
                features = random.sample(CITY_FEATURES, k=random.randint(1, 3))
            else:
                features = [f.strip() for f in feats.split(",") if f.strip()]
            country.add_city(name, population, features)
        elif choice == "3":
            title = input("Law title: ")
            description = input("Description: ")
            print("Enter impact on cities (e.g., crime:-3,happiness:2): ")
            impact_raw = input("Impact: ")
            impact = {}
            for part in impact_raw.split(","):
                if ":" in part:
                    k, v = part.split(":")
                    impact[k.strip()] = int(v.strip())
            country.add_law(title, description, impact)
        elif choice == "4":
            description = input("Event description: ")
            print("Enter effect on resources (e.g., food:-100,money:200): ")
            effect_raw = input("Effect: ")
            effect = {}
            for part in effect_raw.split(","):
                if ":" in part:
                    k, v = part.split(":")
                    effect[k.strip()] = int(v.strip())
            country.add_event(description, effect)
        elif choice == "5":
            country.simulate_tick()
        elif choice == "6":
            filename = input("Save filename (default: nation_save.json): ").strip() or "nation_save.json"
            country.save(filename)
        elif choice == "7":
            filename = input("Load filename (default: nation_save.json): ").strip() or "nation_save.json"
            country.load(filename)
        elif choice == "8":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()