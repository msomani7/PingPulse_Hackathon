import pandas as pd
from collections import defaultdict
import json

def get_holiday_list(from_date, to_date):
    def sort_holidays_by_month(from_date, to_date):
        # Read the Excel file
        df = pd.read_excel("PingHolidayList.xlsx")

        # Ensure proper column names
        df.columns = ['Country', 'Holiday', 'Date']

        # Forward-fill empty country cells with the previous country
        df['Country'] = df['Country'].ffill()

        # Convert the 'Date' column to datetime (accounting for the specific format)
        df['Date'] = pd.to_datetime(df['Date'], format='%A, %B %d', errors='coerce')

        # Drop rows where 'Date' could not be parsed
        df = df.dropna(subset=['Date'])

        # Parse the from_date and to_date as full dates
        from_date = pd.to_datetime(from_date, format='%Y-%m-%d')
        to_date = pd.to_datetime(to_date, format='%Y-%m-%d')
        
        # Extract month and day for comparison
        df['Month-Day'] = df['Date'].dt.strftime('%m-%d')
        df['Month-Day'] = pd.to_datetime(df['Month-Day'], format='%m-%d')
        
        from_month_day = from_date.strftime('%m-%d')
        to_month_day = to_date.strftime('%m-%d')
        
        from_month_day = pd.to_datetime(from_month_day, format='%m-%d')
        to_month_day = pd.to_datetime(to_month_day, format='%m-%d')
        
        if from_month_day > to_month_day:  # Handle year wraparound (e.g., Oct 01 to Feb 15)
            df = df[(df['Month-Day'] >= from_month_day) | (df['Month-Day'] <= to_month_day)]
        else:
            df = df[(df['Month-Day'] >= from_month_day) & (df['Month-Day'] <= to_month_day)]

        # Extract the month for sorting
        df['Month'] = df['Date'].dt.month

        # Sort by month and then by date
        sorted_df = df.sort_values(by=['Month', 'Month-Day'])

        # Group holidays by date and consolidate countries for the same holiday
        holidays_by_month = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for _, row in sorted_df.iterrows():
            month_name = row['Date'].strftime('%B')
            date_str = row['Date'].strftime('%B %d')
            holidays_by_month[month_name][date_str][row['Holiday']].append(row['Country'])

        # Format the output for each month
        formatted_holidays = {"HOLIDAYS": []}
        for month, dates in holidays_by_month.items():
            for date, holidays in dates.items():
                holiday_entries = []
                for holiday_name, countries in holidays.items():
                    country_list = ', '.join(sorted(set(countries)))
                    holiday_entries.append(f"{holiday_name} ({country_list})")
                formatted_holidays["HOLIDAYS"].append(f"{date} | {', '.join(holiday_entries)}")

        if not formatted_holidays["HOLIDAYS"]:
            return []

        return formatted_holidays["HOLIDAYS"]

    # Generate and print the sorted holiday list
    try:
        sorted_holidays = sort_holidays_by_month(from_date, to_date)
        return json.dumps(sorted_holidays)
    except Exception as e:
        return f"Error processing the file: {e}"
    

fromDate = "2024-11-01"
toDate = "2024-11-05"

print(get_holiday_list(fromDate, toDate))