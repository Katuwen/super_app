import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class NoteManager:
    def __init__(self, data_file: str = "notes_data.json"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(base_dir, "..", "..", "data", data_file)
        self.data = self._load_data()

    def _load_data(self) -> dict:
        default_data: dict = {"notes": [], "tags": []}
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    loaded.setdefault("notes", [])
                    loaded.setdefault("tags", [])
                    return loaded
            except Exception:
                return default_data
        return default_data

    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def add_note(self, title: str, content: str, tags: Optional[List[str]] = None) -> int:
        note_id = max((n["id"] for n in self.data["notes"]), default=0) + 1
        note = {
            "id": note_id,
            "title": title,
            "content": content,
            "tags": tags or [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.data["notes"].insert(0, note)
        for tag in (tags or []):
            if tag not in self.data["tags"]:
                self.data["tags"].append(tag)
        self.save_data()
        return note_id

    def edit_note(self, note_id: int, title: str, content: str, tags: Optional[List[str]] = None):
        for note in self.data["notes"]:
            if note["id"] == note_id:
                note["title"] = title
                note["content"] = content
                note["tags"] = tags or []
                note["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                for tag in (tags or []):
                    if tag not in self.data["tags"]:
                        self.data["tags"].append(tag)
                self.save_data()
                return
        raise ValueError("Заметка не найдена")

    def delete_note(self, note_id: int):
        self.data["notes"] = [n for n in self.data["notes"] if n["id"] != note_id]
        self.save_data()

    def get_all_notes(self) -> List[Dict]:
        return self.data["notes"]

    def get_note_by_id(self, note_id: int) -> Optional[Dict]:
        for note in self.data["notes"]:
            if note["id"] == note_id:
                return note
        return None

    def search_notes(self, query: str) -> List[Dict]:
        q = query.lower()
        return [
            n for n in self.data["notes"]
            if q in n["title"].lower() or q in n["content"].lower()
            or any(q in tag.lower() for tag in n.get("tags", []))
        ]

    def filter_by_tag(self, tag: str) -> List[Dict]:
        return [n for n in self.data["notes"] if tag in n.get("tags", [])]

    def get_all_tags(self) -> List[str]:
        return self.data["tags"]

    def get_notes_count(self) -> int:
        return len(self.data["notes"])

    def export_notes(self, filename: str):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def import_notes(self, filename: str):
        if not os.path.exists(filename):
            raise FileNotFoundError("Файл импорта не найден")
        with open(filename, 'r', encoding='utf-8') as f:
            imported = json.load(f)
        existing_ids = {n["id"] for n in self.data["notes"]}
        for note in imported.get("notes", []):
            if note["id"] not in existing_ids:
                self.data["notes"].append(note)
        for tag in imported.get("tags", []):
            if tag not in self.data["tags"]:
                self.data["tags"].append(tag)
        self.save_data()
