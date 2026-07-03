import win32evtlog


def get_system_events(limit=10):
    server = "localhost"
    log_type = "System"

    hand = win32evtlog.OpenEventLog(server, log_type)

    flags = (
        win32evtlog.EVENTLOG_BACKWARDS_READ |
        win32evtlog.EVENTLOG_SEQUENTIAL_READ
    )

    events = []

    while len(events) < limit:
        records = win32evtlog.ReadEventLog(hand,flags, 0)
        if not records: 
            break
        for event in records:

            events.append({
                "Event ID": event.EventID & 0xFFFF,
                "Source": event.SourceName,
                "Time": event.TimeGenerated.Format(),
                "Category": event.EventCategory
            })

            if len(events) >= limit:
                break

    win32evtlog.CloseEventLog(hand)
    
    return events
    
def print_event_logs(limit=10):
    
    events = get_system_events(limit)   # ← Call the function to get data
    
    if not events:
        print("No events found or error occurred.")
        return

    print(f"\n=== Last {len(events)} System Events ===\n")

    for i, event in enumerate(events, 1):
        print(f"Event #{i}")
        print("=" * 50)
        
        for key, value in event.items():
            print(f"{key:12}: {value}")
        
        print()  # Empty line between events

