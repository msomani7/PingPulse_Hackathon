import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key = OPENAI_API_KEY)

def fetch_jira_issues(selected_stream, fromDate = None, toDate = None):

    def append_jql(selected_stream, from_date=None, to_date=None):
        base_jql = 'type in (Epic)'
        
        streams = {
            "Identity Trust": 'and (issuetype = EPIC and (Project in (PID, PIM, PND, PIDPPQ, NEO) or project = P14C and team = 217c3afb-b962-4afb-8ca8-04769743a1cf-47) or labels in (PingOneMFA))',
            "P1AS": 'and Project in (PDO, PP)',
            "iOPS": 'and project in ("SRE Observability Engineering", "SRE Production Services", "SRE Service Management", "SRE Operational Platforms", DevTools, ORB)',
            "MT SaaS": 'and (filter in ("Arun Goel Org") or project in ("PAX Platform", "PingOne End User Experience", DV) or "Product[Select List (multiple choices)]" in ("PingOne Platform", "PingOne DaVinci"))',
            "Software": 'and project in (BRASS, IK, PA, PAPQ, PAA, PASDKC, PASDKJ, PDI, PF, PPQ, POP, OPENIG, OPENIDM, OPENICF, OPENDJ, AMAGENTS, OPENAM)',
            "AI / Analytics Data Platform": 'and project in (IGA, ANALYTICS, AI)',
            "AIC": 'and project in (FRAAS)',
            # "DEFAULT": 'and (issuetype = EPIC and (Project in (PID, PIM, PND, PIDPPQ, NEO) or project = P14C and team = 217c3afb-b962-4afb-8ca8-04769743a1cf-47) or labels in (PingOneMFA) or Project in (PDO, PP) or project in ("SRE Observability Engineering", "SRE Production Services", "SRE Service Management", "SRE Operational Platforms", DevTools, ORB) or filter in ("Arun Goel Org") or project in ("PAX Platform", "PingOne End User Experience", DV) or "Product[Select List (multiple choices)]" in ("PingOne Platform", "PingOne DaVinci") or project in (BRASS, IK, PA, PAPQ, PAA, PASDKC, PASDKJ, PDI, PF, PPQ, POP, OPENIG, OPENIDM, OPENICF, OPENDJ, AMAGENTS, OPENAM) or project in (IGA) or project in (FRAAS))'
        }
        
        if selected_stream in streams:
            jql = base_jql + ' ' + streams[selected_stream]
        # else:
        #     # all_conditions = ' '.join(streams.values())
        #     # jql = base_jql + ' ' + all_conditions
        #     jql  = base_jql + ' ' + streams["DEFAULT"]
        
        if from_date:
            date_condition1 = f' and resolutiondate >= "{from_date} 00:00"'
            jql += date_condition1

        if to_date:
            date_condition2 = f' and resolutiondate <= "{to_date} 23:59"'
            jql += date_condition2

        completed = False
        if completed:
            jql+= f' and ("On-Track[Dropdown]" = "Blue (Complete)" or "On-Track (migrated)" = "Blue (Complete)" or status in (Done, Resolved, Closed))'

        risk_delayed = False
        if risk_delayed:
            jql+= f'and ("On-Track[Dropdown]" = Yellow or "On-Track (migrated)" = "Yellow (At-Risk)" or "On-Track[Dropdown]" = Red or "On-Track (migrated)" = "Red (Delayed)")'
        
        jql += ' and ("Engineering Response" is not EMPTY or "Engineering Response" is EMPTY) order by cf[10078], "Engineering Response", On-Track desc, key'
        
        return jql

    # def fetch_jira_issue_data(jira_id):
    #     def extract_filed_data(fields, changelog):
    #         on_deck_date = None
    #         closed_date = None
    #         created_date = fields.get("created", "")
    #         resolved_date = fields.get("resolutiondate", "")
    #         days_from_created_to_resolved = None
    #         days_from_on_deck_to_committed = None

    #         for history in changelog['histories']:
    #             for item in history['items']:
    #                 if item['field'] == 'status':
    #                     if item['toString'] == 'In Progress':
    #                         on_deck_date = history['created']  # In progress to Resolved
    #                     if item['toString'] == 'Closed':
    #                         closed_date = history['created']

    #         if created_date and resolved_date:
    #             # Convert string dates to datetime objects
    #             created = datetime.strptime(created_date, "%Y-%m-%dT%H:%M:%S.%f%z")
    #             resolved = datetime.strptime(resolved_date, "%Y-%m-%dT%H:%M:%S.%f%z")

    #             # Calculate the difference in days
    #             days_from_created_to_resolved = (resolved - created).days

    #         if on_deck_date and closed_date:
    #             # Convert string dates to datetime objects
    #             on_deck = datetime.strptime(on_deck_date, "%Y-%m-%dT%H:%M:%S.%f%z")
    #             closed = datetime.strptime(closed_date, "%Y-%m-%dT%H:%M:%S.%f%z")

    #             # Calculate the difference in days
    #             days_from_on_deck_to_committed = (closed - on_deck).days

    #         issue_data = {
    #             "Created_Date": created_date,
    #             "Resolved_Date": resolved_date,
    #             "InProgress_Date": on_deck_date,
    #             "Closed_Date": closed_date,
    #             "Days from Created to Resolved": days_from_created_to_resolved,
    #             "Days from In Progress to Closed": days_from_on_deck_to_committed
    #         }

    #         return issue_data

    #     url = f"https://pingidentity.atlassian.net/rest/api/3/issue/{jira_id}?expand=changelog"
    #     payload = {}

    #     jira_token = "ATATT3xFfGF0ndxink9QUjPTdQruBLLfLdrqtf28sIc3xoG9EyN2Jg7xhQFPzDvzfZNYL82Qa2oWqfZQ4qKUGYVCdy4eAkHh1chHxzVCVX-yWYbJFP-bybz_pkEDBl7xfITGpb4lgcf4UhWjbxAhmS3nYzrVS9FEb-zb_BQTLiDxAIhroWSymsI=1BC0A3B3"
    #     auth = HTTPBasicAuth('msomani@pingidentity.com', jira_token)
    #     headers = {
    #         'Content-Type': 'application/json',
    #     }

    #     response = requests.request("GET", url, headers=headers, data=payload, auth=auth)
    #     result = response.json()
    #     fields = result.get("fields", {})
    #     changelog = result.get("changelog", {})

    #     return extract_filed_data(fields, changelog)
    
    def extract_issue_data(issues):
        extracted_data = []

        for issue in issues:
            fields = issue.get("fields", {})
            status = fields.get("status", {}).get("name", "")
            
            product_field = fields.get("customfield_10078")
            product = product_field[0].get("value", "") if product_field else None
            
            track_field = fields.get("customfield_11020")
            track = track_field[0].get("value", "") if track_field else None  

            customfield_10241 = fields.get("customfield_10241")
            customfield_11404 = fields.get("customfield_11404")
            customfield_11085 = fields.get("customfield_11085")
            on_track_status = (customfield_10241.get("value", "") if customfield_10241 else
                                customfield_11404.get("value", "") if customfield_11404 else
                                customfield_11085.get("value", "") if customfield_11085 else None)
            
            if (status == 'Done' or status == 'Closed' or status == 'Resolved') or on_track_status == 'Blue (Complete)':
                on_track_status = 'Blue (Complete)'

            customfield_10100 = fields.get("customfield_10100")
            customfield_11084 = fields.get("customfield_11084")

            engineering_response = (customfield_10100.get("value", "") if customfield_10100 else 
                                    customfield_11084.get("value", "") if customfield_11084 else None)

            customfield_11291 = fields.get("customfield_11291")
            revised_completed_date = customfield_11291.get("value") if customfield_11291 else None
            
            customfield_11025 = fields.get("customfield_11025")
            release_type = customfield_11025.get("value") if customfield_11025 else None

            issue_id = issue.get("key", "")

            issue_data = {
                "IssueId": issue_id,
                "Summary": fields.get("summary", ""),
                # "Status": fields.get("status", {}).get("name", ""),
                "Product": product,
                "Track": track,
                # "Planned_Completed_Date": fields.get("customfield_10112", ""),
                "On_Track_Comment": issue.get("renderedFields", {}).get("customfield_10262", ""),
                # "Aha_Release": fields.get("customfield_10256", ""),
                "OnTrack_Status": on_track_status,
                # "Engineering_Response": engineering_response,
                # "Revised_Completed_Date": revised_completed_date,
                "Release_Type": release_type
            }

            # Fetch additional data for the issue
            # additional_data = fetch_jira_issue_data(issue_id)
            # issue_data.update(additional_data)

            extracted_data.append(issue_data)

        return extracted_data
    
    def create_custom_issue_string_for_prompt(selected_stream, issues):
        issue_string = f"{selected_stream}:\n"
        issue_string += "\n"
        for issue in issues:
            issue_string += f"- IssueId: {issue['IssueId']}, "
            issue_string += f"  Summary: {issue['Summary']}, "
            # issue_string += f"  Status: {issue['Status']}, "
            issue_string += f"  Product: {issue['Product']}, "
            issue_string += f"  Track: {issue['Track']}, "
            # issue_string += f"  Planned_Completed_Date: {issue['Planned_Completed_Date']}, "
            issue_string += f"  On_Track_Comment: {issue['On_Track_Comment']}, "
            # issue_string += f"  Aha_Release: {issue['Aha_Release']}, "
            issue_string += f"  OnTrack_Status: {issue['OnTrack_Status']}, "
            # issue_string += f"  Engineering_Response: {issue['Engineering_Response']}, "
            # issue_string += f"  Revised_Completed_Date: {issue['Revised_Completed_Date']}, "
            issue_string += f"  Release_Type: {issue['Release_Type']}, "
            # issue_string += f"  Created_Date: {issue['Created_Date']}, "
            # issue_string += f"  Resolved_Date: {issue['Resolved_Date']}, "
            # issue_string += f"  InProgress_Date: {issue['InProgress_Date']}, "
            # issue_string += f"  Closed_Date: {issue['Closed_Date']}\n"
            # issue_string += f"  Days from Created to Resolved: {issue['Days from Created to Resolved']}, "
            # issue_string += f"  Days from In Progress to Closed: {issue['Days from In Progress to Closed']}, "
            issue_string  = issue_string[:-2]
            issue_string += "\n"
        issue_string += "\n"
        return issue_string
    
    def fetch_issues_with_pagination(jql, start_at=0, max_results=50):
        url = "https://pingidentity.atlassian.net/rest/api/3/search?_r=1734441761716"
        jira_token = "ATATT3xFfGF0ndxink9QUjPTdQruBLLfLdrqtf28sIc3xoG9EyN2Jg7xhQFPzDvzfZNYL82Qa2oWqfZQ4qKUGYVCdy4eAkHh1chHxzVCVX-yWYbJFP-bybz_pkEDBl7xfITGpb4lgcf4UhWjbxAhmS3nYzrVS9FEb-zb_BQTLiDxAIhroWSymsI=1BC0A3B3"
        auth = HTTPBasicAuth('msomani@pingidentity.com', jira_token)

        payload = json.dumps({
            "jql": jql,
            "validateQuery": "warn",
            "startAt": start_at,
            "maxResults": max_results,
            "fields": [
                "customfield_10078",
                "customfield_11020",
                "customfield_11025",
                "customfield_10112",
                "summary",
                "customfield_10262",
                "status",
                "customfield_10256",
                "customfield_10241",
                "customfield_10100",
                "customfield_11291",
                "customfield_11084",
                "customfield_11404",
                "customfield_11085"
            ],
            "expand": [
                "renderedFields"
            ]
        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=payload, auth=auth)
        result = response.json()
        return result.get("issues", []), result.get("total", 0)
    
    def generate_prompt(issue_string, selected_stream):
        prompt = f"""
    You are an Engineering Operations Analyst at Ping Identity company. Ping Identity helps you protect your users and every digital interaction they have while making experiences frictionless. You are responsible for categorizing and summarizing Jira issues for different product stream categories.

    ## Instructions:
    - Please categorize the following data by the "Product" field
    - For each product category, combine all the "Summary" values corresponding to that category and generate a cumulative summary as a dictionary value that is concise and provides an overview of all related issues, corresponding to that particular product category, and return a dictionary where each key is a product category. The value is a list and each key contains atmost two values, not more.
    - Ensure the summary reflects the essence of all related issues in an informative yet compact manner.
    - Don't include any text before output and after output

    - Ensure the following categories:
        - The categories to include are:
            - "Identity Trust", "P1AS", "iOPS", "MT SAAS", "Software", "AI/Analytics Data Platform", "AIC".
    - Return the output in the following format:
    {{
    "Identity Trust": ["Development for PingID Convergence 2024 is now complete, with an internal Ping and customer preview scheduled for November 15th.", "PingOne Neo has introduced an updated document capture library, providing a smoother experience when scanning expired IDs."],
    "P1AS": ["The Identity Cloud team strengthened infrastructure security with key enhancements, including Secure Boot, OS Login, enforced SSL, container hardening, and CloudSQL hardening to meet CIS Benchmark standards.", "PingOne Advanced Services adopted the Graviton ARM architecture and implemented a comprehensive patch deployment across all environments, achieving projected daily cost savings of approximately $3,900."],
    "iOPS": ["The PingOne Multi-Tenant deployment pipeline migration from Kasparov to ArgoCD was completed in October, encompassing over 350 services. Remaining Kasparov services will not be migrated and are scheduled for deprecation, with the tool set to be disabled in early  Q1 2025.", "Platform Security continues to consolidate legacy Forgerock and Ping toolsets, with all but one tool now integrated."],
    "MT SaaS": ["The PingOne Directory Scalability team made significant strides in scalability and performance, collaborating with SRE on horizontal scaling to manage a surge in users and prepare for future growth and the Black Friday event.", "Victoria’s Secret’s October flash sale on PingOne was a success, with DaVinci handling peaks of 450 requests per second."],
    "Software": ["SDK team and Sales teamed up on a partner webinar for AMER, EMEA, and APJ, showcasing our SDK offerings, attracting approximately 300 live attendees, and enhancing partner relationships.", "The development of Device Profiling for PingOne Protect is complete and scheduled for release in Ping Gateway 2024.11."],
    "AI/Analytics Data Platform": ["Helix, our strategic AI initiative, was unveiled at YOUniverse. The Helix MVP architecture and draft APIs have successfully completed reviews."],
    "AIC": ["The AIC Analytics and Reporting team released the first two milestones for IGA entities to Product Management and the field for internal feedback."]
    }}

    - Here is the issue_data to categorize:
    
    {issue_string}
    """
        if selected_stream != "All":
            # Modify the prompt to include only the selected product category
            prompt += f"\n\nOnly show data for: {selected_stream}"
        return prompt
    
    # Fetch summary for selected product category
    def fetch_summary(issue_string, selected_stream):
        prompt = generate_prompt(issue_string, selected_stream)
        messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
        ]

        completion = openai_client.chat.completions.create(
            messages=messages,
            model="gpt-4o-mini",  # Use the appropriate model
            temperature=0.3,
            stream=False,
        )
        
        generated_texts = [
        choice.message.content.strip() for choice in completion.choices
        ]

        return generated_texts[0]
        
    if selected_stream == "All":
        stream = ["Identity Trust", "P1AS", "iOPS", "MT SaaS", "Software", "AI / Analytics Data Platform", "AIC"]
        main_issue_string = ""
        for selected_stream in stream:
            jql = append_jql(selected_stream, fromDate, toDate)

            all_issues = []
            start_at = 0
            max_results = 50
            total_issues = 1  # Initialize with a non-zero value to enter the loop

            while start_at < total_issues:
                issues, total_issues = fetch_issues_with_pagination(jql, start_at, max_results)
                all_issues.extend(issues)
                start_at += max_results

            # print(len(all_issues))
            # Process and format all fetched issues
            issues_data = extract_issue_data(all_issues)

            # return issues_data
            issue_string = create_custom_issue_string_for_prompt(selected_stream, issues_data)

            main_issue_string += issue_string
        
        return fetch_summary(main_issue_string, "All")
    else:
        # Main logic to fetch all issues
        jql = append_jql(selected_stream, fromDate, toDate)

        all_issues = []
        start_at = 0
        max_results = 50
        total_issues = 1  # Initialize with a non-zero value to enter the loop

        while start_at < total_issues:
            issues, total_issues = fetch_issues_with_pagination(jql, start_at, max_results)
            all_issues.extend(issues)
            start_at += max_results

        # print(len(all_issues))
        # Process and format all fetched issues
        issues_data = extract_issue_data(all_issues)

        # return issues_data
        issue_string = create_custom_issue_string_for_prompt(selected_stream, issues_data)
        return fetch_summary(issue_string, selected_stream)
        # return issue_string

# Example usage
selected_stream = "All"
fromDate = "2024-11-01"
toDate = "2024-11-30"
print(fetch_jira_issues(selected_stream, fromDate, toDate))