from ..core.state_models import State
from requests import  Session


def performance_generate_report(state: State):
    #print("\n\ni am in performance_node\n\n")
    #print("Access Token in State : ", state["access_token"])
    s = Session()
    #print("Resolved user id ",state["resolved_user_id"])
    #print("Resolved date ", state["date"])
    # #print("API in state : ",state["api_endpoint"])
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + state["access_token"],
        "Cookie": "BrowserId=GSlXreH9Ee-ZFAW_KW_xKQ; CookieConsentPolicy=0:1; LSKey-c$CookieConsentPolicy=0:1",
    }

    body = {
        "keyword": "Attendance",
        "conditionName": "UserAndDate_Filter",
        "parameters": [
            {"name": "CheckInDate", "value": str(state["date"])},
            {"name": "UserId", "value": state["resolved_user_id"]},
        ],
    }
    API = "https://appstrail-sfa-dev-ed.develop.my.salesforce.com/services/apexrest/APTLDataRequest"
    # response = s.post(state["api_endpoint"], json=body, headers=headers)
    response = s.post(API, json=body, headers=headers)
    performance_data = response.json().get("records", [])
    # #print(len(performance_data))
    # if response:
    #     #print("Response model in performance Node: ",response.json())
    # else:
    #     #print("No performance found")
    if len(performance_data) == 0:
        state["response"] = "No data found for the given date."
        state["map_cr"] = None
        return state
    
    records = performance_data[0]["parentRecord"]
    final_records = {}
    final_records["AD HOC Orders"] = records["No_of_Ad_hoc_Orders"]
    final_records["Unplanned Visits"] = records["No_of_Unplanned_Visits"]
    final_records["Total Order Value"] = records["Total_Order_Value"]
    final_records["Non Productive Call"] = records["Non_Productive_Call"]
    final_records["Productivity Call"] = records["Productivity_Call"]
    final_records["Scheduled Call"] = records["Scheduled_Call"]
    final_records["Total Visits"] = records["Total_Visits"]
    formatted_output = []
    for key, value in final_records.items():
        value = str(value) if value else "N/A"  # Handle empty values
        formatted_line = f"{key}:**{value}**<br>"
        formatted_output.append(formatted_line)

    if final_records:
        result = "\n".join(formatted_output)
        #print(result)
    else:
        result = "Currently the performance is empty"

    import folium

    coordinates = [
        (12.8995, 77.6144), 
        (12.9250, 77.6170),  
        (12.9166, 77.6101), 
        (12.9172, 77.6238)   
    ]

    if coordinates:
        center_lat = sum(lat for lat, _ in coordinates) / len(coordinates)
        center_lng = sum(lng for _, lng in coordinates) / len(coordinates)
    else:
        center_lat, center_lng = 0, 0

    m = folium.Map(location=[center_lat, center_lng], zoom_start=2)

    for lat, lng in coordinates:
        folium.Marker(
            location=[lat, lng],
            icon=folium.Icon(color='red', icon='cloud')
        ).add_to(m)

    if len(coordinates) > 1:
        sw = min(lat for lat, _ in coordinates), min(lng for _, lng in coordinates)
        ne = max(lat for lat, _ in coordinates), max(lng for _, lng in coordinates)
        m.fit_bounds([sw, ne])

    #Place this RIGHT BEFORE you generate map_html
    m.get_root().html.add_child(folium.Element("""
    <style>
    .leaflet-control-attribution {
        display: none;
    }
    </style>
    """))

    map_html = m._repr_html_()
    map_html = map_html.replace('<span style="color:#565656">Make this Notebook Trusted to load map: File -> Trust Notebook</span>', '')
  
    # print(map_html)



    state["response"] = result
    state["map_cr"]= map_html
    # state["map_cr"]= None

    return state