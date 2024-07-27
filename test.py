from app.messages import Messages

handler_path = 'app/handlers/database_handlers/admin.py'
messages = Messages(handler_path)
print(messages.messages)