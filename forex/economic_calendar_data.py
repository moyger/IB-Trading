#!/usr/bin/env python3
"""
Economic Calendar Data Module
Provides high-impact economic events for trading strategy filtering
"""

from datetime import datetime, date

class EconomicCalendar:
    """
    Economic calendar for high-impact event filtering
    """
    
    def __init__(self):
        """Initialize economic calendar"""
        self.high_impact_events = self._get_2024_2025_events()
    
    def _get_2024_2025_events(self):
        """
        High-impact economic events for 2024-2025 period
        Focus on USD, EUR, GBP events that impact XAUUSD
        """
        events = [
            # 2024 Major Events
            # FOMC Meetings
            date(2024, 1, 31),  # FOMC Meeting
            date(2024, 3, 20),  # FOMC Meeting  
            date(2024, 5, 1),   # FOMC Meeting
            date(2024, 6, 12),  # FOMC Meeting
            date(2024, 7, 31),  # FOMC Meeting
            date(2024, 9, 18),  # FOMC Meeting
            date(2024, 11, 7),  # FOMC Meeting
            date(2024, 12, 18), # FOMC Meeting
            
            # NFP First Fridays
            date(2024, 1, 5),   # January NFP
            date(2024, 2, 2),   # February NFP
            date(2024, 3, 8),   # March NFP
            date(2024, 4, 5),   # April NFP
            date(2024, 5, 3),   # May NFP
            date(2024, 6, 7),   # June NFP
            date(2024, 7, 5),   # July NFP
            date(2024, 8, 2),   # August NFP
            date(2024, 9, 6),   # September NFP
            date(2024, 10, 4),  # October NFP
            date(2024, 11, 1),  # November NFP
            date(2024, 12, 6),  # December NFP
            
            # CPI Releases (Monthly)
            date(2024, 1, 11),  # December 2023 CPI
            date(2024, 2, 13),  # January 2024 CPI
            date(2024, 3, 12),  # February 2024 CPI
            date(2024, 4, 10),  # March 2024 CPI
            date(2024, 5, 15),  # April 2024 CPI
            date(2024, 6, 12),  # May 2024 CPI
            date(2024, 7, 11),  # June 2024 CPI
            date(2024, 8, 14),  # July 2024 CPI
            date(2024, 9, 11),  # August 2024 CPI
            date(2024, 10, 10), # September 2024 CPI
            date(2024, 11, 13), # October 2024 CPI
            date(2024, 12, 11), # November 2024 CPI
            
            # 2025 Major Events
            # FOMC Meetings
            date(2025, 1, 29),  # FOMC Meeting
            date(2025, 3, 19),  # FOMC Meeting
            date(2025, 4, 30),  # FOMC Meeting
            date(2025, 6, 11),  # FOMC Meeting
            date(2025, 7, 30),  # FOMC Meeting
            
            # NFP First Fridays 2025
            date(2025, 1, 3),   # January NFP
            date(2025, 2, 7),   # February NFP
            date(2025, 3, 7),   # March NFP
            date(2025, 4, 4),   # April NFP
            date(2025, 5, 2),   # May NFP
            date(2025, 6, 6),   # June NFP
            date(2025, 7, 4),   # July NFP
            
            # CPI Releases 2025
            date(2025, 1, 15),  # December 2024 CPI
            date(2025, 2, 12),  # January 2025 CPI
            date(2025, 3, 12),  # February 2025 CPI
            date(2025, 4, 9),   # March 2025 CPI
            date(2025, 5, 14),  # April 2025 CPI
            date(2025, 6, 11),  # May 2025 CPI
            date(2025, 7, 10),  # June 2025 CPI
            
            # Additional High-Impact Events
            # Jackson Hole Symposium
            date(2024, 8, 22),  # Jackson Hole 2024
            date(2024, 8, 23),  # Jackson Hole 2024
            date(2024, 8, 24),  # Jackson Hole 2024
            
            # Presidential Election 2024
            date(2024, 11, 5),  # US Presidential Election
            
            # GDP Releases (Quarterly)
            date(2024, 1, 25),  # Q4 2023 GDP
            date(2024, 4, 25),  # Q1 2024 GDP
            date(2024, 7, 25),  # Q2 2024 GDP
            date(2024, 10, 30), # Q3 2024 GDP
            date(2025, 1, 30),  # Q4 2024 GDP
            date(2025, 4, 24),  # Q1 2025 GDP
            date(2025, 7, 24),  # Q2 2025 GDP
            
            # ECB Meetings (Major ones affecting Gold)
            date(2024, 1, 25),  # ECB Meeting
            date(2024, 3, 7),   # ECB Meeting
            date(2024, 4, 11),  # ECB Meeting
            date(2024, 6, 6),   # ECB Meeting
            date(2024, 7, 18),  # ECB Meeting
            date(2024, 9, 12),  # ECB Meeting
            date(2024, 10, 17), # ECB Meeting
            date(2024, 12, 12), # ECB Meeting
            
            # Bank of England Meetings
            date(2024, 2, 1),   # BoE Meeting
            date(2024, 3, 21),  # BoE Meeting
            date(2024, 5, 9),   # BoE Meeting
            date(2024, 6, 20),  # BoE Meeting
            date(2024, 8, 1),   # BoE Meeting
            date(2024, 9, 19),  # BoE Meeting
            date(2024, 11, 7),  # BoE Meeting
            date(2024, 12, 19), # BoE Meeting
        ]
        
        return sorted(list(set(events)))
    
    def get_high_impact_dates(self):
        """Get list of high-impact dates"""
        return self.high_impact_events
    
    def is_high_impact_date(self, check_date):
        """Check if a given date is a high-impact event day"""
        if isinstance(check_date, datetime):
            check_date = check_date.date()
        
        return check_date in self.high_impact_events
    
    def get_events_in_range(self, start_date, end_date):
        """Get high-impact events within a date range"""
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        events_in_range = []
        for event_date in self.high_impact_events:
            if start_date <= event_date <= end_date:
                events_in_range.append(event_date)
        
        return events_in_range
    
    def get_next_event(self, from_date=None):
        """Get the next high-impact event from given date"""
        if from_date is None:
            from_date = date.today()
        
        if isinstance(from_date, datetime):
            from_date = from_date.date()
        
        for event_date in self.high_impact_events:
            if event_date > from_date:
                return event_date
        
        return None
    
    def get_events_for_month(self, year, month):
        """Get all high-impact events for a specific month"""
        events_in_month = []
        for event_date in self.high_impact_events:
            if event_date.year == year and event_date.month == month:
                events_in_month.append(event_date)
        
        return sorted(events_in_month)


if __name__ == "__main__":
    # Test the economic calendar
    calendar = EconomicCalendar()
    events = calendar.get_high_impact_dates()
    
    print("📅 ECONOMIC CALENDAR TEST")
    print("=" * 50)
    print(f"Total high-impact events loaded: {len(events)}")
    print(f"Date range: {events[0]} to {events[-1]}")
    
    # Show first 10 events
    print("\\nFirst 10 events:")
    for i, event in enumerate(events[:10]):
        print(f"  {i+1}. {event}")
    
    # Show events for January 2024
    jan_2024_events = calendar.get_events_for_month(2024, 1)
    print(f"\\nJanuary 2024 events: {len(jan_2024_events)}")
    for event in jan_2024_events:
        print(f"  • {event}")