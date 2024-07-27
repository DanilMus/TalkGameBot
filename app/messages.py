import json
import os

class Messages:
    def __init__(self, handler_path):
        self.messages = self._load(handler_path)

    def _load(self, handler_path: str) -> dict:
        base_path = "data/messages"
        
        # Строим относительный путь от base_path до hadler_path
        # (Допустим, handler_path = 'app/handlers/database_handlers/admin.py', то получить должны rel_path = database_handlers/admin.py)
        rel_path = os.path.relpath(handler_path,  "app/handlers")

        # Разделяем путь на компоненты
        path_parts = os.path.dirname(rel_path).split(os.sep)
        path_parts.append("")

        messages = {}

        # Проходим по компонентам и загружаем common.json
        # (В common.json хранятся базовые сообщения)
        current_path = base_path
        for part in path_parts:
            common_path = os.path.join(current_path, "common.json")
            if os.path.exists(common_path):
                common_messages = json.load(open(common_path, encoding= "utf-8"))
                messages.update(common_messages)
            current_path = os.path.join(current_path, part)
        
        # Загружаем целевой файл 
        filename = os.path.splitext(os.path.basename(handler_path))[0] + ".json"
        target_file_path = os.path.join(current_path, filename)

        if os.path.exists(target_file_path):
            target_messages = json.load(open(target_file_path, encoding= "utf-8"))
            messages.update(target_messages)

        return messages
    

if __name__ == "__main__":
    handler_path = 'app/handlers/database_handlers/admins.py'
    messages = Messages(handler_path)
    print(messages.messages)