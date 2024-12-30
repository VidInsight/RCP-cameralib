from typing import Optional, List, Dict


def sdict(success: bool, data: Optional[Dict] = None, message: str = "") -> Dict:
    return {"success": success, "data": data or {}, "message": message}