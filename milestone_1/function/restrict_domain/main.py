def lambda_handler(event, context):
    # Deny sign-in for a not HID/ASSAABLOY email domain
    user_email = event["request"]["userAttributes"].get("email", "")
    if not user_email.endswith(("@hidglobal.com", "@assaabloy.com")):
        raise Exception("AccessDenied: Email domain is not allowed")

    return event
