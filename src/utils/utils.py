from typing import Optional, Dict

def sdict(success: bool, data: Optional[Dict] = None, message: str = "") -> Dict:
    return {"success": success, "data": data or {}, "message": message}