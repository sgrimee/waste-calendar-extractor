# PRD-01: Event Alarms for Waste Collection Calendar

## 1. Overview

Add alarm functionality to waste collection events in the generated iCal files. Alarms will remind users the day before collection at 20:30 for specific waste types that require regular collection.

## 2. Background

Currently, the waste collection calendar generates iCal files with full-day events for each waste type collection. Users have requested reminder functionality to help them prepare for collection days. However, not all waste types should have alarms - some are occasional or on-demand only.

## 3. Requirements

### 3.1 Functional Requirements

1. **Alarm Configuration**: Add a mapping in the waste types module to specify which waste types should have alarms
2. **Alarm Timing**: Alarms should trigger the day before collection at 20:30 local time
3. **Alarm Type**: Use DisplayAlarm with appropriate reminder text
4. **Language Support**: Alarm messages should be localized to match the calendar language
5. **Selective Application**: Only apply alarms to waste types marked as requiring regular collection

### 3.2 Technical Requirements

1. **Library Compatibility**: Use the existing `ics` library's alarm functionality
2. **Code Integration**: Integrate seamlessly with existing iCal generation in `ical_generator.py`
3. **Configuration**: Extend `waste_types.py` with alarm configuration
4. **Testing**: Add unit tests for alarm functionality

## 4. Design

### 4.1 Waste Type Configuration

Add a new method to the `WasteType` enum in `waste_types.py`:

```python
def has_alarm(self) -> bool:
    """Return True if this waste type should have reminder alarms."""
    # Regular collection types that need alarms
    regular_collection_types = {
        WasteType.RESIDUAL,
        WasteType.ORGANIC, 
        WasteType.PAPER,
        WasteType.PACKAGING,
        WasteType.GLASS
    }
    return self in regular_collection_types
```

### 4.2 Alarm Message Generation

Add a new method to generate localized alarm messages:

```python
def alarm_message(self, language: Languages) -> str:
    """Get alarm reminder message in specified language."""
    # Implementation with localized reminder text
```

### 4.3 iCal Generation Enhancement

Modify `generate_ical_file()` in `ical_generator.py` to:

1. Check if waste type requires alarm using `waste_type.has_alarm()`
2. Create `DisplayAlarm` with trigger set to 1 day before at 20:30
3. Add alarm to the event using `event.alarms.add(alarm)`

### 4.4 Alarm Implementation Details

- **Trigger**: `timedelta(days=-1, hours=20, minutes=30)` relative to event start
- **Action**: `DisplayAlarm` with localized message
- **Message Format**: "Reminder: {waste_type_description} collection tomorrow"

## 5. Implementation Plan

### 5.1 Phase 1: Core Implementation
1. Add `has_alarm()` method to `WasteType` enum
2. Add `alarm_message()` method to `WasteType` enum  
3. Modify `generate_ical_file()` to add alarms conditionally
4. Import required alarm classes from `ics.alarm`

### 5.2 Phase 2: Testing
1. Add unit tests for `has_alarm()` method
2. Add unit tests for `alarm_message()` method
3. Add integration tests for alarm generation in iCal files
4. Test alarm functionality with different calendar applications

### 5.3 Phase 3: Documentation
1. Update CLAUDE.md with alarm implementation details
2. Add examples of alarm usage to documentation

## 6. Technical Considerations

### 6.1 Library Dependencies
- The `ics` library (already in use) supports `DisplayAlarm`, `AudioAlarm`, and `EmailAlarm`
- `DisplayAlarm` is most appropriate for calendar reminders
- Trigger can be set as `timedelta` for relative timing

### 6.2 Time Zone Handling
- Events are all-day events, so alarm timing needs careful consideration
- Use relative timing (timedelta) rather than absolute timing
- 20:30 timing assumes local time zone of the user

### 6.3 Calendar Client Compatibility
- Most modern calendar applications support VALARM components
- DisplayAlarm is widely supported across calendar clients
- Test with major calendar applications (Google Calendar, Apple Calendar, Outlook)

## 7. Success Criteria

1. **Functionality**: Alarms are generated only for specified waste types
2. **Timing**: Alarms trigger at 20:30 the day before collection
3. **Localization**: Alarm messages appear in the correct language
4. **Integration**: No breaking changes to existing calendar generation
5. **Testing**: All tests pass including new alarm-specific tests

## 8. Future Enhancements

1. **Configurable Timing**: Allow users to customize alarm timing
2. **Multiple Alarms**: Support multiple reminder times per event
3. **Audio Alarms**: Option for audio alerts in addition to display
4. **Email Alarms**: Email reminders for users who prefer them

## 9. Risk Assessment

### 9.1 Low Risk
- Library support for alarms is well-established
- Implementation is additive, not modifying existing functionality
- Clear separation between alarm and non-alarm waste types

### 9.2 Mitigation Strategies
- Thorough testing with multiple calendar applications
- Fallback behavior if alarm creation fails
- Clear documentation for troubleshooting alarm issues

## 10. Acceptance Criteria

- [ ] Regular collection waste types (residual, organic, paper, packaging, glass) have alarms
- [ ] Occasional waste types (electric, hedge, problematic, bulky, clothes, christmas trees) do not have alarms
- [ ] Alarms trigger at 20:30 the day before collection
- [ ] Alarm messages are localized to calendar language
- [ ] Generated iCal files are valid and compatible with major calendar applications
- [ ] All existing functionality remains unchanged
- [ ] Unit and integration tests pass