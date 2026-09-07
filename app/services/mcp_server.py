from fastmcp import FastMCP

mcp = FastMCP("LocationVerificationServer")

SUPPORTED_CITIES = {
    "springfield": ["main st", "evergreen terrace", "oak st", "maple ave", "elm st"],
    "riverside": ["river rd", "broadway", "1st ave", "central blvd", "park way"],
    "metro city": ["5th ave", "lexington ave", "wall st", "grand central", "sunset blvd"]
}

@mcp.tool()
def verify_location(city: str, street_address: str) -> str:
    if not city or not street_address:
        return "ERROR: Both city name and street address are required."
    city_clean = city.strip().lower()
    street_clean = street_address.strip().lower()

    if city_clean not in SUPPORTED_CITIES:
        supported = ", ".join([c.title() for c in SUPPORTED_CITIES.keys()])
        return f"INVALID_CITY: '{city}' is outside our area. Service only: {supported}."

    known = SUPPORTED_CITIES[city_clean]
    matches = [s for s in known if s in street_clean or street_clean in s]
    if not matches:
        if len(street_clean) < 3:
            return f"AMBIGUOUS_STREET: '{street_address}' seems incomplete. Ask for cross street."
        return f"INVALID_STREET: '{street_address}' is not recognized in {city.title()}. Ask for a supported street or landmark."

    return f"VALID_LOCATION: {street_address.title()}, {city.title()}."

if __name__ == "__main__":
    mcp.run(transport="sse", port=8001)