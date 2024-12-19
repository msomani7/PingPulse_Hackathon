import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime

def metric(selected_stream, fromDate = None, toDate = None):

    def calculate_epic_statistics(data, selected_stream):
        # Initialize counters and totals
        total_epics = len(data)
        completed = 0
        in_progress = 0
        at_risk = 0
        delayed = 0
        not_started = 0
        committed_or_stretch = 0
        total_days_created_to_resolved = 0
        total_days_in_progress_to_closed = 0

        for epic in data:
            # Track epic status
            if epic.get('OnTrack_Status') == 'Blue (Complete)':
                completed += 1
            if epic.get('OnTrack_Status') == 'In Progress':
                in_progress += 1
            if epic.get('OnTrack_Status') == 'At Risk':
                at_risk += 1
            if epic.get('OnTrack_Status') == 'Not Started':
                not_started += 1
            # Track commitment for % of delivery commitment
            if epic.get('Engineering_Response') == "Committed" or epic.get('Engineering_Response') == "Stretch":
                committed_or_stretch += 1
            # Track days for average calculations (handle None as 0)
            days_created_to_resolved = epic.get('Days from Created to Resolved', 0)
            total_days_created_to_resolved += days_created_to_resolved if days_created_to_resolved is not None else 0
            # For "Days from In Progress to Closed", check if it's None, and treat it as 0
            days_in_progress_to_closed = epic.get('Days from In Progress to Closed', 0)
            total_days_in_progress_to_closed += days_in_progress_to_closed if days_in_progress_to_closed is not None else 0

        # Calculate statistics
        percent_delivery_commitment = (committed_or_stretch / total_epics) * 100 if total_epics > 0 else 0
        avg_age_of_epic = total_days_created_to_resolved / total_epics if total_epics > 0 else 0
        avg_time_for_fixing_epic = total_days_in_progress_to_closed / total_epics if total_epics > 0 else 0

        # Format results to two decimal points
        percent_delivery_commitment = round(percent_delivery_commitment, 2)
        avg_age_of_epic = round(avg_age_of_epic, 2)
        avg_time_for_fixing_epic = round(avg_time_for_fixing_epic, 2)
        # Store results in the specified format
        results = {
            selected_stream: [
                total_epics,
                completed,
                in_progress,
                at_risk,
                delayed,
                not_started,
                percent_delivery_commitment,
                avg_age_of_epic,
                avg_time_for_fixing_epic
            ]
        }

        return results

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
            date_condition2 = f' and resolutiondate <= "{to_date} 00:00"'
            jql += date_condition2

        completed = False
        if completed:
            jql+= f' and ("On-Track[Dropdown]" = "Blue (Complete)" or "On-Track (migrated)" = "Blue (Complete)" or status in (Done, Resolved, Closed))'

        risk_delayed = False
        if risk_delayed:
            jql+= f'and ("On-Track[Dropdown]" = Yellow or "On-Track (migrated)" = "Yellow (At-Risk)" or "On-Track[Dropdown]" = Red or "On-Track (migrated)" = "Red (Delayed)")'
        
        jql += ' and ("Engineering Response" is not EMPTY or "Engineering Response" is EMPTY) order by cf[10078], "Engineering Response", On-Track desc, key'
        
        return jql

    def fetch_jira_issue_data(jira_id):
        def extract_filed_data(fields, changelog):
            on_deck_date = None
            closed_date = None
            created_date = fields.get("created", "")
            resolved_date = fields.get("resolutiondate", "")
            days_from_created_to_resolved = None
            days_from_on_deck_to_committed = None

            for history in changelog['histories']:
                for item in history['items']:
                    if item['field'] == 'status':
                        if item['toString'] == 'In Progress':
                            on_deck_date = history['created']  # In progress to Resolved
                        if item['toString'] == 'Closed':
                            closed_date = history['created']

            if created_date and resolved_date:
                # Convert string dates to datetime objects
                created = datetime.strptime(created_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                resolved = datetime.strptime(resolved_date, "%Y-%m-%dT%H:%M:%S.%f%z")

                # Calculate the difference in days
                days_from_created_to_resolved = (resolved - created).days

            if on_deck_date and closed_date:
                # Convert string dates to datetime objects
                on_deck = datetime.strptime(on_deck_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                closed = datetime.strptime(closed_date, "%Y-%m-%dT%H:%M:%S.%f%z")

                # Calculate the difference in days
                days_from_on_deck_to_committed = (closed - on_deck).days

            issue_data = {
                "Created_Date": created_date,
                "Resolved_Date": resolved_date,
                "InProgress_Date": on_deck_date,
                "Closed_Date": closed_date,
                "Days from Created to Resolved": days_from_created_to_resolved,
                "Days from In Progress to Closed": days_from_on_deck_to_committed
            }

            return issue_data

        url = f"https://pingidentity.atlassian.net/rest/api/3/issue/{jira_id}?expand=changelog"
        payload = {}

        jira_token = "ATATT3xFfGF0ndxink9QUjPTdQruBLLfLdrqtf28sIc3xoG9EyN2Jg7xhQFPzDvzfZNYL82Qa2oWqfZQ4qKUGYVCdy4eAkHh1chHxzVCVX-yWYbJFP-bybz_pkEDBl7xfITGpb4lgcf4UhWjbxAhmS3nYzrVS9FEb-zb_BQTLiDxAIhroWSymsI=1BC0A3B3"
        auth = HTTPBasicAuth('msomani@pingidentity.com', jira_token)
        headers = {
            'Content-Type': 'application/json',
        }

        response = requests.request("GET", url, headers=headers, data=payload, auth=auth)
        result = response.json()
        fields = result.get("fields", {})
        changelog = result.get("changelog", {})

        return extract_filed_data(fields, changelog)
    
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
                "Status": fields.get("status", {}).get("name", ""),
                "Product": product,
                "Track": track,
                "Planned_Completed_Date": fields.get("customfield_10112", ""),
                "On_Track_Comment": issue.get("renderedFields", {}).get("customfield_10262", ""),
                "Aha_Release": fields.get("customfield_10256", ""),
                "OnTrack_Status": on_track_status,
                "Engineering_Response": engineering_response,
                "Revised_Completed_Date": revised_completed_date,
                "Release_Type": release_type
            }

            # Fetch additional data for the issue
            additional_data = fetch_jira_issue_data(issue_id)
            issue_data.update(additional_data)

            extracted_data.append(issue_data)

        return extracted_data
    
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
    
    if selected_stream == "All":
        stream = ["Identity Trust", "P1AS", "iOPS", "MT SaaS", "Software", "AI / Analytics Data Platform", "AIC"]
        metrics = {}

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

            # Process and format all fetched issues
            issues_data = extract_issue_data(all_issues)

            if issues_data:
                metrics[selected_stream] = metrics[selected_stream] = list(calculate_epic_statistics(issues_data, selected_stream).values())[0]
            else:
                metrics[selected_stream] = []

        return json.dumps(metrics)
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
        metrics = {}
        if issues_data:
            metrics = calculate_epic_statistics(issues_data, selected_stream)
        return json.dumps(metrics)
        # return issues_data
        # issue_string = create_custom_issue_string_for_prompt(selected_stream, issues_data)
        # return issue_string

# Example usage
selected_stream = "Identity Trust"
fromDate = "2024-11-01"
toDate = "2024-11-30"
data = metric(selected_stream, fromDate, toDate)
print(data)