"""Sample documents for testing the pipeline."""

SAMPLES = [
    {
        "text": """
        Apple Inc. announced record-breaking quarterly earnings today, with CEO Tim Cook 
        praising the team's innovation and dedication. The company's new iPhone lineup 
        exceeded expectations, driving significant growth in the consumer electronics sector. 
        Investors responded positively, with stock prices reaching an all-time high. 
        The Cupertino-based tech giant continues to dominate the market with its ecosystem 
        of products and services.
        """,
        "source": "tech_news",
        "expected_sentiment": "positive"
    },
    {
        "text": """
        The recent data breach at MegaCorp has left millions of customers vulnerable, 
        with personal information including names, addresses, and credit card details 
        potentially compromised. Security experts are calling this one of the worst 
        cybersecurity incidents in recent history. The company's CEO issued an apology, 
        but customers remain frustrated and concerned about identity theft. Regulatory 
        bodies in Washington D.C. have launched an investigation into the incident.
        """,
        "source": "security_news",
        "expected_sentiment": "negative"
    },
    {
        "text": """
        The weather forecast for New York City this weekend shows partly cloudy skies 
        with temperatures ranging from 65 to 72 degrees Fahrenheit. Meteorologists 
        predict a 30% chance of light rain on Sunday afternoon. Residents are advised 
        to carry an umbrella just in case. The National Weather Service has not issued 
        any severe weather warnings for the region.
        """,
        "source": "weather_report",
        "expected_sentiment": "neutral"
    },
    {
        "text": """
        Dr. Sarah Johnson from Stanford University published groundbreaking research 
        on renewable energy storage solutions. Her team developed a new battery technology 
        that could revolutionize electric vehicles and grid storage. The findings were 
        presented at the International Energy Conference in Berlin, Germany. Major 
        automotive companies including Tesla and Toyota have expressed interest in 
        licensing the technology. This breakthrough could accelerate the transition 
        to sustainable energy worldwide.
        """,
        "source": "science_journal",
        "expected_sentiment": "positive"
    },
    {
        "text": """
        Local community members gathered at Central Park yesterday to discuss the 
        proposed changes to zoning regulations. The meeting, organized by the 
        neighborhood association, saw diverse opinions from residents, business owners, 
        and city planners. Some attendees supported the development plans, citing 
        economic benefits, while others raised concerns about traffic and environmental 
        impact. The city council will vote on the proposal next month.
        """,
        "source": "local_news",
        "expected_sentiment": "neutral"
    }
]


def get_samples():
    """Return all sample documents."""
    return SAMPLES


def get_sample(index: int):
    """Get a specific sample by index."""
    if 0 <= index < len(SAMPLES):
        return SAMPLES[index]
    return None
