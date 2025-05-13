# Dynamic Values

PromptMigrate supports dynamic value placeholders that are processed at runtime when accessing prompts. This allows for creating more flexible and context-aware prompts without hardcoding values.

## Using Dynamic Values

Dynamic values use the following format in your prompts:

```
{{type:options}}
```

Where:
- `type`: The type of dynamic content (date, number, choice, text)
- `options`: Configuration specific to each type

## Available Placeholder Types

### Date Placeholders

Date placeholders insert the current date/time formatted according to your specifications.

**Format:**
```
{{date:format=FORMAT_STRING}}
```

The format string follows Python's [strftime format codes](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes).

**Examples:**

```python
# In your migration function
prompts["DATE_EXAMPLE"] = "Today is {{date:format=%B %d, %Y}}."
prompts["TIME_EXAMPLE"] = "The current time is {{date:format=%H:%M}}."
prompts["FULL_TIMESTAMP"] = "Timestamp: {{date:format=%Y-%m-%d %H:%M:%S}}"
```

These would resolve to something like:

```
"Today is May 13, 2025."
"The current time is 14:30."
"Timestamp: 2025-05-13 14:30:45"
```

### Number Placeholders

Number placeholders generate random integers within a specified range.

**Format:**
```
{{number:min=MIN,max=MAX}}
```

**Examples:**

```python
# In your migration function
prompts["DICE_ROLL"] = "You rolled a {{number:min=1,max=6}}!"
prompts["PERCENTAGE"] = "The system is {{number:min=0,max=100}}% complete."
prompts["YEAR_FUTURE"] = "In the year {{number:min=2030,max=2050}}..."
```

Each time these prompts are accessed, a new random number will be generated:

```
"You rolled a 4!"
"The system is 67% complete."
"In the year 2042..."
```

### Choice Placeholders

Choice placeholders randomly select one option from a list of comma-separated values.

**Format:**
```
{{choice:option1,option2,option3,...}}
```

**Examples:**

```python
# In your migration function
prompts["GREETING"] = "{{choice:Hello,Hi,Hey,Greetings}}! How can I help?"
prompts["MOOD"] = "I'm feeling {{choice:happy,excited,thoughtful,curious}} today."
prompts["SUGGESTION"] = "Have you tried {{choice:yoga,meditation,journaling,walking}}?"
```

Each access will randomly select one option:

```
"Hello! How can I help?"
"I'm feeling thoughtful today."
"Have you tried walking?"
```

### Text Placeholders

Text placeholders use Python's string formatting to insert variables into text templates.

**Format:**
```
{{text:template_string,var1=value1,var2=value2,...}}
```

**Examples:**

```python
# In your migration function
prompts["WELCOME"] = "{{text:Welcome to {service}, {name}!,service=ChatBot,name=user}}"
prompts["INTRO"] = "{{text:I am a {type} assistant created by {company}.,type=friendly,company=YourCompany}}"
prompts["COMPLEX"] = "{{text:The {color} {animal} jumped over the {object}.,color=brown,animal=fox,object=fence}}"
```

These would resolve to:

```
"Welcome to ChatBot, user!"
"I am a friendly assistant created by YourCompany."
"The brown fox jumped over the fence."
```

## Advanced Usage

### Combining Dynamic Values

You can use multiple dynamic values in a single prompt:

```python
prompt = "Today ({{date:format=%Y-%m-%d}}) your lucky number is {{number:min=1,max=100}}. Try {{choice:running,swimming,biking}} today!"
```

### Using Dynamic Values in Real-World Applications

This feature is particularly useful for:

1. **Time-sensitive prompts**: Incorporating current dates or time references
2. **Randomized responses**: Creating variety in system responses
3. **Customizable templates**: Creating reusable prompt templates with variables

## Example: Weather App with Dynamic Values

```python
@prompt_revision("003_weather_dynamic", "Add dynamic weather prompts")
def add_weather_prompts(prompts):
    # Date-aware weather question
    prompts["WEATHER_QUESTION"] = "What's the weather like on {{date:format=%A, %B %d}}?"
    
    # Randomized weather follow-up
    prompts["WEATHER_FOLLOWUP"] = "{{choice:Would you like a detailed forecast?,Should I show the weekly outlook?,Do you want to know about precipitation chances?}}"
    
    # Location-aware greeting template
    prompts["LOCATION_GREETING"] = "{{text:Welcome to the weather service for {location}!,location=your area}}"
    
    return prompts
```

Using these prompts in your application:

```python
from promptmigrate import promptmanager as pm

# Each time these are accessed, dynamic values are processed
weather_q = pm.WEATHER_QUESTION      # "What's the weather like on Wednesday, May 13?"
followup = pm.WEATHER_FOLLOWUP       # Random followup question
greeting = pm.LOCATION_GREETING      # "Welcome to the weather service for your area!"

# You can override template variables at runtime
custom_location = pm.LOCATION_GREETING.replace("your area", "New York")
```